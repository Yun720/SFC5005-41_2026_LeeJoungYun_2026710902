# Claude 구현 요청서: AAS 기반 가상 SMT 라인 모니터링 프로토타입

아래 내용을 기준으로 Python 기반 프로토타입의 프로젝트 구조와 뼈대 코드를 만들어주세요. 목표는 실제 PLC나 실제 AASX 서버를 완성하는 것이 아니라, AAS 개념을 적용한 가상 SMT 라인의 PLC TAG 매핑, 생산 이력 수집, 불량 추적 모니터링 흐름을 학습용 MVP로 구현하는 것입니다.

## 1. 프로젝트 주제

**AAS 기반 가상 SMT 라인의 PLC TAG 매핑 및 불량 추적 모니터링 시스템**

스마트팩토리 SMT 라인에서 설비 PLC TAG 데이터를 AAS(Asset Administration Shell) 형태의 설비 Instance 데이터와 연결하고, 가상 제품이 공정을 통과할 때 설비 상태값과 품질 결과를 PCB Barcode 기준으로 저장합니다. AOI 또는 ICT에서 불량이 발생하면 해당 제품이 이전 공정에서 어떤 설비 데이터 조건을 거쳤는지 추적할 수 있어야 합니다.

## 2. 구현 목표

다음 3가지 기능이 동작하는 최소 프로토타입을 만들어주세요.

1. **AAS Type/Instance 관리**
   - SMT 설비 Type을 정의합니다.
   - Type을 참조하여 설비 Instance를 생성합니다.
   - 설비는 `ScreenPrinter`, `SPI`, `Mounter`, `Reflow`, `AOI`, `ICT`를 사용합니다.

2. **PLC TAG와 AAS 속성 매핑**
   - 가상 PLC TAG 값을 설비 Instance의 AAS 속성에 매핑합니다.
   - 예:
     - `PLC.PRINTER.TEMP` -> `ScreenPrinter_01.OperationData.Temp`
     - `PLC.REFLOW.ZONE1_TEMP` -> `Reflow_01.OperationData.Zone1Temperature`
     - `PLC.AOI.INSPECTION_RESULT` -> `AOI_01.QualityResult.InspectionResult`

3. **가상 SMT 생산 및 불량 추적**
   - 가상 PCB 제품이 다음 순서로 이동합니다.
     - `ScreenPrinter -> SPI -> Mounter -> Reflow -> AOI -> ICT`
   - 각 공정 통과 시점의 설비 데이터 스냅샷을 저장합니다.
   - AOI 또는 ICT에서 불량이 발생하면 PCB Barcode 기준으로 이전 공정 데이터를 조회합니다.

## 3. 구현 제외 범위

다음 항목은 이번 MVP에서 구현하지 마세요.

- 실제 PLC 통신
- OPC UA, Modbus, Ethernet/IP 등 실제 산업용 통신
- 실제 AASX 파일 생성 또는 AAS 서버 연동
- BaSyx 등 외부 AAS 플랫폼 연동
- 사용자 로그인/권한 관리
- 장기 데이터베이스 운영
- 클라우드 배포
- 복잡한 3D 시각화

필요하면 JSON/CSV 파일 저장 정도만 사용하고, 기본은 로컬 실행 가능한 구조로 작성해주세요.

## 4. 추천 기술 스택

가능하면 다음 중 하나로 구현해주세요.

- Python 3
- 데이터 모델: `dataclasses` 또는 `pydantic`
- 저장 방식: 메모리 기반, 필요 시 JSON 저장
- UI: 우선 콘솔 출력으로 가능
- 시간이 되면 Streamlit 대시보드 구조까지 확장 가능하도록 설계

처음에는 콘솔 기반 프로토타입으로 충분합니다. 다만 나중에 웹 대시보드로 확장하기 쉽게 모듈을 분리해주세요.

## 5. 핵심 데이터 모델

다음 개념을 코드에 반영해주세요.

### AAS Type

설비 종류별 템플릿입니다.

예:

```text
EquipmentAASType
- type_id
- type_name
- process_name
- operation_fields
- quality_fields
```

### AAS Instance

실제 설비 Instance입니다.

예:

```text
EquipmentAASInstance
- instance_id
- type_id
- display_name
- identification
- operation_data
- production_context
- quality_result
```

### PLC TAG Mapping

PLC TAG와 AAS 속성 경로의 연결 정보입니다.

예:

```text
PLCTagMapping
- plc_tag
- equipment_instance_id
- aas_path
- data_type
- unit
```

### Product / PCB

가상 생산되는 제품입니다.

예:

```text
ProductPCB
- pcb_barcode
- lot_id
- work_order_id
- model_name
- current_process
- final_result
```

### Process Snapshot

제품이 특정 설비를 통과한 순간의 데이터입니다.

예:

```text
ProcessSnapshot
- pcb_barcode
- lot_id
- work_order_id
- process_name
- equipment_instance_id
- timestamp
- operation_data
- quality_result
```

## 6. 설비별 예시 데이터

각 설비는 다음 정도의 데이터를 가지면 됩니다.

### ScreenPrinter

- `Temp`
- `Humidity`
- `SqueegeePressure`
- `SqueegeeSpeed`
- `PasteID`
- `StencilID`
- `CycleTime`

### SPI

- `InspectionResult`
- `SolderVolume`
- `SolderHeight`
- `OffsetX`
- `OffsetY`
- `DefectType`

### Mounter

- `PlacementSpeed`
- `MountCT`
- `PickupError`
- `PartsVisionError`
- `ProducedBoards`
- `WorkingRatio`

### Reflow

- `Zone1Temperature`
- `Zone2Temperature`
- `Zone3Temperature`
- `ConveyorSpeed`
- `OxygenLevel`
- `PowerConsumption`

### AOI

- `InspectionResult`
- `DefectType`
- `DefectLocation`
- `MeasureValue`
- `ReviewResult`

### ICT

- `InspectionResult`
- `TestVoltage`
- `TestCurrent`
- `DefectType`
- `ActualValue`
- `StandardValue`

## 7. 프로그램 실행 흐름

다음 흐름으로 동작하는 샘플 실행 코드를 만들어주세요.

1. SMT 설비 Type을 생성합니다.
2. 설비 Instance를 생성합니다.
3. PLC TAG 매핑 테이블을 생성합니다.
4. 가상 PLC TAG 값을 생성합니다.
5. 가상 PCB 제품 5~10개를 생성합니다.
6. 각 PCB가 SMT 라인을 순서대로 통과합니다.
7. 각 공정에서 설비 데이터 스냅샷을 저장합니다.
8. 일부 PCB는 AOI 또는 ICT에서 불량으로 판정합니다.
9. 불량 PCB를 선택해 이전 공정 데이터를 추적 출력합니다.

## 8. 기대 출력 예시

콘솔 출력은 다음 내용을 포함하면 됩니다.

```text
=== Equipment Instances ===
ScreenPrinter_01 / SPI_01 / Mounter_01 / Reflow_01 / AOI_01 / ICT_01

=== PLC TAG Mappings ===
PLC.REFLOW.ZONE1_TEMP -> Reflow_01.OperationData.Zone1Temperature
PLC.AOI.INSPECTION_RESULT -> AOI_01.QualityResult.InspectionResult

=== Production Result ===
PCB-0001 PASS
PCB-0002 PASS
PCB-0003 FAIL at AOI

=== Trace Result: PCB-0003 ===
ScreenPrinter_01: Temp=24.1, Humidity=45.0, SqueegeePressure=0.32
SPI_01: SolderVolume=82.5, SolderHeight=0.12, InspectionResult=PASS
Mounter_01: PickupError=1, PartsVisionError=0
Reflow_01: Zone1Temperature=145.2, Zone2Temperature=178.3, PowerConsumption=4.8
AOI_01: InspectionResult=FAIL, DefectType=Misalignment
```

## 9. 추천 폴더 구조

다음 구조로 만들어주세요.

```text
aas_smt_traceability/
  README.md
  requirements.txt
  main.py
  src/
    aas_models.py
    equipment_factory.py
    plc_mapping.py
    virtual_plc.py
    production_simulator.py
    traceability.py
  data/
    sample_mappings.json
  tests/
    test_traceability.py
```

## 10. 코드 작성 지침

- 처음부터 너무 복잡하게 만들지 마세요.
- 실제 산업 표준 전체 구현보다 학습용 구조가 명확해야 합니다.
- 각 파일과 클래스의 역할을 주석으로 짧게 설명해주세요.
- `main.py`를 실행하면 전체 데모가 한 번에 돌아가야 합니다.
- 외부 패키지는 최소화해주세요.
- 테스트는 최소 1개 이상 작성해주세요.
- README에는 실행 방법과 주요 개념을 설명해주세요.

## 11. 최종 산출물

다음을 생성해주세요.

1. 실행 가능한 Python 프로젝트 뼈대
2. 샘플 가상 데이터
3. `main.py` 실행 데모
4. 불량 PCB 추적 결과 출력
5. 간단한 README
6. 최소 단위 테스트

중요: 이번 단계에서는 완성형 대시보드보다, 데이터 구조와 추적 흐름이 명확하게 작동하는 프로토타입을 우선으로 해주세요.
