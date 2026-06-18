"""
main.py
AAS 기반 가상 SMT 라인 모니터링 프로토타입 - 전체 데모 실행 진입점

실행: python main.py
"""

from src.equipment_factory import create_equipment_types, create_equipment_instances
from src.plc_mapping import create_plc_mappings, save_mappings_to_json, build_tag_index
from src.production_simulator import create_pcb_products, run_simulation
from src.traceability import (
    print_production_summary,
    print_all_traces,
)


def print_equipment_summary(instances: dict) -> None:
    print("\n" + "=" * 50)
    print("=== Equipment Instances ===")
    print("=" * 50)
    for inst in instances.values():
        print(f"  {inst.instance_id:<20} | {inst.display_name:<20} | {inst.identification}")


def print_mapping_samples(mappings: list, n: int = 6) -> None:
    print("\n" + "=" * 50)
    print("=== PLC TAG Mappings (sample) ===")
    print("=" * 50)
    for m in mappings[:n]:
        print(f"  {m.plc_tag:<35} -> {m.equipment_instance_id}.{m.aas_path}  [{m.data_type}, {m.unit}]")
    print(f"  ... 총 {len(mappings)}개 매핑")


def main() -> None:
    print("\n" + "=" * 50)
    print("  AAS 기반 가상 SMT 라인 모니터링 프로토타입")
    print("=" * 50)

    # ── 1. AAS Type 생성
    print("\n[1] AAS Type 생성 중...")
    types = create_equipment_types()
    print(f"    {len(types)}개 Type 생성 완료: {list(types.keys())}")

    # ── 2. AAS Instance 생성
    print("[2] AAS Instance 생성 중...")
    instances = create_equipment_instances(types)
    print_equipment_summary(instances)

    # ── 3. PLC TAG 매핑 테이블 생성 & JSON 저장
    print("\n[3] PLC TAG 매핑 테이블 생성 중...")
    mappings = create_plc_mappings()
    save_mappings_to_json(mappings, "data/sample_mappings.json")
    print_mapping_samples(mappings)

    # ── 4. 가상 PCB 제품 생성
    print("\n[4] 가상 PCB 제품 생성 중...")
    products = create_pcb_products(count=8)
    print(f"    {len(products)}개 PCB 생성: {[p.pcb_barcode for p in products]}")

    # ── 5. SMT 라인 시뮬레이션 실행
    print("\n[5] SMT 라인 생산 시뮬레이션 실행 중...")
    snapshots = run_simulation(products, instances, mappings, fail_rate=0.30)
    print(f"    총 {len(snapshots)}개 공정 스냅샷 수집 완료")

    # ── 6. 생산 결과 출력
    print_production_summary(products)

    # ── 7. 불량 PCB 추적 출력
    print("\n[6] 불량 PCB 추적 데이터 조회 중...")
    print_all_traces(products, snapshots)

    print("\n" + "=" * 50)
    print("  데모 종료")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
