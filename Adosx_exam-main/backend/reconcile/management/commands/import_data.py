import csv, logging
from pathlib import Path
from django.core.management.base import BaseCommand
from reconcile.models import Location, SystemARecord, SystemBEntry
from reconcile.importer import clean_text, normalize_ref, parse_amount, parse_date
log=logging.getLogger(__name__)
DATA=Path(__file__).resolve().parents[3]/"data"
def read_csv(name):
    with (DATA/name).open(newline="",encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)
class Command(BaseCommand):
    help="Import all source rows idempotently."
    def handle(self,*args,**kwargs):
        nloc=0
        for r in read_csv("locations.csv"):
            Location.objects.update_or_create(location_id=clean_text(r.get("location_id")),defaults={"org_id":clean_text(r.get("org_id")),"name":clean_text(r.get("location_name"))})
            nloc+=1
        a_read=a_saved=b_read=b_saved=bad=cleaned=0
        for raw in read_csv("system_a.csv"):
            a_read+=1; r={k:clean_text(v) for k,v in raw.items()}
            loc=Location.objects.filter(location_id=r.get("location_id")).first()
            if r.get("location_id") and not loc: log.warning("Unknown A location: %s",r.get("location_id"))
            SystemARecord.objects.update_or_create(record_id=r["record_id"],defaults={
                "location":loc,"location_id_raw":r.get("location_id",""),"event_date":parse_date(r.get("event_date")),
                "category_code":r.get("category_code",""),"actor_id":r.get("actor_id") or None,
                "base_value_raw":r.get("base_value",""),"adjustment_raw":r.get("adjustment",""),"total_value_raw":r.get("total_value",""),
                "base_value":parse_amount(r.get("base_value")),"adjustment":parse_amount(r.get("adjustment")),"total_value":parse_amount(r.get("total_value")),"state":r.get("state","")})
            a_saved+=1
        for raw in read_csv("system_b.csv"):
            b_read+=1; r={k:clean_text(v) for k,v in raw.items()}
            ref=normalize_ref(r.get("record_ref")); val=parse_amount(r.get("value"))
            if ref != r.get("record_ref"): cleaned+=1
            if val is None: bad+=1; log.warning("Blank/invalid B amount at %s",r.get("entry_id"))
            loc=Location.objects.filter(location_id=r.get("location_id")).first()
            if r.get("location_id") and not loc: log.warning("Unknown B location: %s",r.get("location_id"))
            SystemBEntry.objects.update_or_create(entry_id=r["entry_id"],defaults={
                "record_ref_raw":r.get("record_ref",""),"record_ref":ref,"location":loc,"location_id_raw":r.get("location_id",""),
                "recorded_on":parse_date(r.get("recorded_on")),"value_raw":r.get("value",""),"value":val,"label":r.get("label","")})
            b_saved+=1
        self.stdout.write(self.style.SUCCESS(f"Locations: {nloc} read; A: {a_read} read/{a_saved} upserted; B: {b_read} read/{b_saved} upserted; invalid B amounts: {bad}; refs normalized: {cleaned}"))
