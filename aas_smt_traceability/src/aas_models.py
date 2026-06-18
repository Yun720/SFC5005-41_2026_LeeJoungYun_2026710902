"""
aas_models.py
AAS Type / Instance / PLC 매핑 / PCB / 공정 스냅샷 데이터 모델 정의
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


# ─────────────────────────────────────────
# AAS Type: 설비 종류별 템플릿
# ─────────────────────────────────────────
@dataclass
class EquipmentAASType:
    type_id: str                        # 예: "TYPE_SCREEN_PRINTER"
    type_name: str                      # 예: "ScreenPrinter"
    process_name: str                   # 예: "SolderPaste"
    operation_fields: List[str]         # OperationData에 포함될 필드 목록
    quality_fields: List[str]           # QualityResult에 포함될 필드 목록


# ─────────────────────────────────────────
# AAS Instance: 실제 설비 인스턴스
# ─────────────────────────────────────────
@dataclass
class EquipmentAASInstance:
    instance_id: str                            # 예: "ScreenPrinter_01"
    type_id: str                                # 참조하는 AAS Type ID
    display_name: str                           # 화면 표시명
    identification: Dict[str, str]              # 제조사, 시리얼 등 식별 정보
    operation_data: Dict[str, Any] = field(default_factory=dict)   # 실시간 운전 데이터
    production_context: Dict[str, Any] = field(default_factory=dict)  # 생산 컨텍스트
    quality_result: Dict[str, Any] = field(default_factory=dict)   # 품질 결과


# ─────────────────────────────────────────
# PLC TAG 매핑: PLC 태그 ↔ AAS 속성 경로
# ─────────────────────────────────────────
@dataclass
class PLCTagMapping:
    plc_tag: str                    # 예: "PLC.PRINTER.TEMP"
    equipment_instance_id: str      # 예: "ScreenPrinter_01"
    aas_path: str                   # 예: "OperationData.Temp"
    data_type: str                  # "float", "int", "str", "bool"
    unit: str = ""                  # 예: "°C", "mm", "%"


# ─────────────────────────────────────────
# 가상 PCB 제품
# ─────────────────────────────────────────
@dataclass
class ProductPCB:
    pcb_barcode: str                # 예: "PCB-0001"
    lot_id: str                     # 예: "LOT-2026-001"
    work_order_id: str              # 예: "WO-2026-0618-01"
    model_name: str                 # 예: "MODEL-A"
    current_process: str = "READY"  # 현재 공정 위치
    final_result: str = "PENDING"   # "PASS" / "FAIL" / "PENDING"


# ─────────────────────────────────────────
# 공정 스냅샷: 제품이 설비를 통과한 순간의 기록
# ─────────────────────────────────────────
@dataclass
class ProcessSnapshot:
    pcb_barcode: str
    lot_id: str
    work_order_id: str
    process_name: str               # 예: "AOI"
    equipment_instance_id: str      # 예: "AOI_01"
    timestamp: str                  # ISO 형식 타임스탬프
    operation_data: Dict[str, Any] = field(default_factory=dict)
    quality_result: Dict[str, Any] = field(default_factory=dict)
