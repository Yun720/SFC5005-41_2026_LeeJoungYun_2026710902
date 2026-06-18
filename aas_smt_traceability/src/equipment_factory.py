"""
equipment_factory.py
SMT 라인 설비의 AAS Type 및 Instance를 생성하는 팩토리 모듈
"""

from src.aas_models import EquipmentAASType, EquipmentAASInstance


# ─────────────────────────────────────────
# AAS Type 정의 (설비 종류 템플릿)
# ─────────────────────────────────────────
def create_equipment_types() -> dict[str, EquipmentAASType]:
    types = [
        EquipmentAASType(
            type_id="TYPE_SCREEN_PRINTER",
            type_name="ScreenPrinter",
            process_name="SolderPaste",
            operation_fields=["Temp", "Humidity", "SqueegeePressure", "SqueegeeSpeed",
                              "PasteID", "StencilID", "CycleTime"],
            quality_fields=[],
        ),
        EquipmentAASType(
            type_id="TYPE_SPI",
            type_name="SPI",
            process_name="SolderInspection",
            operation_fields=[],
            quality_fields=["InspectionResult", "SolderVolume", "SolderHeight",
                            "OffsetX", "OffsetY", "DefectType"],
        ),
        EquipmentAASType(
            type_id="TYPE_MOUNTER",
            type_name="Mounter",
            process_name="ComponentPlacement",
            operation_fields=["PlacementSpeed", "MountCT", "PickupError",
                              "PartsVisionError", "ProducedBoards", "WorkingRatio"],
            quality_fields=[],
        ),
        EquipmentAASType(
            type_id="TYPE_REFLOW",
            type_name="Reflow",
            process_name="Reflow",
            operation_fields=["Zone1Temperature", "Zone2Temperature", "Zone3Temperature",
                              "ConveyorSpeed", "OxygenLevel", "PowerConsumption"],
            quality_fields=[],
        ),
        EquipmentAASType(
            type_id="TYPE_AOI",
            type_name="AOI",
            process_name="OpticalInspection",
            operation_fields=[],
            quality_fields=["InspectionResult", "DefectType", "DefectLocation",
                            "MeasureValue", "ReviewResult"],
        ),
        EquipmentAASType(
            type_id="TYPE_ICT",
            type_name="ICT",
            process_name="CircuitTest",
            operation_fields=[],
            quality_fields=["InspectionResult", "TestVoltage", "TestCurrent",
                            "DefectType", "ActualValue", "StandardValue"],
        ),
    ]
    return {t.type_id: t for t in types}


# ─────────────────────────────────────────
# AAS Instance 생성 (실제 설비 1대씩)
# ─────────────────────────────────────────
def create_equipment_instances(types: dict[str, EquipmentAASType]) -> dict[str, EquipmentAASInstance]:
    instances_raw = [
        ("ScreenPrinter_01", "TYPE_SCREEN_PRINTER", "Screen Printer #1",
         {"manufacturer": "DEK", "serial": "SP-001", "line": "SMT-LINE-1"}),
        ("SPI_01", "TYPE_SPI", "SPI #1",
         {"manufacturer": "Koh Young", "serial": "SPI-001", "line": "SMT-LINE-1"}),
        ("Mounter_01", "TYPE_MOUNTER", "Mounter #1",
         {"manufacturer": "Fuji", "serial": "MT-001", "line": "SMT-LINE-1"}),
        ("Reflow_01", "TYPE_REFLOW", "Reflow Oven #1",
         {"manufacturer": "Heller", "serial": "RF-001", "line": "SMT-LINE-1"}),
        ("AOI_01", "TYPE_AOI", "AOI #1",
         {"manufacturer": "Omron", "serial": "AOI-001", "line": "SMT-LINE-1"}),
        ("ICT_01", "TYPE_ICT", "ICT #1",
         {"manufacturer": "Keysight", "serial": "ICT-001", "line": "SMT-LINE-1"}),
    ]

    instances: dict[str, EquipmentAASInstance] = {}
    for instance_id, type_id, display_name, identification in instances_raw:
        t = types[type_id]
        # 필드 목록으로 초기 딕셔너리 생성 (값은 None)
        op_data = {f: None for f in t.operation_fields}
        qr_data = {f: None for f in t.quality_fields}
        instances[instance_id] = EquipmentAASInstance(
            instance_id=instance_id,
            type_id=type_id,
            display_name=display_name,
            identification=identification,
            operation_data=op_data,
            quality_result=qr_data,
        )
    return instances
