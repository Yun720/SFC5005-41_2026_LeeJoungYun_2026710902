# AAS 기반 가상 SMT 라인 모니터링 프로토타입

AAS(Asset Administration Shell) 개념을 적용하여 SMT 라인의  
PLC TAG 매핑, 생산 이력 수집, 불량 PCB 추적 흐름을 시뮬레이션하는 학습용 MVP입니다.

---

## 실행 방법

```bash
# 프로젝트 루트에서
python main.py

# 테스트 실행
python -m pytest tests/ -v
# 또는 (pytest 미설치 시)
python -m unittest tests/test_traceability.py -v
```

Python 3.10 이상 권장. 외부 패키지 설치 불필요.

---

## 폴더 구조

```
aas_smt_traceability/
  main.py                    진입점 — 전체 데모 한 번에 실행
  requirements.txt
  src/
    aas_models.py            핵심 데이터 모델 (dataclass)
    equipment_factory.py     AAS Type / Instance 생성
    plc_mapping.py           PLC TAG ↔ AAS 속성 매핑 테이블
    virtual_plc.py           가상 PLC 값 생성 및 Instance 반영
    production_simulator.py  SMT 라인 시뮬레이션 및 스냅샷 수집
    traceability.py          불량 PCB 추적·출력
  data/
    sample_mappings.json     실행 후 자동 생성되는 매핑 테이블 JSON
  tests/
    test_traceability.py     단위 테스트
```

---

## 주요 개념

| 개념 | 설명 |
|---|---|
| **AAS Type** | 설비 종류 템플릿 (ScreenPrinter, SPI, Mounter, Reflow, AOI, ICT) |
| **AAS Instance** | 실제 설비 1대. Type을 참조해 생성 |
| **PLC TAG Mapping** | `PLC.REFLOW.ZONE1_TEMP` → `Reflow_01.OperationData.Zone1Temperature` |
| **ProductPCB** | 가상 PCB 제품. 바코드 기준으로 추적 |
| **ProcessSnapshot** | 제품이 설비를 통과한 순간의 운전·품질 데이터 스냅샷 |

---

## SMT 라인 공정 순서

```
ScreenPrinter → SPI → Mounter → Reflow → AOI → ICT
```

AOI 또는 ICT에서 불량 판정된 PCB는 바코드 기준으로  
이전 모든 공정의 스냅샷 데이터를 조회할 수 있습니다.

---

## 확장 계획

- `streamlit`을 추가하면 `main.py`의 출력을 웹 대시보드로 전환 가능
- 각 모듈이 독립적으로 분리되어 있어 OPC UA / DB 연동으로 교체 용이
