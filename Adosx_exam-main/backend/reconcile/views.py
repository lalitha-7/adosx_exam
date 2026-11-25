from collections import Counter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SystemARecord,SystemBEntry
from .compare import compare_records,tenant_view
@api_view(["GET"])
def disagreements(request):
    org=request.query_params.get("org")
    if org not in {"ORG-A","ORG-B"}: return Response({"error":"org must be ORG-A or ORG-B"},status=status.HTTP_400_BAD_REQUEST)
    a=list(SystemARecord.objects.filter(location__org_id=org).select_related("location"))
    ids=[x.record_id for x in a]
    b=list(SystemBEntry.objects.filter(location__org_id=org).select_related("location"))
    # Fetch cross-org counterparts only for A records owned by this org; output redacts B-side fields.
    b += list(SystemBEntry.objects.filter(record_ref__in=ids).exclude(location__org_id=org).select_related("location"))
    rows=[tenant_view(x,org) for x in compare_records(a,b)]
    rows=[x for x in rows if x]
    reason=request.query_params.get("reason")
    if reason: rows=[x for x in rows if x["reason"]==reason]
    sort=request.query_params.get("sort","")
    if sort in {"value","-value"}: rows.sort(key=lambda x:float(x["a_value"] or x["b_value"] or 0),reverse=sort.startswith("-"))
    elif sort in {"date","-date"}: rows.sort(key=lambda x:x["date"] or "",reverse=sort.startswith("-"))
    return Response({"org":org,"summary":{"total":len(rows),"by_reason":dict(Counter(x["reason"] for x in rows))},"results":rows})
