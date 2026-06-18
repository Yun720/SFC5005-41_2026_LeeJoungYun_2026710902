"""
plc_mapping.py
PLC TAG ↔ AAS 속성 경로 매핑 테이블 정의 및 저장/로드
"""

import json
from pathlib import Path
from src.aas_models import PLCTagMapping


# ─────────────────────────────────────────
# 매핑 테이블 생성
# ─────────────────────────────────────────
def create_plc_mappings() -> list[PLCTagMapping]:
    mappings = [
        # ScreenPrinter
        PLCTagMapping("PLC.PRINTER.TEMP",             "ScreenPrinter_01", "OperationData.Temp",             "float", "°C"),
        PLCTagMapping("PLC.PRINTER.HUMIDITY",         "ScreenPrinter_01", "OperationData.Humidity",         "float", "%"),
        PLCTagMapping("PLC.PRINTER.SQUEEGEE_PRESSURE","ScreenPrinter_01", "OperationData.SqueegeePressure", "float", "MPa"),
        PLCTagMapping("PLC.PRINTER.SQUEEGEE_SPEED",   "ScreenPrinter_01", "OperationData.SqueegeeSpeed",    "float", "mm/s"),
        PLCTagMapping("PLC.PRINTER.PASTE_ID",         "ScreenPrinter_01", "OperationData.PasteID",          "str",   ""),
        PLCTagMapping("PLC.PRINTER.STENCIL_ID",       "ScreenPrinter_01", "OperationData.StencilID",        "str",   ""),
        PLCTagMapping("PLC.PRINTER.CYCLE_TIME",       "ScreenPrinter_01", "OperationData.CycleTime",        "float", "s"),
        # SPI
        PLCTagMapping("PLC.SPI.INSPECTION_RESULT",    "SPI_01", "QualityResult.InspectionResult", "str",   ""),
        PLCTagMapping("PLC.SPI.SOLDER_VOLUME",        "SPI_01", "QualityResult.SolderVolume",     "float", "%"),
        PLCTagMapping("PLC.SPI.SOLDER_HEIGHT",        "SPI_01", "QualityResult.SolderHeight",     "float", "mm"),
        PLCTagMapping("PLC.SPI.OFFSET_X",             "SPI_01", "QualityResult.OffsetX",          "float", "mm"),
        PLCTagMapping("PLC.SPI.OFFSET_Y",             "SPI_01", "QualityResult.OffsetY",          "float", "mm"),
        PLCTagMapping("PLC.SPI.DEFECT_TYPE",          "SPI_01", "QualityResult.DefectType",       "str",   ""),
        # Mounter
        PLCTagMapping("PLC.MOUNTER.PLACEMENT_SPEED",  "Mounter_01", "OperationData.PlacementSpeed",  "float", "cph"),
        PLCTagMapping("PLC.MOUNTER.MOUNT_CT",         "Mounter_01", "OperationData.MountCT",         "float", "s"),
        PLCTagMapping("PLC.MOUNTER.PICKUP_ERROR",     "Mounter_01", "OperationData.PickupError",     "int",   ""),
        PLCTagMapping("PLC.MOUNTER.PARTS_VISION_ERR", "Mounter_01", "OperationData.PartsVisionError","int",   ""),
        PLCTagMapping("PLC.MOUNTER.PRODUCED_BOARDS",  "Mounter_01", "OperationData.ProducedBoards",  "int",   ""),
        PLCTagMapping("PLC.MOUNTER.WORKING_RATIO",    "Mounter_01", "OperationData.WorkingRatio",    "float", "%"),
        # Reflow
        PLCTagMapping("PLC.REFLOW.ZONE1_TEMP",        "Reflow_01", "OperationData.Zone1Temperature", "float", "°C"),
        PLCTagMapping("PLC.REFLOW.ZONE2_TEMP",        "Reflow_01", "OperationData.Zone2Temperature", "float", "°C"),
        PLCTagMapping("PLC.REFLOW.ZONE3_TEMP",        "Reflow_01", "OperationData.Zone3Temperature", "float", "°C"),
        PLCTagMapping("PLC.REFLOW.CONVEYOR_SPEED",    "Reflow_01", "OperationData.ConveyorSpeed",    "float", "cm/min"),
        PLCTagMapping("PLC.REFLOW.OXYGEN_LEVEL",      "Reflow_01", "OperationData.OxygenLevel",      "float", "ppm"),
        PLCTagMapping("PLC.REFLOW.POWER_CONSUMPTION", "Reflow_01", "OperationData.PowerConsumption", "float", "kW"),
        # AOI
        PLCTagMapping("PLC.AOI.INSPECTION_RESULT",    "AOI_01", "QualityResult.InspectionResult", "str",   ""),
        PLCTagMapping("PLC.AOI.DEFECT_TYPE",          "AOI_01", "QualityResult.DefectType",       "str",   ""),
        PLCTagMapping("PLC.AOI.DEFECT_LOCATION",      "AOI_01", "QualityResult.DefectLocation",   "str",   ""),
        PLCTagMapping("PLC.AOI.MEASURE_VALUE",        "AOI_01", "QualityResult.MeasureValue",     "float", "mm"),
        PLCTagMapping("PLC.AOI.REVIEW_RESULT",        "AOI_01", "QualityResult.ReviewResult",     "str",   ""),
        # ICT
        PLCTagMapping("PLC.ICT.INSPECTION_RESULT",    "ICT_01", "QualityResult.InspectionResult", "str",   ""),
        PLCTagMapping("PLC.ICT.TEST_VOLTAGE",         "ICT_01", "QualityResult.TestVoltage",      "float", "V"),
        PLCTagMapping("PLC.ICT.TEST_CURRENT",         "ICT_01", "QualityResult.TestCurrent",      "float", "mA"),
        PLCTagMapping("PLC.ICT.DEFECT_TYPE",          "ICT_01", "QualityResult.DefectType",       "str",   ""),
        PLCTagMapping("PLC.ICT.ACTUAL_VALUE",         "ICT_01", "QualityResult.ActualValue",      "float", ""),
        PLCTagMapping("PLC.ICT.STANDARD_VALUE",       "ICT_01", "QualityResult.StandardValue",    "float", ""),
    ]
    return mappings


def save_mappings_to_json(mappings: list[PLCTagMapping], path: str) -> None:
    """매핑 테이블을 JSON 파일로 저장"""
    data = [m.__dict__ for m in mappings]
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_mappings_from_json(path: str) -> list[PLCTagMapping]:
    """JSON 파일에서 매핑 테이블 로드"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [PLCTagMapping(**d) for d in data]


def build_tag_index(mappings: list[PLCTagMapping]) -> dict[str, PLCTagMapping]:
    """PLC 태그 이름으로 빠르게 조회하기 위한 인덱스"""
    return {m.plc_tag: m for m in mappings}
