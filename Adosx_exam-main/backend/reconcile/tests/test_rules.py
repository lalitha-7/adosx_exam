from decimal import Decimal
from datetime import date
from types import SimpleNamespace as O
import pytest
from reconcile.compare import compare_records
from reconcile.importer import normalize_ref,parse_amount

def loc(i="L1",org="ORG-A"): return O(location_id=i,org_id=org)
def A(total="100.00",state="CONFIRMED",rid="REC-1",location="L1",dt=date(2026,3,1)):
    return O(record_id=rid,total_value=Decimal(total) if total is not None else None,state=state,location=loc(location),location_id_raw=location,event_date=dt)
def B(ref="REC-1",value="100.00",entry="E1",location="L1",dt=date(2026,3,1)):
    return O(record_ref=ref,record_ref_raw=ref,value=Decimal(value) if value is not None else None,entry_id=entry,location=loc(location),location_id_raw=location,recorded_on=dt)
def rs(a,b): return [x["reason"] for x in compare_records(a,b)]
def test_clean(): assert compare_records([A()],[B()])==[]
def test_missing(): assert "MISSING_IN_B" in rs([A()],[])
def test_orphan(): assert "ORPHAN_IN_B" in rs([], [B(ref="REC-9")])
def test_duplicate(): assert "DUPLICATE_IN_B" in rs([A()],[B(),B(entry="E2")])
def test_value_mismatch(): assert "VALUE_MISMATCH" in rs([A()],[B(value="90")])
def test_blank_invalid_not_zero(): assert "INVALID_AMOUNT" in rs([A()],[B(value=None)])
def test_split_is_valid(): assert rs([A()],[B(value="40"),B(value="60",entry="E2")])==[]
def test_voided(): assert "VOIDED_ENTRY_IN_B" in rs([A(state="VOIDED")],[B()])
def test_metadata_mismatch():
    assert {"LOCATION_MISMATCH","DATE_MISMATCH"} <= set(rs([A()],[B(location="L2",dt=date(2026,3,2))]))
def test_cleaners():
    assert [normalize_ref(x) for x in ("rec1034"," REC - 1070 ","1112")]==["REC-1034","REC-1070","REC-1112"]
    assert parse_amount("1,25,400.00")==Decimal("125400.00")
    assert parse_amount("") is None and parse_amount("bad") is None
