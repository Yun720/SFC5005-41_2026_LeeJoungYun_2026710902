"""
dashboard.py
AAS 기반 가상 SMT 라인 Streamlit 모니터링 대시보드

실행: python -m streamlit run dashboard.py
"""

import time
from datetime import datetime

import pandas as pd
import streamlit as st

from src.emulator import SMTLineEmulator
from src.production_simulator import SMT_LINE_SEQUENCE, PROCESS_NAME_MAP
from src.traceability import get_snapshots_by_barcode

# ── 페이지 설정 ────────────────────────────────────────
st.set_page_config(
    page_title="AAS SMT 라인 모니터링",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 설비별 아이콘 및 표시 주요 필드 ───────────────────
_EQ_ICONS = {
    "ScreenPrinter_01": "🖨️",
    "SPI_01":           "🔬",
    "Mounter_01":       "🤖",
    "Reflow_01":        "🌡️",
    "AOI_01":           "📷",
    "ICT_01":           "⚡",
}

# (필드명, 단위) — 카드에 표시할 핵심 3개
_EQ_KEY_FIELDS: dict[str, list[tuple[str, str]]] = {
    "ScreenPrinter_01": [("Temp", "°C"), ("SqueegeePressure", "MPa"), ("CycleTime", "s")],
    "SPI_01":           [("InspectionResult", ""), ("SolderVolume", "%"), ("SolderHeight", "mm")],
    "Mounter_01":       [("PlacementSpeed", "cph"), ("WorkingRatio", "%"), ("PickupError", "건")],
    "Reflow_01":        [("Zone1Temperature", "°C"), ("Zone2Temperature", "°C"), ("Zone3Temperature", "°C")],
    "AOI_01":           [("InspectionResult", ""), ("DefectType", ""), ("DefectLocation", "")],
    "ICT_01":           [("InspectionResult", ""), ("ActualValue", ""), ("StandardValue", "")],
}

# ── 세션 상태 초기화 ───────────────────────────────────
if "emu" not in st.session_state:
    st.session_state.emu = SMTLineEmulator(fail_rate=0.25)
if "tick_count" not in st.session_state:
    st.session_state.tick_count = 0
if "event_log" not in st.session_state:
    st.session_state.event_log: list[str] = []

emu: SMTLineEmulator = st.session_state.emu


# ── 헬퍼 ──────────────────────────────────────────────
def _safe_df(data: dict) -> pd.DataFrame:
    rows = [(k, str(v) if v is not None else "") for k, v in data.items()]
    return pd.DataFrame(rows, columns=["필드", "값"])


def _hl_insp(row: pd.Series) -> list[str]:
    if row["필드"] == "InspectionResult":
        color = "#FFCCCC" if row["값"] == "FAIL" else "#CCFFCC"
        return [f"background-color:{color}"] * 2
    return [""] * 2


def _append_events(events: list[tuple]) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"ENTER": "⬇", "MOVE": "→", "COMPLETE": "✓", "BLOCK": "■"}
    for ev_type, barcode, stage in events:
        icon = icons.get(ev_type, "·")
        st.session_state.event_log.insert(
            0, f"[{ts}] {icon} {ev_type:<9} {barcode}  →  {stage}"
        )
    st.session_state.event_log = st.session_state.event_log[:60]


def _do_tick() -> None:
    events = emu.tick()
    st.session_state.tick_count += 1
    _append_events(events)


# ══════════════════════════════════════════════════════
#  SMT 라인 비주얼 다이어그램 HTML 생성
# ══════════════════════════════════════════════════════
_CSS = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; }

.flow-wrapper {
  background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
  border-radius: 16px;
  padding: 18px 20px 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.flow-title {
  text-align: center;
  color: #94a3b8;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 14px;
}

/* ─── 라인 전체 ─── */
.flow-line {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 0;
  overflow-x: auto;
  padding-bottom: 4px;
}

/* ─── 장비 카드 ─── */
.eq-card {
  width: 148px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #334155;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.eq-card.idle   { border-color: #334155; box-shadow: 0 2px 8px rgba(0,0,0,.4); }
.eq-card.active { border-color: #3b82f6; box-shadow: 0 0 18px rgba(59,130,246,.35); }
.eq-card.fail   { border-color: #ef4444; box-shadow: 0 0 22px rgba(239,68,68,.5);
                  animation: pulse-red 1.2s ease-in-out infinite; }

@keyframes pulse-red {
  0%,100% { box-shadow: 0 0 22px rgba(239,68,68,.5); }
  50%      { box-shadow: 0 0 38px rgba(239,68,68,.85); }
}

/* 카드 헤더 */
.eq-hdr {
  padding: 9px 10px 7px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.eq-hdr.idle   { background: #1e293b; }
.eq-hdr.active { background: #1d4ed8; }
.eq-hdr.fail   { background: #b91c1c; }

.eq-icon { font-size: 20px; line-height: 1; flex-shrink: 0; }

.eq-label { flex: 1; min-width: 0; }
.eq-name  { color: #f1f5f9; font-size: 10.5px; font-weight: 700;
             white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.eq-id    { color: rgba(255,255,255,.5); font-size: 8.5px; }

.eq-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.eq-dot.idle   { background: #475569; }
.eq-dot.active { background: #34d399; animation: blink 1.5s infinite; }
.eq-dot.fail   { background: #fca5a5; animation: blink .6s infinite; }

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

/* 카드 바디 */
.eq-body {
  background: #0f172a;
  padding: 8px 9px;
  min-height: 108px;
}

.pcb-tag {
  display: block; text-align: center;
  background: #1e40af; color: #bfdbfe;
  border-radius: 4px; padding: 3px 6px;
  font-size: 10.5px; font-weight: 700;
  font-family: 'Courier New', monospace;
  letter-spacing: .04em; margin-bottom: 7px;
}
.pcb-tag.fail { background: #7f1d1d; color: #fca5a5; }

.pcb-empty {
  display: block; text-align: center;
  background: #1e293b; color: #475569;
  border-radius: 4px; padding: 3px 6px;
  font-size: 9.5px; margin-bottom: 7px;
}

.metric-row {
  display: flex; justify-content: space-between;
  margin-bottom: 3.5px; font-size: 9.5px;
  line-height: 1.2;
}
.mk { color: #64748b; overflow: hidden; text-overflow: ellipsis;
      white-space: nowrap; max-width: 55%; }
.mv { color: #cbd5e1; font-family: 'Courier New', monospace; font-size: 9px; }
.mv.pass { color: #34d399; font-weight: 700; }
.mv.fail { color: #f87171; font-weight: 700; }
.mv.warn { color: #fbbf24; }

/* 카드 푸터 */
.eq-ftr {
  padding: 4px; text-align: center;
  font-size: 9.5px; font-weight: 700; letter-spacing: .06em;
}
.eq-ftr.idle   { background: #1e293b; color: #475569; }
.eq-ftr.active { background: #1e3a8a; color: #93c5fd; }
.eq-ftr.fail   { background: #7f1d1d; color: #fca5a5; }

/* ─── 화살표 ─── */
.arrow-zone {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  width: 36px; flex-shrink: 0; padding: 0 2px;
}
.arrow-shaft {
  display: flex; align-items: center;
}
.arrow-line { width: 22px; height: 2px; background: #3b82f6; }
.arrow-tip  {
  width: 0; height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 8px solid #3b82f6;
}
.pcb-dot {
  width: 10px; height: 5px;
  background: #f59e0b; border-radius: 1px;
  margin-top: 4px;
  animation: slide 1.1s ease-in-out infinite;
}
@keyframes slide {
  0%   { opacity:0; transform:translateX(-9px); }
  40%  { opacity:1; }
  100% { opacity:0; transform:translateX(9px); }
}

/* ─── 컨베이어 벨트 ─── */
.conveyor {
  height: 5px;
  margin-top: 12px;
  background: repeating-linear-gradient(
    90deg, #1e293b 0px,#1e293b 18px,
    #334155 18px,#334155 36px
  );
  border-radius: 3px;
  background-size: 36px 100%;
  animation: belt .7s linear infinite;
}
@keyframes belt {
  from { background-position: 0 0; }
  to   { background-position: 36px 0; }
}

/* ─── 범례 & 통계 ─── */
.bottom-bar {
  display: flex; justify-content: space-between;
  align-items: center; margin-top: 10px;
  flex-wrap: wrap; gap: 6px;
}
.legend { display: flex; gap: 12px; align-items: center; }
.leg-item { display: flex; align-items: center; gap: 4px;
             font-size: 9.5px; color: #64748b; }
.leg-dot { width: 7px; height: 7px; border-radius: 50%; }

.stats { display: flex; gap: 14px; }
.stat  { font-size: 10px; color: #64748b; }
.stat b { font-size: 11px; }
</style>
"""


def _render_flow_diagram(emu: SMTLineEmulator) -> str:
    """설비 파이프라인 시각화 HTML 생성"""
    parts: list[str] = []

    for i, eq_id in enumerate(SMT_LINE_SEQUENCE):
        inst = emu.instances[eq_id]
        pcb  = emu.pipeline[i]
        insp = inst.quality_result.get("InspectionResult")

        # ── 상태 클래스
        if pcb is None:
            cls, footer = "idle", "대  기"
        elif insp == "FAIL":
            cls, footer = "fail", "❌  FAIL"
        else:
            cls, footer = "active", "▶  처리 중"

        # ── PCB 태그
        if pcb:
            ft = "fail" if insp == "FAIL" else ""
            pcb_html = f'<span class="pcb-tag {ft}">{pcb.pcb_barcode}</span>'
        else:
            pcb_html = '<span class="pcb-empty">— 비어있음 —</span>'

        # ── 핵심 메트릭 (최대 3행)
        all_data = {**inst.operation_data, **inst.quality_result}
        metrics = ""
        for field, unit in _EQ_KEY_FIELDS.get(eq_id, []):
            val = all_data.get(field)
            if val is None:
                disp = "—"
                vc = ""
            else:
                disp = f"{val}{unit}" if unit else str(val)
                if field == "InspectionResult":
                    vc = "pass" if val == "PASS" else "fail" if val == "FAIL" else ""
                elif isinstance(val, (int, float)) and val == 0 and "Error" in field:
                    vc = ""
                elif isinstance(val, (int, float)) and val > 0 and "Error" in field:
                    vc = "warn"
                else:
                    vc = ""
            metrics += (
                f'<div class="metric-row">'
                f'<span class="mk">{field}</span>'
                f'<span class="mv {vc}">{disp}</span>'
                f'</div>'
            )

        icon = _EQ_ICONS.get(eq_id, "⚙️")
        proc = PROCESS_NAME_MAP.get(eq_id, eq_id)

        parts.append(f"""
        <div class="eq-card {cls}">
          <div class="eq-hdr {cls}">
            <span class="eq-icon">{icon}</span>
            <div class="eq-label">
              <div class="eq-name">{proc}</div>
              <div class="eq-id">{eq_id}</div>
            </div>
            <div class="eq-dot {cls}"></div>
          </div>
          <div class="eq-body">
            {pcb_html}
            {metrics}
          </div>
          <div class="eq-ftr {cls}">{footer}</div>
        </div>""")

        # ── 화살표 (마지막 카드 제외)
        if i < len(SMT_LINE_SEQUENCE) - 1:
            dot = '<div class="pcb-dot"></div>' if pcb else ""
            parts.append(f"""
        <div class="arrow-zone">
          <div class="arrow-shaft">
            <div class="arrow-line"></div>
            <div class="arrow-tip"></div>
          </div>
          {dot}
        </div>""")

    flow_html = "\n".join(parts)

    # ── 통계
    total  = len(emu.completed)
    pass_c = emu.pass_count
    fail_c = emu.fail_count
    yield_ = f"{emu.yield_rate:.1f}%" if total else "—"

    return f"""
{_CSS}
<div class="flow-wrapper">
  <div class="flow-title">⚙&nbsp; SMT LINE — REAL-TIME AAS MONITORING</div>
  <div class="flow-line">
    {flow_html}
  </div>
  <div class="conveyor"></div>
  <div class="bottom-bar">
    <div class="legend">
      <div class="leg-item"><div class="leg-dot" style="background:#475569"></div>대기</div>
      <div class="leg-item"><div class="leg-dot" style="background:#34d399"></div>처리 중</div>
      <div class="leg-item"><div class="leg-dot" style="background:#f87171"></div>FAIL</div>
      <div class="leg-item"><div class="leg-dot" style="background:#f59e0b"></div>PCB 이동</div>
    </div>
    <div class="stats">
      <span class="stat">완료 <b style="color:#e2e8f0">{total}</b></span>
      <span class="stat">PASS <b style="color:#34d399">{pass_c}</b></span>
      <span class="stat">FAIL <b style="color:#f87171">{fail_c}</b></span>
      <span class="stat">수율 <b style="color:#60a5fa">{yield_}</b></span>
      <span class="stat">라인 내 <b style="color:#fcd34d">{emu.in_line_count}</b></span>
    </div>
  </div>
</div>"""


# ══════════════════════════════════════════════════════
#  헤더
# ══════════════════════════════════════════════════════
st.markdown("## 🏭 AAS 기반 가상 SMT 라인 모니터링")
st.caption(
    f"Tick #{st.session_state.tick_count} &nbsp;|&nbsp; "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# ── 제어 바 ────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 2])
with c1:
    st.toggle("⚡ Auto Run", key="auto_run")
with c2:
    tick_speed = st.slider("속도 (초/틱)", 0.5, 3.0, 1.5, 0.5)
with c3:
    if st.button("▶ 1 Tick", use_container_width=True):
        _do_tick(); st.rerun()
with c4:
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.emu        = SMTLineEmulator(fail_rate=0.25)
        st.session_state.tick_count = 0
        st.session_state.event_log  = []
        st.session_state.auto_run   = False
        st.rerun()
with c5:
    fail_pct = st.slider("불량률 (%)", 0, 60, 25, 5)
    emu.fail_rate = fail_pct / 100

st.divider()

# ══════════════════════════════════════════════════════
#  ★ SMT 라인 비주얼 다이어그램
# ══════════════════════════════════════════════════════
st.html(_render_flow_diagram(emu))

st.divider()

# ══════════════════════════════════════════════════════
#  탭 (상세 데이터)
# ══════════════════════════════════════════════════════
tab_eq, tab_line, tab_trace = st.tabs([
    "🔧 설비 AAS 상세",
    "🏗️ 생산 이력 & 로그",
    "🔍 불량 추적 (Traceability)",
])

# ──────────────────────────────────────────────────────
# TAB 1: 설비 AAS 상세
# ──────────────────────────────────────────────────────
with tab_eq:
    st.subheader("설비별 AAS Instance 전체 데이터")
    sel_eq = st.selectbox(
        "설비 선택",
        options=list(emu.instances.keys()),
        format_func=lambda eid: f"{_EQ_ICONS.get(eid,'⚙️')} {eid}  |  {PROCESS_NAME_MAP.get(eid,eid)}",
    )
    if sel_eq:
        inst = emu.instances[sel_eq]
        insp = inst.quality_result.get("InspectionResult")
        status_txt = "🔴 FAIL" if insp == "FAIL" else ("🟢 PASS" if insp == "PASS" else "🔵 대기")

        info_c1, info_c2, info_c3, info_c4 = st.columns(4)
        info_c1.metric("설비 ID",    inst.instance_id)
        info_c2.metric("제조사",     inst.identification.get("manufacturer", "—"))
        info_c3.metric("시리얼",     inst.identification.get("serial", "—"))
        info_c4.metric("검사 상태",  status_txt)

        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**OperationData**")
            op = {k: v for k, v in inst.operation_data.items() if v is not None}
            if op:
                st.dataframe(_safe_df(op), hide_index=True, use_container_width=True)
            else:
                st.caption("_(데이터 없음)_")
        with d2:
            st.markdown("**QualityResult**")
            qr = {k: v for k, v in inst.quality_result.items() if v is not None}
            if qr:
                st.dataframe(
                    _safe_df(qr).style.apply(_hl_insp, axis=1),
                    hide_index=True, use_container_width=True,
                )
            else:
                st.caption("_(데이터 없음)_")

        st.markdown("**Identification**")
        st.json(inst.identification)

# ──────────────────────────────────────────────────────
# TAB 2: 생산 이력 & 이벤트 로그
# ──────────────────────────────────────────────────────
with tab_line:
    left, right = st.columns([3, 2])

    with left:
        st.subheader("생산 완료 이력 (최근 30장)")
        if emu.completed:
            rows = [
                {"바코드": p.pcb_barcode, "로트": p.lot_id,
                 "모델": p.model_name,    "결과": p.final_result}
                for p in reversed(emu.completed[-30:])
            ]
            df = pd.DataFrame(rows)

            def _cr(val: str) -> str:
                if "FAIL" in str(val): return "background-color:#FFCCCC;color:#8B0000"
                if val == "PASS":      return "background-color:#CCFFCC;color:#006400"
                return ""

            st.dataframe(df.style.map(_cr, subset=["결과"]),
                         hide_index=True, height=440)
        else:
            st.info("아직 완료된 PCB가 없습니다.")

    with right:
        st.subheader("이벤트 로그")
        if st.session_state.event_log:
            st.code("\n".join(st.session_state.event_log[:35]), language=None)
        else:
            st.caption("_(이벤트 없음)_")

# ──────────────────────────────────────────────────────
# TAB 3: 불량 추적
# ──────────────────────────────────────────────────────
with tab_trace:
    st.subheader("불량 PCB 공정 데이터 역추적")
    failed = emu.failed_products

    if not failed:
        st.info("💡 아직 불량 PCB가 없습니다. Auto Run을 켜고 잠시 기다려 보세요.")
    else:
        opts = {
            p.pcb_barcode: f"{p.pcb_barcode}  ─  {p.final_result}"
            for p in reversed(failed)
        }
        sel = st.selectbox(
            f"추적할 PCB 선택 (총 {len(failed)}개 불량)",
            options=list(opts.keys()),
            format_func=lambda b: opts[b],
        )
        if sel:
            pcb = emu.all_products[sel]
            ca, cb, cc = st.columns(3)
            ca.metric("바코드",    pcb.pcb_barcode)
            cb.metric("로트",      pcb.lot_id)
            cc.metric("최종 결과", pcb.final_result)

            st.divider()
            st.markdown("#### 공정별 스냅샷 데이터")

            for snap in get_snapshots_by_barcode(sel, emu.all_snapshots):
                insp   = snap.quality_result.get("InspectionResult")
                icon   = "🔴" if insp == "FAIL" else ("🟢" if insp == "PASS" else "🔵")
                expand = insp == "FAIL"

                with st.expander(
                    f"{icon} [{snap.process_name}]  {snap.equipment_instance_id}"
                    f"  —  {snap.timestamp}",
                    expanded=expand,
                ):
                    p1, p2 = st.columns(2)
                    with p1:
                        st.markdown("**OperationData**")
                        op = {k: v for k, v in snap.operation_data.items() if v is not None}
                        st.dataframe(_safe_df(op), hide_index=True) if op else st.caption("_(없음)_")
                    with p2:
                        st.markdown("**QualityResult**")
                        qr = {k: v for k, v in snap.quality_result.items() if v is not None}
                        if qr:
                            st.dataframe(
                                _safe_df(qr).style.apply(_hl_insp, axis=1),
                                hide_index=True,
                            )
                        else:
                            st.caption("_(없음)_")

# ══════════════════════════════════════════════════════
#  Auto Run 루프
# ══════════════════════════════════════════════════════
if st.session_state.get("auto_run", False):
    time.sleep(tick_speed)
    _do_tick()
    st.rerun()
