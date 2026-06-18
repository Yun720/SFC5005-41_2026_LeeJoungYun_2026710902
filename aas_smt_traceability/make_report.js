/**
 * AAS 기반 가상 SMT 라인 모니터링 프로토타입 구현 보고서
 * 학번: 2026710902  이름: 이정윤
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, ExternalHyperlink,
  PageBreak, TableOfContents,
} = require("C:/Users/MICUBE/AppData/Roaming/npm/node_modules/docx");
const fs = require("fs");
const path = require("path");

const FONT = "맑은 고딕";
const IMG_DIR = path.join(__dirname, "images");
const OUT = path.join(__dirname, "AAS_SMT_구현보고서_이정윤_2026710902.docx");

// ── 색상 팔레트 ──────────────────────────────────────────────
const C = {
  primary:   "1A3C5E",  // 딥 네이비
  accent:    "2196F3",  // 블루
  light:     "E3F2FD",  // 연한 파랑
  lightGray: "F5F5F5",
  midGray:   "DDDDDD",
  darkGray:  "555555",
  white:     "FFFFFF",
  black:     "111111",
  green:     "1B5E20",
  greenBg:   "E8F5E9",
};

// ── 헬퍼 ─────────────────────────────────────────────────────
function border(color = C.midGray, size = 4) {
  return { style: BorderStyle.SINGLE, size, color };
}
function cellBorders(color = C.midGray) {
  const b = border(color, 4);
  return { top: b, bottom: b, left: b, right: b };
}
function noBorder() {
  const n = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: n, bottom: n, left: n, right: n };
}

function t(text, opts = {}) {
  return new TextRun({ text, font: FONT, ...opts });
}
function bold(text, size = 22, color = C.black) {
  return t(text, { bold: true, size, color });
}
function para(children, opts = {}) {
  return new Paragraph({ children: Array.isArray(children) ? children : [children], ...opts });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: FONT, bold: true, size: 36, color: C.primary })],
    spacing: { before: 360, after: 160 },
    border: { bottom: border(C.accent, 8) },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: FONT, bold: true, size: 28, color: C.primary })],
    spacing: { before: 280, after: 120 },
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, font: FONT, bold: true, size: 24, color: C.darkGray })],
    spacing: { before: 200, after: 80 },
  });
}
function bodyText(text, opts = {}) {
  return para([t(text, { size: 22, color: C.black, ...opts })], {
    spacing: { before: 60, after: 60 },
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [t(text, { size: 22, color: C.black })],
    spacing: { before: 40, after: 40 },
  });
}
function numbered(text) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    children: [t(text, { size: 22, color: C.black })],
    spacing: { before: 40, after: 40 },
  });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}
function spacer(lines = 1) {
  return new Paragraph({ children: [t("")], spacing: { before: 80 * lines, after: 0 } });
}
function caption(text) {
  return para(
    [t(text, { size: 18, color: C.darkGray, italics: true })],
    { alignment: AlignmentType.CENTER, spacing: { before: 60, after: 120 } }
  );
}

// ── 이미지 로드 ───────────────────────────────────────────────
function loadImg(filename, widthPx, heightPx) {
  const p = path.join(IMG_DIR, filename);
  if (!fs.existsSync(p)) return null;
  return new ImageRun({
    type: "png",
    data: fs.readFileSync(p),
    transformation: { width: widthPx, height: heightPx },
    altText: { title: filename, description: filename, name: filename },
  });
}
function imgPara(filename, w, h, alt) {
  const img = loadImg(filename, w, h);
  if (!img) return bodyText(`[이미지: ${alt || filename}]`);
  return new Paragraph({
    children: [img],
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 60 },
  });
}

// ── 테이블 헬퍼 ──────────────────────────────────────────────
function simpleRow(cells, isHeader = false) {
  return new TableRow({
    tableHeader: isHeader,
    children: cells.map(({ text, width, bg, span }) =>
      new TableCell({
        width: { size: width || 2000, type: WidthType.DXA },
        columnSpan: span,
        borders: cellBorders(C.midGray),
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          para(
            [t(text, { size: 20, bold: isHeader, color: isHeader ? C.white : C.black, font: FONT })],
            { alignment: AlignmentType.CENTER }
          ),
        ],
      })
    ),
  });
}

// ═══════════════════════════════════════════════════════════
// 문서 구성
// ═══════════════════════════════════════════════════════════

// 1) 표지
const coverPage = [
  spacer(6),
  para(
    [t("스마트팩토리 응용프로그래밍", { font: FONT, size: 28, color: C.darkGray })],
    { alignment: AlignmentType.CENTER }
  ),
  spacer(1),
  para(
    [t("AAS 기반 가상 SMT 라인 모니터링 프로토타입", { font: FONT, size: 42, bold: true, color: C.primary })],
    { alignment: AlignmentType.CENTER }
  ),
  spacer(1),
  para(
    [t("구현 보고서", { font: FONT, size: 36, bold: true, color: C.accent })],
    { alignment: AlignmentType.CENTER }
  ),
  spacer(3),
  // 구분선
  new Paragraph({ border: { bottom: border(C.accent, 10) }, children: [t("")] }),
  spacer(2),
  para([t("학  번 : 2026710902", { font: FONT, size: 26, color: C.darkGray })], { alignment: AlignmentType.CENTER }),
  spacer(1),
  para([t("이  름 : 이정윤", { font: FONT, size: 26, color: C.darkGray })], { alignment: AlignmentType.CENTER }),
  spacer(1),
  para([t("제출일 : 2026년 6월 18일", { font: FONT, size: 24, color: C.darkGray })], { alignment: AlignmentType.CENTER }),
  spacer(1),
  para([t("과  목 : 스마트팩토리 응용프로그래밍", { font: FONT, size: 24, color: C.darkGray })], { alignment: AlignmentType.CENTER }),
  spacer(2),
  para(
    [
      t("GitHub: ", { font: FONT, size: 22, color: C.darkGray }),
      new ExternalHyperlink({
        children: [new TextRun({ text: "https://github.com/Yun720/SFC5005-41_2026_LeeJoungYun_2026710902", font: FONT, size: 22, style: "Hyperlink" })],
        link: "https://github.com/Yun720/SFC5005-41_2026_LeeJoungYun_2026710902",
      }),
    ],
    { alignment: AlignmentType.CENTER }
  ),
  pageBreak(),
];

// 2) 초록
const abstractSection = [
  h1("초록 (Abstract)"),
  bodyText(
    "본 프로젝트는 스마트 제조 환경에서 자산관리쉘(AAS, Asset Administration Shell) 개념을 적용하여 " +
    "SMT(Surface Mount Technology) 생산 라인의 가상 모니터링 시스템을 구현한 것이다. " +
    "AAS의 Type/Instance 구조를 Python 데이터 클래스로 모델링하고, PLC TAG와 AAS 속성 간 36개의 매핑 테이블을 정의하였다. " +
    "가상 PLC 에뮬레이터는 ScreenPrinter, SPI, Mounter, Reflow, AOI, ICT의 6개 공정 설비에 대해 " +
    "현실적인 범위의 센서 데이터를 실시간으로 생성하며, 파이프라인 방식으로 PCB를 순차 처리한다. " +
    "Streamlit 기반 웹 대시보드를 통해 라인 흐름, 설비별 AAS 데이터, 생산 이력, 불량 PCB 추적(Traceability)을 " +
    "직관적으로 시각화하였다. " +
    "단위 테스트 13개를 포함하며, 모든 핵심 모듈이 독립적으로 검증되었다. " +
    "본 구현은 실제 OPC UA 또는 데이터베이스 연동으로 확장 가능한 학습용 MVP로서의 가치를 갖는다."
  ),
  spacer(1),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 7360],
    rows: [
      simpleRow([
        { text: "키워드", width: 2000, bg: C.primary, isHeader: true },
        { text: "AAS, SMT, 디지털 트윈, PLC TAG 매핑, Streamlit, 불량 추적", width: 7360 },
      ]),
    ],
  }),
  pageBreak(),
];

// 3) 목차
const tocSection = [
  h1("목차"),
  new TableOfContents("목차", { hyperlink: true, headingStyleRange: "1-3" }),
  pageBreak(),
];

// 4) 서론
const introSection = [
  h1("1. 서론"),
  h2("1.1 연구 배경 및 목적"),
  bodyText(
    "스마트 제조(Smart Manufacturing)는 IoT, 디지털 트윈, AI를 융합하여 제조 설비의 상태를 실시간으로 파악하고 " +
    "생산 품질을 향상시키는 패러다임이다. IEC 62890과 Industry 4.0 표준에서 제안하는 " +
    "AAS(Asset Administration Shell)는 설비의 디지털 표현을 표준화하는 핵심 개념으로, " +
    "물리적 자산(Physical Asset)과 디지털 세계를 연결하는 인터페이스를 제공한다."
  ),
  bodyText(
    "본 프로젝트의 목적은 SMT 라인의 6개 공정 설비를 AAS Type/Instance 구조로 모델링하고, " +
    "가상 PLC 에뮬레이터와 연동하여 실시간 모니터링 및 불량 추적이 가능한 웹 대시보드를 구현하는 것이다."
  ),
  h2("1.2 구현 목표"),
  bullet("AAS Type/Instance 구조 설계 및 Python 구현"),
  bullet("36개 PLC TAG ↔ AAS 속성 매핑 테이블 정의"),
  bullet("파이프라인 방식의 가상 SMT 라인 에뮬레이터 구현"),
  bullet("Streamlit 기반 실시간 웹 대시보드 (라인 흐름 시각화)"),
  bullet("바코드 기반 불량 PCB 추적(Traceability) 기능"),
  bullet("단위 테스트 13개 작성 및 검증"),
  pageBreak(),
];

// 5) 이론적 배경
const theorySection = [
  h1("2. 이론적 배경"),
  h2("2.1 AAS (Asset Administration Shell)"),
  bodyText(
    "AAS는 물리적 자산을 디지털로 표현하는 표준 인터페이스로, Industry 4.0의 핵심 요소이다. " +
    "AAS는 크게 AAS Type(설비 종류 템플릿)과 AAS Instance(실제 설비 1대)로 구성된다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 3580, 3580],
    rows: [
      simpleRow(
        [
          { text: "구분", width: 2200, bg: C.primary },
          { text: "AAS Type", width: 3580, bg: C.primary },
          { text: "AAS Instance", width: 3580, bg: C.primary },
        ],
        true
      ),
      simpleRow([
        { text: "역할", width: 2200, bg: C.lightGray },
        { text: "설비 종류 템플릿 (클래스)", width: 3580 },
        { text: "실제 설비 1대 (객체)", width: 3580 },
      ]),
      simpleRow([
        { text: "예시", width: 2200, bg: C.lightGray },
        { text: "ScreenPrinterType", width: 3580 },
        { text: "ScreenPrinter_01", width: 3580 },
      ]),
      simpleRow([
        { text: "포함 정보", width: 2200, bg: C.lightGray },
        { text: "공정명, 운전/품질 필드 목록", width: 3580 },
        { text: "Identification, OperationData, QualityResult", width: 3580 },
      ]),
    ],
  }),
  caption("표 1. AAS Type과 Instance 비교"),
  h2("2.2 SMT (Surface Mount Technology) 공정"),
  bodyText(
    "SMT는 PCB(인쇄회로기판) 위에 전자 부품을 표면 실장하는 공정 기술이다. " +
    "본 프로젝트에서 구현한 SMT 라인의 6단계 공정은 다음과 같다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1200, 2200, 5960],
    rows: [
      simpleRow(
        [
          { text: "순서", width: 1200, bg: C.primary },
          { text: "설비", width: 2200, bg: C.primary },
          { text: "역할", width: 5960, bg: C.primary },
        ],
        true
      ),
      ...[
        ["1", "ScreenPrinter", "스텐실을 통해 PCB에 솔더 페이스트를 도포"],
        ["2", "SPI", "Solder Paste Inspection - 솔더 도포 상태 검사"],
        ["3", "Mounter", "Pick & Place - 부품을 PCB에 장착"],
        ["4", "Reflow", "고온 오븐에서 솔더를 녹여 부품 고정"],
        ["5", "AOI", "Automated Optical Inspection - 외관 검사"],
        ["6", "ICT", "In-Circuit Test - 전기적 특성 검사"],
      ].map(([n, eq, role], i) =>
        simpleRow([
          { text: n, width: 1200, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: eq, width: 2200, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: role, width: 5960, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 2. SMT 라인 6단계 공정"),
  pageBreak(),
];

// 6) 시스템 설계
const designSection = [
  h1("3. 시스템 설계"),
  h2("3.1 전체 아키텍처"),
  bodyText(
    "시스템은 크게 데이터 모델 계층, 에뮬레이션 계층, 시각화 계층의 3단계로 구성된다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2500, 6860],
    rows: [
      simpleRow(
        [{ text: "계층", width: 2500, bg: C.primary }, { text: "구성 요소", width: 6860, bg: C.primary }],
        true
      ),
      simpleRow([
        { text: "데이터 모델", width: 2500, bg: C.lightGray },
        { text: "aas_models.py, equipment_factory.py, plc_mapping.py", width: 6860 },
      ]),
      simpleRow([
        { text: "에뮬레이션", width: 2500, bg: C.lightGray },
        { text: "virtual_plc.py, production_simulator.py, emulator.py", width: 6860 },
      ]),
      simpleRow([
        { text: "시각화", width: 2500, bg: C.lightGray },
        { text: "dashboard.py (Streamlit 웹 대시보드)", width: 6860 },
      ]),
      simpleRow([
        { text: "추적", width: 2500, bg: C.lightGray },
        { text: "traceability.py (바코드 기반 불량 추적)", width: 6860 },
      ]),
      simpleRow([
        { text: "테스트", width: 2500, bg: C.lightGray },
        { text: "tests/test_traceability.py (13개 단위 테스트)", width: 6860 },
      ]),
    ],
  }),
  caption("표 3. 시스템 아키텍처 계층 구성"),
  h2("3.2 프로젝트 폴더 구조"),
  bodyText("프로젝트는 다음과 같은 폴더 구조로 구성된다."),
  new Paragraph({
    children: [
      t(
        "aas_smt_traceability/\n" +
        "  dashboard.py          웹 대시보드 (Streamlit)\n" +
        "  main.py               CLI 진입점\n" +
        "  requirements.txt      의존 패키지\n" +
        "  src/\n" +
        "    aas_models.py       핵심 데이터 모델 (dataclass)\n" +
        "    equipment_factory.py AAS Type/Instance 생성\n" +
        "    plc_mapping.py      PLC TAG ↔ AAS 매핑 테이블\n" +
        "    virtual_plc.py      가상 PLC 값 생성\n" +
        "    production_simulator.py  SMT 라인 시뮬레이션\n" +
        "    emulator.py         파이프라인 에뮬레이터\n" +
        "    traceability.py     불량 추적\n" +
        "  tests/\n" +
        "    test_traceability.py  단위 테스트",
        { font: "Consolas", size: 18, color: C.darkGray }
      ),
    ],
    shading: { fill: C.lightGray, type: ShadingType.CLEAR },
    spacing: { before: 100, after: 100 },
    indent: { left: 360 },
  }),
  pageBreak(),
];

// 7) 구현 상세
const implSection = [
  h1("4. 구현 상세"),
  h2("4.1 데이터 모델 설계 (aas_models.py)"),
  bodyText(
    "Python dataclass를 이용해 5개의 핵심 데이터 모델을 정의하였다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: [
      simpleRow(
        [{ text: "클래스", width: 2800, bg: C.primary }, { text: "주요 필드", width: 6560, bg: C.primary }],
        true
      ),
      ...([
        ["EquipmentAASType", "type_id, type_name, process_name, operation_fields, quality_fields"],
        ["EquipmentAASInstance", "instance_id, type_id, display_name, identification, operation_data, quality_result"],
        ["PLCTagMapping", "plc_tag, equipment_instance_id, aas_path, data_type, unit"],
        ["ProductPCB", "pcb_barcode, lot_id, work_order_id, model_name, current_process, final_result"],
        ["ProcessSnapshot", "pcb_barcode, process_name, equipment_instance_id, timestamp, operation_data, quality_result"],
      ]).map(([cls, fields], i) =>
        simpleRow([
          { text: cls, width: 2800, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: fields, width: 6560, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 4. 핵심 데이터 클래스"),
  h2("4.2 PLC TAG 매핑 (plc_mapping.py)"),
  bodyText(
    "총 36개의 PLC TAG를 AAS 속성 경로에 매핑하였다. " +
    "예를 들어 PLC.REFLOW.ZONE1_TEMP 태그는 Reflow_01.OperationData.Zone1Temperature에 매핑된다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3200, 3760, 1200, 1200],
    rows: [
      simpleRow(
        [
          { text: "PLC TAG", width: 3200, bg: C.primary },
          { text: "AAS 경로", width: 3760, bg: C.primary },
          { text: "타입", width: 1200, bg: C.primary },
          { text: "단위", width: 1200, bg: C.primary },
        ],
        true
      ),
      ...([
        ["PLC.SCREEN.TEMP", "ScreenPrinter_01.OperationData.Temp", "float", "°C"],
        ["PLC.SPI.INSPECTION", "SPI_01.QualityResult.InspectionResult", "str", "-"],
        ["PLC.MOUNTER.SPEED", "Mounter_01.OperationData.PlacementSpeed", "float", "CPH"],
        ["PLC.REFLOW.ZONE1_TEMP", "Reflow_01.OperationData.Zone1Temperature", "float", "°C"],
        ["PLC.AOI.RESULT", "AOI_01.QualityResult.InspectionResult", "str", "-"],
        ["PLC.ICT.ACTUAL_VAL", "ICT_01.QualityResult.ActualValue", "float", "%"],
      ]).map(([tag, path, dtype, unit], i) =>
        simpleRow([
          { text: tag, width: 3200, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: path, width: 3760, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: dtype, width: 1200, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: unit, width: 1200, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 5. PLC TAG 매핑 예시 (전체 36개 중 일부)"),
  h2("4.3 파이프라인 에뮬레이터 (emulator.py)"),
  bodyText(
    "SMTLineEmulator 클래스는 6개 스테이지를 파이프라인으로 시뮬레이션한다. " +
    "tick() 1회 호출이 한 스텝 전진을 의미하며, 블로킹 방지를 위해 마지막 스테이지부터 역순으로 처리한다."
  ),
  bullet("pipeline: 각 스테이지에 있는 PCB 목록 (None = 비어있음)"),
  bullet("tick(): 파이프라인 1 스텝 전진, 이벤트 목록 반환"),
  bullet("ENTER / MOVE / COMPLETE / BLOCK 4가지 이벤트 타입"),
  bullet("불량 스테이지 사전 결정 (_planned_fail): AOI 또는 ICT"),
  bullet("fail_rate 파라미터로 불량률 조정 (기본값 25%)"),
  h2("4.4 웹 대시보드 (dashboard.py)"),
  bodyText(
    "Streamlit v1.58 기반 웹 대시보드를 구현하였다. " +
    "st.html()을 활용한 다크 테마 SMT 라인 흐름도와 3개의 탭으로 구성된다."
  ),
  bullet("SMT 라인 흐름 시각화: CSS 애니메이션 (pulse, blink, slide, belt)"),
  bullet("탭 1 (설비 AAS 상세): 설비별 AAS Instance 전체 데이터"),
  bullet("탭 2 (생산 이력 & 로그): 완료 PCB 목록, 틱 이벤트 로그"),
  bullet("탭 3 (불량 추적): 바코드 입력 → 공정별 스냅샷 조회"),
  bullet("Auto Run 모드: 자동 틱 실행, 속도 및 불량률 실시간 조정"),
  pageBreak(),
];

// 8) 결과 및 분석
const resultSection = [
  h1("5. 결과 및 분석"),
  h2("5.1 대시보드 실행 화면"),
  imgPara("dashboard_overview.png", 580, 300, "대시보드 전체 화면"),
  caption("그림 1. AAS 기반 가상 SMT 라인 모니터링 대시보드 전체 화면"),
  bodyText(
    "대시보드는 상단에 제어 영역(Auto Run, 속도, 불량률), 중앙에 SMT 라인 흐름도, " +
    "하단에 3개 탭을 배치하였다. 다크 테마와 CSS 애니메이션으로 직관적인 라인 상태를 표현한다."
  ),
  h2("5.2 SMT 라인 흐름 시각화"),
  imgPara("dashboard_flow.png", 580, 200, "SMT 라인 흐름도"),
  caption("그림 2. SMT 라인 실시간 흐름 다이어그램 (6개 설비 카드)"),
  bodyText(
    "각 설비는 카드 형태로 표시되며, PCB가 라인에 투입되면 설비 카드가 활성화된다. " +
    "FAIL 판정 설비는 빨간색 펄스 애니메이션으로 강조된다. " +
    "설비 간 화살표와 컨베이어 벨트 애니메이션으로 흐름을 직관적으로 표현한다."
  ),
  h2("5.3 단위 테스트 결과"),
  bodyText("총 13개의 단위 테스트를 작성하였으며, 모두 PASS하였다."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3200, 1800, 4360],
    rows: [
      simpleRow(
        [
          { text: "테스트 클래스", width: 3200, bg: C.primary },
          { text: "테스트 수", width: 1800, bg: C.primary },
          { text: "검증 내용", width: 4360, bg: C.primary },
        ],
        true
      ),
      ...([
        ["TestEquipmentFactory", "4", "AAS Type/Instance 생성 및 속성 검증"],
        ["TestPLCMapping", "3", "매핑 테이블 생성, JSON 저장/로드, 인덱스 빌드"],
        ["TestVirtualPLC", "2", "PLC 값 생성 범위, Instance 반영 검증"],
        ["TestSimulation", "4", "PCB 생성, 파이프라인 처리, PASS/FAIL 판정"],
      ]).map(([cls, cnt, desc], i) =>
        simpleRow([
          { text: cls, width: 3200, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: cnt, width: 1800, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: desc, width: 4360, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 6. 단위 테스트 결과 (전체 13개 PASS, 소요 시간 0.008초)"),
  h2("5.4 에뮬레이터 성능"),
  bodyText(
    "에뮬레이터는 설정된 불량률(기본 25%)에 따라 AOI 또는 ICT에서 불량 판정이 이루어진다. " +
    "파이프라인 방식으로 최대 6개의 PCB가 동시에 라인 내에 존재할 수 있으며, " +
    "블로킹 이벤트 발생 시 해당 스테이지에서 PCB 대기 상태가 유지된다."
  ),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows: [
      simpleRow(
        [{ text: "지표", width: 3000, bg: C.primary }, { text: "측정값", width: 6360, bg: C.primary }],
        true
      ),
      ...([
        ["불량률 설정 범위", "0% ~ 100% (슬라이더 조정)"],
        ["파이프라인 최대 PCB 수", "6개 (스테이지 수)"],
        ["불량 판정 설비", "AOI_01, ICT_01"],
        ["추적 단위", "PCB 바코드 (PCB-0001 형식)"],
        ["생성 스냅샷", "설비 통과 시 자동 저장 (운전 + 품질 데이터)"],
      ]).map(([metric, val], i) =>
        simpleRow([
          { text: metric, width: 3000, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: val, width: 6360, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 7. 에뮬레이터 주요 성능 지표"),
  pageBreak(),
];

// 9) AI 활용
const aiSection = [
  h1("6. AI 활용 내용"),
  h2("6.1 Claude Code 활용"),
  bodyText(
    "본 프로젝트 전체 구현 과정에서 Anthropic의 Claude Code (claude-sonnet-4-6)를 활용하였다. " +
    "AI 도구를 활용한 구체적인 내용은 다음과 같다."
  ),
  numbered("AAS Type/Instance 데이터 모델 설계 및 Python dataclass 구현"),
  numbered("36개 PLC TAG 매핑 테이블 생성 (현실적인 센서 범위 포함)"),
  numbered("파이프라인 에뮬레이터 알고리즘 설계 (역순 처리로 블로킹 방지)"),
  numbered("Streamlit 대시보드 CSS 애니메이션 및 다크 테마 구현"),
  numbered("Streamlit v1.58 deprecation 오류 수정 (use_container_width, applymap → map)"),
  numbered("Arrow 직렬화 오류 해결 (_safe_df() 헬퍼 함수)"),
  numbered("단위 테스트 13개 자동 생성 및 검증"),
  h2("6.2 주요 디버깅 사례"),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3500, 5860],
    rows: [
      simpleRow(
        [{ text: "문제", width: 3500, bg: C.primary }, { text: "해결 방법", width: 5860, bg: C.primary }],
        true
      ),
      ...([
        ["Streamlit use_container_width deprecated", "파라미터 제거 (기본값 사용)"],
        ["DataFrame Arrow 직렬화 오류", "_safe_df()로 모든 값을 str 변환"],
        ["st.components.v1.html deprecated", "st.html()로 대체 (인라인 렌더링)"],
        ["파이프라인 블로킹", "역순 처리 (마지막→첫 스테이지)로 해결"],
        ["Python 경로 충돌", "python -m streamlit run 명령어 사용"],
      ]).map(([prob, sol], i) =>
        simpleRow([
          { text: prob, width: 3500, bg: i % 2 === 0 ? C.lightGray : C.white },
          { text: sol, width: 5860, bg: i % 2 === 0 ? C.lightGray : C.white },
        ])
      ),
    ],
  }),
  caption("표 8. 주요 디버깅 사례 및 해결 방법"),
  h2("6.3 AI 활용 회고"),
  bodyText(
    "AI 코딩 도구를 활용함으로써 AAS 개념 설계부터 구현, 디버깅까지의 전체 과정을 효율적으로 진행할 수 있었다. " +
    "특히 Streamlit API 변경사항 대응, CSS 애니메이션 구현, 복잡한 파이프라인 알고리즘 설계 등에서 " +
    "AI의 도움이 크게 유효하였다. " +
    "다만 AI가 제안한 코드를 무비판적으로 수용하지 않고 실제 실행 결과를 검증하며 수정하는 과정이 필요하였으며, " +
    "이를 통해 도구 활용 역량과 코드 이해도를 동시에 향상시킬 수 있었다."
  ),
  pageBreak(),
];

// 10) 고찰 및 결론
const discussionSection = [
  h1("7. 고찰 (Discussion)"),
  h2("7.1 잘된 점"),
  bullet(
    "AAS Type/Instance 구조를 Python dataclass로 명확하게 표현하여 확장성이 높은 데이터 모델을 구현하였다."
  ),
  bullet(
    "파이프라인 역순 처리 알고리즘으로 블로킹 없는 안정적인 에뮬레이터를 구현하였다."
  ),
  bullet(
    "ProcessSnapshot 개념으로 PCB가 설비를 통과하는 순간의 모든 데이터를 캡처하여 완전한 이력 추적이 가능하다."
  ),
  bullet(
    "st.html()을 활용한 커스텀 HTML/CSS 시각화로 Streamlit의 기본 컴포넌트 한계를 극복하였다."
  ),
  h2("7.2 한계점"),
  bullet(
    "가상 PLC 데이터는 설정된 범위 내 랜덤값으로, 실제 공정의 시계열 특성(추세, 계절성)을 반영하지 못한다."
  ),
  bullet(
    "현재 데이터는 메모리에만 저장되어 서버 재시작 시 이력이 소실된다. 실제 시스템에서는 데이터베이스 연동이 필요하다."
  ),
  bullet(
    "AAS 표준(IEC 62890)의 완전한 구현이 아닌 학습 목적의 단순화된 구현으로, 실제 표준과 차이가 있다."
  ),
  bullet(
    "GIF 자동 생성 기능이 미구현으로, 동적 라인 흐름을 정적 스크린샷으로만 표현한다."
  ),
  pageBreak(),
];

const conclusionSection = [
  h1("8. 결론 및 향후 연구"),
  h2("8.1 결론"),
  bodyText(
    "본 프로젝트에서는 AAS(Asset Administration Shell) 개념을 Python으로 구현하고, " +
    "6단계 SMT 공정의 가상 라인을 파이프라인 에뮬레이터로 시뮬레이션하였다. " +
    "Streamlit 기반 웹 대시보드를 통해 실시간 라인 모니터링과 불량 PCB 추적 기능을 구현하였으며, " +
    "단위 테스트 13개로 핵심 모듈의 정확성을 검증하였다."
  ),
  bodyText(
    "AI 코딩 도구(Claude Code)를 활용하여 설계부터 구현, 디버깅, 보고서 작성까지의 전체 과정을 효율적으로 수행하였다. " +
    "이를 통해 AI 도구가 복잡한 소프트웨어 개발 과정에서 생산성을 크게 향상시킬 수 있음을 확인하였다."
  ),
  h2("8.2 향후 연구 방향"),
  numbered(
    "OPC UA 또는 MQTT 프로토콜을 통한 실제 PLC 데이터 연동으로 가상 → 실제 시스템으로 전환"
  ),
  numbered(
    "PostgreSQL 또는 InfluxDB 연동으로 영속적인 생산 이력 저장 및 대용량 데이터 처리"
  ),
  numbered(
    "머신러닝 기반 불량 예측 모델 추가로 예지보전(Predictive Maintenance) 기능 구현"
  ),
  numbered(
    "AAS 표준(IEC 62890) 완전 준수 및 AASX 포맷 내보내기/가져오기 기능 구현"
  ),
  numbered(
    "실시간 OEE(Overall Equipment Effectiveness) 계산 및 생산성 지표 시각화"
  ),
  pageBreak(),
];

// 11) 참고문헌
const refSection = [
  h1("참고문헌"),
  bodyText("[1] IEC 62890:2020, Industrial-process measurement, control and automation — Life-cycle-management for systems and components."),
  bodyText("[2] Platform Industrie 4.0, \"Details of the Asset Administration Shell,\" Version 3.0, 2022."),
  bodyText("[3] Streamlit Inc., \"Streamlit Documentation,\" https://docs.streamlit.io, 2024."),
  bodyText("[4] Python Software Foundation, \"dataclasses — Data Classes,\" Python 3.12 Documentation."),
  bodyText("[5] 스마트팩토리추진단, \"스마트공장 개념 및 구축 전략,\" 2023."),
  spacer(2),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      t("GitHub Repository: ", { font: FONT, size: 20, color: C.darkGray }),
      new ExternalHyperlink({
        children: [new TextRun({ text: "https://github.com/Yun720/SFC5005-41_2026_LeeJoungYun_2026710902", font: FONT, size: 20, style: "Hyperlink" })],
        link: "https://github.com/Yun720/SFC5005-41_2026_LeeJoungYun_2026710902",
      }),
    ],
  }),
];

// ── 문서 생성 ─────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 }, spacing: { before: 40, after: 40 } } } }],
      },
      {
        reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 }, spacing: { before: 40, after: 40 } } } }],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: FONT, color: C.primary },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: C.primary },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: C.darkGray },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },  // A4
          margin: { top: 1440, right: 1134, bottom: 1440, left: 1134 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              children: [
                t("AAS 기반 가상 SMT 라인 모니터링 프로토타입 구현 보고서", { font: FONT, size: 18, color: C.darkGray }),
                t("      |      이정윤 (2026710902)", { font: FONT, size: 18, color: C.darkGray }),
              ],
              border: { bottom: border(C.midGray, 4) },
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              border: { top: border(C.midGray, 4) },
              children: [
                t("- ", { font: FONT, size: 18, color: C.darkGray }),
                new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: C.darkGray }),
                t(" -", { font: FONT, size: 18, color: C.darkGray }),
              ],
            }),
          ],
        }),
      },
      children: [
        ...coverPage,
        ...abstractSection,
        ...tocSection,
        ...introSection,
        ...theorySection,
        ...designSection,
        ...implSection,
        ...resultSection,
        ...aiSection,
        ...discussionSection,
        ...conclusionSection,
        ...refSection,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("✓ 보고서 생성 완료:", OUT);
}).catch((e) => {
  console.error("오류:", e.message);
  process.exit(1);
});
