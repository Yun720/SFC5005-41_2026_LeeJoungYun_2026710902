"""
test_traceability.py
핵심 기능에 대한 최소 단위 테스트 (표준 라이브러리 unittest 사용)

실행: python -m pytest tests/ -v
      또는: python -m unittest tests/test_traceability.py -v
"""

import sys
import os
import unittest

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.aas_models import ProductPCB, ProcessSnapshot
from src.equipment_factory import create_equipment_types, create_equipment_instances
from src.plc_mapping import create_plc_mappings, build_tag_index
from src.virtual_plc import generate_plc_values, apply_plc_to_instance
from src.production_simulator import create_pcb_products, run_simulation, SMT_LINE_SEQUENCE
from src.traceability import (
    get_snapshots_by_barcode,
    find_failed_products,
)


class TestEquipmentFactory(unittest.TestCase):
    def setUp(self):
        self.types = create_equipment_types()
        self.instances = create_equipment_instances(self.types)

    def test_type_count(self):
        """6종 설비 Type이 생성되어야 한다"""
        self.assertEqual(len(self.types), 6)

    def test_instance_count(self):
        """6대 설비 Instance가 생성되어야 한다"""
        self.assertEqual(len(self.instances), 6)

    def test_instance_has_correct_fields(self):
        """ScreenPrinter_01은 OperationData에 Temp 필드를 가져야 한다"""
        inst = self.instances["ScreenPrinter_01"]
        self.assertIn("Temp", inst.operation_data)

    def test_aoi_has_quality_fields(self):
        """AOI_01은 QualityResult에 InspectionResult 필드를 가져야 한다"""
        inst = self.instances["AOI_01"]
        self.assertIn("InspectionResult", inst.quality_result)


class TestPLCMapping(unittest.TestCase):
    def setUp(self):
        self.mappings = create_plc_mappings()
        self.index = build_tag_index(self.mappings)

    def test_mapping_count(self):
        """총 매핑 수는 30개 이상이어야 한다"""
        self.assertGreaterEqual(len(self.mappings), 30)

    def test_tag_index_lookup(self):
        """특정 태그를 인덱스에서 조회할 수 있어야 한다"""
        m = self.index["PLC.REFLOW.ZONE1_TEMP"]
        self.assertEqual(m.equipment_instance_id, "Reflow_01")
        self.assertEqual(m.aas_path, "OperationData.Zone1Temperature")

    def test_aoi_result_mapping(self):
        """AOI 검사 결과 태그가 QualityResult에 매핑되어야 한다"""
        m = self.index["PLC.AOI.INSPECTION_RESULT"]
        self.assertTrue(m.aas_path.startswith("QualityResult"))


class TestVirtualPLC(unittest.TestCase):
    def setUp(self):
        self.types = create_equipment_types()
        self.instances = create_equipment_instances(self.types)
        self.mappings = create_plc_mappings()

    def test_plc_values_generated(self):
        """PLC 값이 생성되면 태그 수만큼 항목이 있어야 한다"""
        values = generate_plc_values(self.mappings)
        self.assertEqual(len(values), len(self.mappings))

    def test_apply_plc_updates_instance(self):
        """PLC 값을 적용하면 Instance의 OperationData가 업데이트되어야 한다"""
        values = generate_plc_values(self.mappings)
        apply_plc_to_instance(values, self.mappings, self.instances)
        reflow = self.instances["Reflow_01"]
        self.assertIsNotNone(reflow.operation_data.get("Zone1Temperature"))


class TestSimulation(unittest.TestCase):
    def setUp(self):
        types = create_equipment_types()
        self.instances = create_equipment_instances(types)
        self.mappings = create_plc_mappings()
        self.products = create_pcb_products(count=5)
        # fail_rate=1.0 으로 설정하면 모든 PCB가 AOI 또는 ICT에서 불량
        self.snapshots = run_simulation(
            self.products, self.instances, self.mappings, fail_rate=1.0
        )

    def test_snapshot_count(self):
        """PCB 수 × 공정 수만큼 스냅샷이 생성되어야 한다"""
        expected = len(self.products) * len(SMT_LINE_SEQUENCE)
        self.assertEqual(len(self.snapshots), expected)

    def test_all_products_failed(self):
        """fail_rate=1.0 이면 모든 PCB가 FAIL이어야 한다"""
        failed = find_failed_products(self.products)
        self.assertEqual(len(failed), len(self.products))

    def test_trace_barcode(self):
        """특정 바코드의 스냅샷 수는 공정 수와 같아야 한다"""
        barcode = self.products[0].pcb_barcode
        records = get_snapshots_by_barcode(barcode, self.snapshots)
        self.assertEqual(len(records), len(SMT_LINE_SEQUENCE))

    def test_snapshot_has_process_name(self):
        """스냅샷에는 process_name이 있어야 한다"""
        for snap in self.snapshots:
            self.assertTrue(snap.process_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
