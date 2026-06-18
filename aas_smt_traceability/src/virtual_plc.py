"""
virtual_plc.py
가상 PLC TAG 값 생성기 - 실제 PLC 대신 랜덤 범위 값으로 시뮬레이션
"""

import random
from src.aas_models import EquipmentAASInstance
from src.plc_mapping import PLCTagMapping


# 각 PLC 태그에 대한 정상 범위 정의
_TAG_RANGES: dict[str, tuple] = {
    # ScreenPrinter
    "PLC.PRINTER.TEMP":              (22.0,  26.0),
    "PLC.PRINTER.HUMIDITY":          (40.0,  55.0),
    "PLC.PRINTER.SQUEEGEE_PRESSURE": (0.28,  0.38),
    "PLC.PRINTER.SQUEEGEE_SPEED":    (30.0,  60.0),
    "PLC.PRINTER.PASTE_ID":          ("PASTE-A", "PASTE-B"),
    "PLC.PRINTER.STENCIL_ID":        ("STENCIL-001",),
    "PLC.PRINTER.CYCLE_TIME":        (18.0,  24.0),
    # SPI
    "PLC.SPI.SOLDER_VOLUME":         (75.0,  95.0),
    "PLC.SPI.SOLDER_HEIGHT":         (0.10,  0.15),
    "PLC.SPI.OFFSET_X":              (-0.05, 0.05),
    "PLC.SPI.OFFSET_Y":              (-0.05, 0.05),
    # Mounter
    "PLC.MOUNTER.PLACEMENT_SPEED":   (25000, 35000),
    "PLC.MOUNTER.MOUNT_CT":          (8.0,   12.0),
    "PLC.MOUNTER.PICKUP_ERROR":      (0,     2),
    "PLC.MOUNTER.PARTS_VISION_ERR":  (0,     1),
    "PLC.MOUNTER.PRODUCED_BOARDS":   (100,   500),
    "PLC.MOUNTER.WORKING_RATIO":     (90.0,  98.0),
    # Reflow
    "PLC.REFLOW.ZONE1_TEMP":         (140.0, 155.0),
    "PLC.REFLOW.ZONE2_TEMP":         (170.0, 185.0),
    "PLC.REFLOW.ZONE3_TEMP":         (240.0, 260.0),
    "PLC.REFLOW.CONVEYOR_SPEED":     (55.0,  75.0),
    "PLC.REFLOW.OXYGEN_LEVEL":       (500,   1500),
    "PLC.REFLOW.POWER_CONSUMPTION":  (4.0,   6.0),
    # ICT
    "PLC.ICT.TEST_VOLTAGE":          (3.2,   3.4),
    "PLC.ICT.TEST_CURRENT":          (95.0,  105.0),
    "PLC.ICT.ACTUAL_VALUE":          (98.0,  102.0),
    "PLC.ICT.STANDARD_VALUE":        (100.0, 100.0),
}

_DEFECT_TYPES_AOI = ["Misalignment", "BridgeSolder", "MissingPart", "TombStoning"]
_DEFECT_TYPES_SPI = ["InsufficientSolder", "ExcessSolder", "Offset"]
_DEFECT_TYPES_ICT = ["OpenCircuit", "ShortCircuit", "WrongComponent"]


def _random_value(tag: str, data_type: str) -> object:
    """태그 이름과 타입에 따라 랜덤 값 생성"""
    rng = _TAG_RANGES.get(tag)
    if rng is None:
        return None
    if data_type == "str":
        return random.choice(rng)
    if data_type == "int":
        return random.randint(int(rng[0]), int(rng[1]))
    # float
    return round(random.uniform(rng[0], rng[1]), 3)


def generate_plc_values(mappings: list[PLCTagMapping]) -> dict[str, object]:
    """모든 PLC 태그에 대해 가상 값 딕셔너리 반환"""
    values: dict[str, object] = {}
    for m in mappings:
        values[m.plc_tag] = _random_value(m.plc_tag, m.data_type)
    return values


def apply_plc_to_instance(
    plc_values: dict[str, object],
    mappings: list[PLCTagMapping],
    instances: dict[str, EquipmentAASInstance],
) -> None:
    """PLC 값을 AAS Instance의 해당 속성에 기록"""
    for m in mappings:
        inst = instances.get(m.equipment_instance_id)
        if inst is None:
            continue
        value = plc_values.get(m.plc_tag)
        # aas_path 예: "OperationData.Temp" or "QualityResult.InspectionResult"
        section, _, field_name = m.aas_path.partition(".")
        if section == "OperationData":
            inst.operation_data[field_name] = value
        elif section == "QualityResult":
            inst.quality_result[field_name] = value


def set_inspection_result(
    instance: EquipmentAASInstance,
    result: str,
    defect_type: str = "",
    extra: dict | None = None,
) -> None:
    """검사 설비(SPI/AOI/ICT)의 판정 결과를 직접 설정"""
    instance.quality_result["InspectionResult"] = result
    if defect_type:
        instance.quality_result["DefectType"] = defect_type
    if extra:
        instance.quality_result.update(extra)
