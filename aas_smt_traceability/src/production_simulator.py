"""
production_simulator.py
가상 PCB 제품이 SMT 라인을 통과하는 흐름을 시뮬레이션하고
공정 스냅샷을 수집하는 모듈
"""

import copy
import random
from datetime import datetime, timedelta
from src.aas_models import ProductPCB, ProcessSnapshot, EquipmentAASInstance
from src.plc_mapping import PLCTagMapping
from src.virtual_plc import (
    generate_plc_values,
    apply_plc_to_instance,
    set_inspection_result,
    _DEFECT_TYPES_AOI,
    _DEFECT_TYPES_ICT,
    _DEFECT_TYPES_SPI,
)

# SMT 라인 공정 순서 (equipment_instance_id 순서)
SMT_LINE_SEQUENCE = [
    "ScreenPrinter_01",
    "SPI_01",
    "Mounter_01",
    "Reflow_01",
    "AOI_01",
    "ICT_01",
]

# 공정명 매핑
PROCESS_NAME_MAP = {
    "ScreenPrinter_01": "ScreenPrinter",
    "SPI_01":           "SPI",
    "Mounter_01":       "Mounter",
    "Reflow_01":        "Reflow",
    "AOI_01":           "AOI",
    "ICT_01":           "ICT",
}


def create_pcb_products(count: int = 8) -> list[ProductPCB]:
    """가상 PCB 제품 리스트 생성"""
    products = []
    for i in range(1, count + 1):
        products.append(ProductPCB(
            pcb_barcode=f"PCB-{i:04d}",
            lot_id="LOT-2026-001",
            work_order_id="WO-2026-0618-01",
            model_name="MODEL-A",
        ))
    return products


def _make_snapshot(
    pcb: ProductPCB,
    equipment_id: str,
    instance: EquipmentAASInstance,
    base_time: datetime,
    step_index: int,
) -> ProcessSnapshot:
    """현재 Instance 상태로 스냅샷 생성"""
    ts = (base_time + timedelta(minutes=step_index * 3)).isoformat()
    return ProcessSnapshot(
        pcb_barcode=pcb.pcb_barcode,
        lot_id=pcb.lot_id,
        work_order_id=pcb.work_order_id,
        process_name=PROCESS_NAME_MAP[equipment_id],
        equipment_instance_id=equipment_id,
        timestamp=ts,
        operation_data=copy.deepcopy(instance.operation_data),
        quality_result=copy.deepcopy(instance.quality_result),
    )


def run_simulation(
    products: list[ProductPCB],
    instances: dict[str, EquipmentAASInstance],
    mappings: list[PLCTagMapping],
    fail_rate: float = 0.25,
) -> list[ProcessSnapshot]:
    """
    모든 PCB를 SMT 라인에 통과시키고 스냅샷 리스트 반환.
    fail_rate: AOI 또는 ICT에서 불량 판정 확률
    """
    all_snapshots: list[ProcessSnapshot] = []
    base_time = datetime.now()

    for pcb_idx, pcb in enumerate(products):
        pcb_failed = False
        fail_at: str = ""

        # 이 PCB가 AOI/ICT에서 불량이 될지 미리 결정
        will_fail = random.random() < fail_rate
        fail_stage = random.choice(["AOI_01", "ICT_01"]) if will_fail else None

        for step_idx, eq_id in enumerate(SMT_LINE_SEQUENCE):
            inst = instances[eq_id]

            # 각 공정마다 PLC 값을 새로 생성해 Instance에 반영
            plc_values = generate_plc_values(mappings)
            apply_plc_to_instance(plc_values, mappings, instances)

            # 검사 공정의 판정 결과 처리
            if eq_id == "SPI_01":
                result = "FAIL" if (random.random() < 0.1) else "PASS"
                defect = random.choice(_DEFECT_TYPES_SPI) if result == "FAIL" else ""
                set_inspection_result(inst, result, defect,
                                      extra={"DefectLocation": "R12" if defect else ""})
            elif eq_id == "AOI_01":
                if fail_stage == "AOI_01":
                    defect = random.choice(_DEFECT_TYPES_AOI)
                    set_inspection_result(inst, "FAIL", defect,
                                          extra={"DefectLocation": f"U{random.randint(1,20)}",
                                                 "MeasureValue": round(random.uniform(0.0, 0.3), 3),
                                                 "ReviewResult": "CONFIRM"})
                    pcb_failed = True
                    fail_at = "AOI"
                else:
                    set_inspection_result(inst, "PASS", extra={"ReviewResult": "PASS"})
            elif eq_id == "ICT_01":
                if fail_stage == "ICT_01" and not pcb_failed:
                    defect = random.choice(_DEFECT_TYPES_ICT)
                    set_inspection_result(inst, "FAIL", defect,
                                          extra={"ActualValue": round(random.uniform(80, 95), 2),
                                                 "StandardValue": 100.0})
                    pcb_failed = True
                    fail_at = "ICT"
                else:
                    set_inspection_result(inst, "PASS",
                                          extra={"ActualValue": round(random.uniform(98, 102), 2),
                                                 "StandardValue": 100.0})

            snapshot = _make_snapshot(pcb, eq_id, inst, base_time,
                                      pcb_idx * len(SMT_LINE_SEQUENCE) + step_idx)
            all_snapshots.append(snapshot)

        # 최종 판정 업데이트
        if pcb_failed:
            pcb.final_result = f"FAIL at {fail_at}"
            pcb.current_process = fail_at
        else:
            pcb.final_result = "PASS"
            pcb.current_process = "COMPLETE"

    return all_snapshots
