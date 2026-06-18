"""
traceability.py
불량 PCB의 이전 공정 데이터를 조회·출력하는 추적 모듈
"""

from src.aas_models import ProcessSnapshot, ProductPCB


def get_snapshots_by_barcode(
    barcode: str,
    snapshots: list[ProcessSnapshot],
) -> list[ProcessSnapshot]:
    """특정 PCB 바코드의 모든 공정 스냅샷을 시간순으로 반환"""
    matched = [s for s in snapshots if s.pcb_barcode == barcode]
    matched.sort(key=lambda s: s.timestamp)
    return matched


def find_failed_products(products: list[ProductPCB]) -> list[ProductPCB]:
    """불량 판정된 PCB 목록 반환"""
    return [p for p in products if p.final_result.startswith("FAIL")]


def print_production_summary(products: list[ProductPCB]) -> None:
    print("\n" + "=" * 50)
    print("=== Production Result ===")
    print("=" * 50)
    for p in products:
        status = p.final_result
        print(f"  {p.pcb_barcode}  [{p.model_name}]  →  {status}")


def print_trace_result(barcode: str, snapshots: list[ProcessSnapshot]) -> None:
    """불량 PCB의 공정별 데이터를 보기 좋게 출력"""
    records = get_snapshots_by_barcode(barcode, snapshots)
    print("\n" + "=" * 50)
    print(f"=== Trace Result: {barcode} ===")
    print("=" * 50)
    if not records:
        print(f"  데이터 없음: {barcode}")
        return
    for snap in records:
        print(f"\n  [{snap.process_name}]  설비: {snap.equipment_instance_id}  시각: {snap.timestamp}")
        # 운전 데이터
        if snap.operation_data:
            items = [f"{k}={v}" for k, v in snap.operation_data.items() if v is not None]
            if items:
                print(f"    OperationData : {', '.join(items)}")
        # 품질 결과
        if snap.quality_result:
            items = [f"{k}={v}" for k, v in snap.quality_result.items() if v is not None]
            if items:
                print(f"    QualityResult : {', '.join(items)}")


def print_all_traces(products: list[ProductPCB], snapshots: list[ProcessSnapshot]) -> None:
    """불량 PCB 전체 추적 결과 출력"""
    failed = find_failed_products(products)
    if not failed:
        print("\n  불량 PCB 없음 — 전 수량 PASS")
        return
    for p in failed:
        print_trace_result(p.pcb_barcode, snapshots)
