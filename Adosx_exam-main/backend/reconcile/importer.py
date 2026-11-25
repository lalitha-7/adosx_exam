import re
from datetime import date
from decimal import Decimal, InvalidOperation
def clean_text(v): return (v or "").strip()
def normalize_ref(raw):
    m = re.search(r"\\d+", clean_text(raw))
    return f"REC-{m.group()}" if m else None
def parse_amount(raw):
    s = clean_text(raw).replace(",", "")
    if not s: return None
    try: return Decimal(s)
    except (InvalidOperation, ValueError): return None
def parse_date(raw):
    try: return date.fromisoformat(clean_text(raw)) if clean_text(raw) else None
    except ValueError: return None
