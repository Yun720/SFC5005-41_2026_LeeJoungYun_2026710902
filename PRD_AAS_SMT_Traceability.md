# PRD: AAS 기반 가상 SMT 라인 PLC TAG 매핑 및 불량 추적 모니터링 시스템

## 1. 문제 / 배경

스마트팩토리 현장에서는 설비 PLC TAG 데이터가 설비별로 흩어져 있고, TAG 이름만으로는 데이터의 의미와 제품 생산 이력을 함께 이해하기 어렵다. 특히 SMT 라인에서 불량이 발생했을 때 해당 제품이 어떤 설비를 통과했는지, 당시 온도·압력·전력·검사값이 어땠는지 추적하려면 데이터 구조가 표준화되어 있어야 한다. 본 프로젝트는 AAS(Asset Administration Shell) 개념을 활용해 설비 데이터를 구조화하고, PLC TAG와 AAS 속성을 매핑하여 가상 SMT 라인의 생산 및 불량 추적을 모니터링하는 프로토타입을 만든다.

## 2. 목표 / 범위

본 프로젝트의 목표는 SMT 설비 AAS Type을 정의하고, 이를 참조해 설비 Instance AAS를 생성한 뒤, 가상 PLC TAG 데이터를 AAS 속성에 매핑하여 제품 생산 흐름과 품질 이력을 모니터링하는 것이다. 최종적으로 PCB Barcode 기준으로 제품이 지나간 공정별 설비 데이터 스냅샷을 저장하고, 불량 발생 시 이전 공정 데이터를 역추적할 수 있어야 한다.

범위에 포함하는 것은 AAS Type/Instance 관리, PLC TAG 매핑 테이블, 가상 PLC 데이터 생성, 가상 SMT 생산 흐름, 제품별 공정 이력 조회, 불량 추적 대시보드이다. 실제 PLC 통신, 실제 AASX 파일 완전 구현, 장기 DB 저장, 사용자 권한 관리, 실시간 배포 서버 운영은 제외한다.

## 3. 사용자 / 시나리오

사용자는 스마트팩토리 운영자 또는 품질 담당자이다. 사용자는 가상 SMT 라인에 등록된 설비 Instance를 확인하고, 각 설비의 PLC TAG 값이 어떤 AAS OperationData 속성에 연결되는지 확인한다. 가상 제품이 `ScreenPrinter -> SPI -> Mounter -> Reflow -> AOI -> ICT` 순서로 생산되면, 시스템은 PCB Barcode, LotID, WorkOrderID와 함께 각 공정의 설비 상태값을 기록한다. AOI 또는 ICT에서 불량이 발생하면 사용자는 해당 PCB Barcode를 선택해 이전 공정의 온도, 압력, 전력, 검사 결과, 설비 상태를 추적한다.

## 4. 입력 / 출력

입력 데이터는 가상 SMT 라인 설정, 설비 AAS Type 정의, 설비 Instance 목록, PLC TAG 매핑 정보, 가상 PLC TAG 값, 가상 생산 제품 정보이다. 설비 Type은 `ScreenPrinter`, `SPI`, `Mounter`, `Reflow`, `AOI`, `ICT`로 구성하며, 기존 `SMT AAS` 폴더의 AASX 자료를 참고한다.

출력 데이터는 설비별 현재 상태 대시보드, PLC TAG-AAS 속성 매핑표, 제품별 공정 통과 이력, 공정별 설비 데이터 스냅샷, 불량 제품 추적 결과이다. 불량 추적 결과에는 PCB Barcode, LotID, 불량 발생 공정, 불량 유형, 그리고 이전 공정에서 수집된 주요 설비 데이터가 포함된다.

## 5. 핵심 기능 (MVP)

1. AAS Type/Instance 관리
   - SMT 설비별 AAS Type을 정의한다.
   - Type을 참조해 `ScreenPrinter_01`, `SPI_01`, `Mounter_01`, `Reflow_01`, `AOI_01`, `ICT_01` Instance를 생성한다.
   - 각 Instance는 `Identification`, `OperationData`, `ProductionContext`, `QualityResult` 정보를 가진다.

2. PLC TAG와 AAS 속성 매핑
   - 가상 PLC TAG를 설비 Instance의 AAS 속성과 연결한다.
   - 예: `PLC.REFLOW.ZONE1_TEMP` -> `Reflow_01.OperationData.Zone1Temperature`
   - 예: `PLC.AOI.INSPECTION_RESULT` -> `AOI_01.QualityResult.InspectionResult`

3. 가상 SMT 생산 및 불량 추적
   - 가상 PCB가 SMT 공정을 순서대로 통과하도록 시뮬레이션한다.
   - 각 공정 통과 시점의 설비 데이터 스냅샷을 PCB Barcode 기준으로 저장한다.
   - 불량 발생 시 해당 제품의 이전 공정 데이터와 검사 결과를 조회한다.

## 6. 비기능 / 제약

프로토타입은 Python 기반 로컬 실행을 기본으로 한다. 데이터는 실제 PLC가 아닌 시뮬레이션 데이터로 생성하며, 필요 시 CSV 또는 JSON 파일로 저장한다. 화면은 간단한 웹 대시보드 또는 콘솔 기반 결과 출력으로 구현할 수 있다. 외부 네트워크로 실제 생산 데이터나 민감 정보를 전송하지 않는다. AAS 표준은 개념과 구조를 참고하되, 과제 범위에서는 완전한 AASX 패키지 생성이 아니라 학습용 데이터 모델로 단순화한다.

## 7. 성공 기준

프로그램 실행 시 가상 SMT 설비 Instance가 생성되고, PLC TAG 매핑 정보가 확인되어야 한다. 가상 PCB 제품이 라인을 통과하면서 공정별 설비 데이터가 기록되어야 한다. AOI 또는 ICT에서 불량 제품이 발생했을 때 PCB Barcode 기준으로 이전 공정의 설비 데이터와 품질 결과를 조회할 수 있어야 한다. 최종 보고서에는 AAS Type/Instance 구조, PLC TAG 매핑 방식, 제품 추적 데이터 구조, 불량 추적 예시 결과가 포함되어야 한다.
