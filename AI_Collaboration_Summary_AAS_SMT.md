# AI 도구 활용 및 프로젝트 기획 과정 정리

## 1. 프로젝트 주제

이번 최종 프로젝트의 주제는 **AAS 기반 가상 SMT 라인의 PLC TAG 매핑 및 불량 추적 모니터링 시스템**이다.

스마트팩토리 SMT 라인에서 설비 PLC TAG 데이터를 단순히 수집하는 것에 그치지 않고, 설비 데이터를 AAS(Asset Administration Shell) 형태로 구조화하여 관리하는 것을 목표로 한다. 설비 AAS는 Type과 Instance로 나누어 구성하고, 설비 Instance AAS의 속성값과 PLC TAG를 매핑한다. 이후 가상 SMT 라인에서 제품이 생산되는 과정을 시뮬레이션하고, 제품별 생산 이력과 설비 데이터를 함께 저장하여 불량 발생 시 원인을 추적할 수 있도록 한다.

## 2. 주제 선정 과정

처음에는 Week14 강의자료에 맞춰 `13 Examples` 폴더의 스마트공장 사업계획서를 참고해 과제 주제를 정하려고 했다. 사업계획서들을 확인한 결과 대부분 MES, LOT 추적, 설비 모니터링, 품질 이력 관리와 관련된 내용이었다.

하지만 단순히 예시 문서에서 주제를 고르는 것보다, 직접 관심 있는 방향을 바탕으로 주제를 정하기로 했다. 이에 따라 **설비 PLC에서 데이터를 취득하고, 이를 AAS 기반으로 관리하며, 최종적으로 모니터링하는 프로그램**을 만들고자 하는 방향을 세웠다.

이후 주제를 더 구체화하면서 다음 요구사항을 정리했다.

- 설비 데이터를 AAS 형태로 묶어 관리한다.
- 설비 AAS는 Type과 Instance 구조로 관리한다.
- 설비 Type AAS를 참조해 설비 Instance AAS를 생성한다.
- 설비의 PLC TAG와 설비 Instance AAS의 속성값을 매핑한다.
- 가상의 SMT 라인을 구성한다.
- 가상의 제품이 SMT 라인을 통과하며 생산되는 흐름을 만든다.
- 제품 생산 이력과 설비 데이터(온도, 압력, 전력 등)를 함께 저장한다.
- 불량 발생 시 해당 제품의 이전 공정 데이터를 추적할 수 있도록 한다.

## 3. 참고 자료 확인

프로젝트 방향을 구체화하기 위해 `SMT AAS` 폴더에 있는 자료를 확인했다. 해당 폴더에는 SMT 주요 설비별 AASX 파일과 가이던스 문서가 포함되어 있었다.

확인한 설비 AASX 파일은 다음과 같다.

- `ScreenPrinter_v3.aasx`
- `SPI_v3.aasx`
- `Mounter_v3.aasx`
- `Reflow_v3.aasx`
- `AOI_v3.aasx`
- `ICT_v3.aasx`

각 AASX에는 공통적으로 `DigitalNameplate`, `TechnicalData`, `OperationData`, `Identification` 등의 Submodel이 포함되어 있었다. 특히 `OperationData`에는 실제 모니터링과 추적에 활용할 수 있는 항목들이 포함되어 있었다.

예를 들어 다음과 같은 데이터 항목을 확인했다.

- `PCBBarcode`
- `LotID`
- `WorkOrderID`
- `InspectionResult`
- `RecipeID`
- `MeasureValue`
- `Temp`
- `Humidity`
- `PowerConsumption`
- `DefectType`
- `InterlockAction`

이를 바탕으로 본 프로젝트에서는 기존 SMT AAS 자료를 참고하되, 실제 AASX 표준 전체를 구현하기보다는 학습용 프로토타입에 맞게 단순화된 AAS 데이터 모델을 설계하기로 했다.

## 4. 최종 프로젝트 범위 조정

처음 아이디어에는 실제 PLC 데이터 취득, AASX 파일 관리, Type/Instance AAS 관리, 설비 모니터링, 가상 생산 시뮬레이션이 모두 포함되어 있었다. 그러나 과제 범위와 구현 가능성을 고려해 MVP 범위를 다음과 같이 조정했다.

### 포함할 기능

1. AAS Type/Instance 관리
   - SMT 설비별 Type 정의
   - Type을 참조한 설비 Instance 생성
   - Instance별 OperationData, ProductionContext, QualityResult 관리

2. PLC TAG와 AAS 속성 매핑
   - 가상 PLC TAG와 AAS 속성 경로 연결
   - 예: `PLC.REFLOW.ZONE1_TEMP -> Reflow_01.OperationData.Zone1Temperature`

3. 가상 SMT 생산 및 불량 추적
   - 가상 PCB가 `ScreenPrinter -> SPI -> Mounter -> Reflow -> AOI -> ICT` 순서로 이동
   - 각 공정 통과 시점의 설비 데이터 스냅샷 저장
   - AOI 또는 ICT에서 불량 발생 시 PCB Barcode 기준으로 이전 공정 데이터 조회

### 제외할 기능

- 실제 PLC 통신
- OPC UA, Modbus, Ethernet/IP 등 산업용 통신 구현
- 실제 AASX 파일 생성
- BaSyx 등 외부 AAS 플랫폼 연동
- 사용자 로그인/권한 관리
- 장기 데이터베이스 운영
- 클라우드 배포
- 복잡한 3D 시각화

이렇게 범위를 조정함으로써, 기술적으로는 AAS 기반 스마트팩토리 데이터 관리 개념을 보여주면서도 과제 기간 안에 구현 가능한 수준으로 프로젝트를 정리했다.

## 5. 작성한 산출물

AI 도구와의 대화를 통해 다음 산출물을 작성했다.

1. **PRD 문서**
   - 파일명: `PRD_AAS_SMT_Traceability.md`
   - 내용: 프로젝트 문제 정의, 목표, 범위, 사용자 시나리오, 입력/출력, 핵심 기능, 제약, 성공 기준

2. **PRD PDF**
   - 파일명: `PRD_AAS_SMT_Traceability.pdf`
   - 내용: 제출용으로 정리한 PRD PDF 문서

3. **Claude 구현 요청서**
   - 파일명: `Claude_Implementation_Brief_AAS_SMT.md`
   - 내용: Claude로 프로토타입을 구현할 수 있도록 데이터 모델, 실행 흐름, 추천 폴더 구조, 구현 제외 범위, 기대 출력 예시를 정리한 문서

## 6. AI 도구 활용 방식

이번 기획 과정에서 AI 도구는 다음 역할로 활용했다.

- Week14 강의자료의 과제 요구사항 확인
- `13 Examples` 폴더의 사업계획서 내용 검토
- PRD 개념 설명
- 프로젝트 주제 구체화
- SMT AAS 자료 구조 확인
- AAS Type/Instance와 PLC TAG 매핑 구조 정리
- 제품 생산 이력과 설비 데이터 추적 구조 설계
- PRD 문서 작성
- PRD PDF 변환
- Claude 구현 요청서 작성
- 제출용 대화 및 기획 과정 요약

AI가 프로젝트 방향을 대신 결정한 것이 아니라, 사용자가 제시한 아이디어를 바탕으로 과제 범위에 맞게 정리하고, 구현 가능한 MVP 형태로 줄이는 데 활용했다.

## 7. 배운 점

이번 기획 과정을 통해 스마트팩토리 프로젝트에서는 단순히 데이터를 수집하는 것보다 **데이터의 의미와 관계를 어떻게 구조화할 것인지**가 중요하다는 점을 확인했다.

PLC TAG는 실제 설비 데이터를 나타내지만, TAG 이름만으로는 데이터의 의미, 단위, 제품 이력과의 관계를 파악하기 어렵다. AAS 기반 구조를 적용하면 설비 Type, 설비 Instance, OperationData, 품질 결과, 제품 이력을 연결할 수 있으며, 이는 불량 추적과 공정 분석에 유용하다.

또한 프로젝트 범위를 정할 때 실제 산업 표준 전체를 구현하려고 하기보다, 핵심 개념을 보여줄 수 있는 MVP를 먼저 만드는 것이 중요하다는 점을 알게 되었다.

## 8. 앞으로의 질문

프로토타입 구현을 진행하면서 추가로 확인하고 싶은 질문은 다음과 같다.

1. AAS Type과 Instance를 코드에서 어떤 구조로 표현하는 것이 가장 이해하기 쉬운가?
2. PLC TAG와 AAS 속성 매핑 정보를 JSON으로 관리할 때 어떤 필드를 포함해야 추후 확장성이 좋은가?
3. 불량 추적 결과를 콘솔 출력에서 웹 대시보드로 확장하려면 어떤 데이터 구조를 미리 준비해야 하는가?

## 9. 최종 정리

최종 프로젝트는 **AAS 기반으로 SMT 설비 데이터를 구조화하고, PLC TAG와 제품 생산 이력을 연결하여 불량 발생 시 원인을 추적할 수 있는 가상 모니터링 프로토타입**으로 진행한다.

이번 단계에서는 실제 PLC 연결이나 완전한 AASX 구현보다, AAS 개념을 반영한 데이터 모델과 제품 추적 흐름을 명확히 구현하는 것을 우선 목표로 한다. 이후 구현 단계에서는 Claude를 활용해 Python 기반 프로젝트 뼈대와 가상 생산 시뮬레이션 코드를 생성하고, 실행 결과를 바탕으로 기술보고서를 작성할 예정이다.
