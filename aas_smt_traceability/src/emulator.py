"""
emulator.py
SMT 라인 PLC 에뮬레이터 — 파이프라인 방식

파이프라인 동작 원리:
  tick() 1회 호출 = 한 스텝 전진
  - 각 설비마다 랜덤 PLC 값을 생성해 AAS Instance에 반영
  - PCB가 현재 스테이지에서 처리된 뒤 다음 스테이지로 이동
  - 마지막 스테이지(ICT) 통과 시 완료 처리
"""

import copy
import random
from datetime import datetime
from typing import Optional

from src.aas_models import ProductPCB, ProcessSnapshot
from src.equipment_factory import create_equipment_types, create_equipment_instances
from src.plc_mapping import create_plc_mappings, build_tag_index
from src.virtual_plc import (
    generate_plc_values,
    apply_plc_to_instance,
    set_inspection_result,
    _DEFECT_TYPES_AOI,
    _DEFECT_TYPES_ICT,
    _DEFECT_TYPES_SPI,
)
from src.production_simulator import SMT_LINE_SEQUENCE, PROCESS_NAME_MAP

# 각 스테이지 인덱스
_STAGE_INDEX = {eq_id: i for i, eq_id in enumerate(SMT_LINE_SEQUENCE)}


class SMTLineEmulator:
    """
    SMT 라인 전체를 파이프라인으로 시뮬레이션하는 에뮬레이터.

    Attributes:
        pipeline     : 각 스테이지에 있는 PCB (None = 비어있음)
        instances    : 설비 AAS Instance 딕셔너리
        all_products : 생성된 모든 PCB (barcode → ProductPCB)
        all_snapshots: 수집된 모든 ProcessSnapshot
        completed    : 완료된 PCB 리스트 (최신 순)
    """

    def __init__(self, fail_rate: float = 0.25):
        self.types     = create_equipment_types()
        self.instances = create_equipment_instances(self.types)
        self.mappings  = create_plc_mappings()
        self.tag_index = build_tag_index(self.mappings)
        self.fail_rate = fail_rate

        self.pipeline: list[Optional[ProductPCB]] = [None] * len(SMT_LINE_SEQUENCE)

        self._pcb_counter      = 0
        self.all_products:   dict[str, ProductPCB]       = {}
        self.all_snapshots:  list[ProcessSnapshot]       = []
        self.completed:      list[ProductPCB]            = []

        # 각 PCB의 예정 불량 스테이지 (없으면 None → PASS)
        self._planned_fail: dict[str, Optional[str]] = {}

    # ── PCB 생성 ─────────────────────────────────
    def _new_pcb(self) -> ProductPCB:
        self._pcb_counter += 1
        barcode = f"PCB-{self._pcb_counter:04d}"
        pcb = ProductPCB(
            pcb_barcode=barcode,
            lot_id="LOT-2026-001",
            work_order_id="WO-2026-0618-01",
            model_name="MODEL-A",
        )
        self.all_products[barcode] = pcb

        # PASS / FAIL 및 불량 스테이지 사전 결정
        if random.random() < self.fail_rate:
            self._planned_fail[barcode] = random.choice(["AOI_01", "ICT_01"])
        else:
            self._planned_fail[barcode] = None
        return pcb

    # ── 스테이지 처리 ─────────────────────────────
    def _process_stage(self, stage_idx: int, pcb: ProductPCB) -> ProcessSnapshot:
        """
        해당 스테이지에서 PCB를 처리한다.
        - 모든 설비의 PLC 값을 새로 생성해 AAS Instance에 반영
        - 검사 설비(SPI/AOI/ICT)는 PASS/FAIL 판정을 설정
        - ProcessSnapshot을 기록하고 반환
        """
        eq_id = SMT_LINE_SEQUENCE[stage_idx]
        inst  = self.instances[eq_id]

        # 전체 설비 PLC 값 갱신
        plc_values = generate_plc_values(self.mappings)
        apply_plc_to_instance(plc_values, self.mappings, self.instances)

        fail_stage = self._planned_fail.get(pcb.pcb_barcode)

        if eq_id == "SPI_01":
            result = "FAIL" if random.random() < 0.10 else "PASS"
            defect = random.choice(_DEFECT_TYPES_SPI) if result == "FAIL" else ""
            set_inspection_result(inst, result, defect)

        elif eq_id == "AOI_01":
            if fail_stage == "AOI_01":
                defect = random.choice(_DEFECT_TYPES_AOI)
                set_inspection_result(inst, "FAIL", defect, {
                    "DefectLocation": f"U{random.randint(1, 20)}",
                    "MeasureValue":   round(random.uniform(0.0, 0.3), 3),
                    "ReviewResult":   "CONFIRM",
                })
            else:
                set_inspection_result(inst, "PASS", extra={"ReviewResult": "PASS"})

        elif eq_id == "ICT_01":
            if fail_stage == "ICT_01":
                defect = random.choice(_DEFECT_TYPES_ICT)
                set_inspection_result(inst, "FAIL", defect, {
                    "ActualValue":   round(random.uniform(80, 95), 2),
                    "StandardValue": 100.0,
                })
            else:
                set_inspection_result(inst, "PASS", extra={
                    "ActualValue":   round(random.uniform(98, 102), 2),
                    "StandardValue": 100.0,
                })

        snap = ProcessSnapshot(
            pcb_barcode=pcb.pcb_barcode,
            lot_id=pcb.lot_id,
            work_order_id=pcb.work_order_id,
            process_name=PROCESS_NAME_MAP[eq_id],
            equipment_instance_id=eq_id,
            timestamp=datetime.now().isoformat(timespec="seconds"),
            operation_data=copy.deepcopy(inst.operation_data),
            quality_result=copy.deepcopy(inst.quality_result),
        )
        self.all_snapshots.append(snap)
        return snap

    # ── 틱 ───────────────────────────────────────
    def tick(self) -> list[tuple]:
        """
        파이프라인 한 스텝 전진.

        처리 순서: 마지막 스테이지 → 첫 스테이지 (블로킹 방지)
        새 PCB는 첫 스테이지가 비어있을 때 자동 투입.

        반환: [(event_type, barcode, stage_name), ...]
          event_type: "ENTER" | "MOVE" | "COMPLETE" | "BLOCK"
        """
        events: list[tuple] = []
        last_idx = len(SMT_LINE_SEQUENCE) - 1

        for idx in range(last_idx, -1, -1):
            pcb = self.pipeline[idx]
            if pcb is None:
                continue

            self._process_stage(idx, pcb)
            eq_id = SMT_LINE_SEQUENCE[idx]

            if idx == last_idx:
                # 완료
                fail_stage = self._planned_fail.get(pcb.pcb_barcode)
                if fail_stage == "AOI_01":
                    pcb.final_result = "FAIL at AOI"
                elif fail_stage == "ICT_01":
                    pcb.final_result = "FAIL at ICT"
                else:
                    pcb.final_result = "PASS"
                pcb.current_process = "COMPLETE"
                self.completed.append(pcb)
                self.pipeline[idx] = None
                events.append(("COMPLETE", pcb.pcb_barcode, PROCESS_NAME_MAP[eq_id]))

            else:
                if self.pipeline[idx + 1] is None:
                    self.pipeline[idx + 1] = pcb
                    self.pipeline[idx]     = None
                    next_eq = SMT_LINE_SEQUENCE[idx + 1]
                    pcb.current_process = PROCESS_NAME_MAP[next_eq]
                    events.append(("MOVE", pcb.pcb_barcode, PROCESS_NAME_MAP[next_eq]))
                else:
                    events.append(("BLOCK", pcb.pcb_barcode, PROCESS_NAME_MAP[eq_id]))

        # 새 PCB 투입
        if self.pipeline[0] is None:
            new_pcb = self._new_pcb()
            self.pipeline[0] = new_pcb
            new_pcb.current_process = PROCESS_NAME_MAP[SMT_LINE_SEQUENCE[0]]
            events.append(("ENTER", new_pcb.pcb_barcode, PROCESS_NAME_MAP[SMT_LINE_SEQUENCE[0]]))

        return events

    # ── 편의 속성 ─────────────────────────────────
    @property
    def failed_products(self) -> list[ProductPCB]:
        return [p for p in self.completed if "FAIL" in p.final_result]

    @property
    def pass_count(self) -> int:
        return sum(1 for p in self.completed if p.final_result == "PASS")

    @property
    def fail_count(self) -> int:
        return len(self.failed_products)

    @property
    def yield_rate(self) -> float:
        total = len(self.completed)
        return (self.pass_count / total * 100) if total > 0 else 0.0

    @property
    def in_line_count(self) -> int:
        return sum(1 for x in self.pipeline if x is not None)
