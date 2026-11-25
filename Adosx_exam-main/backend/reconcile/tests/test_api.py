import pytest
from rest_framework.test import APIClient
from reconcile.models import Location,SystemARecord
@pytest.mark.django_db
def test_api_org_scoping():
    la=Location.objects.create(location_id="LA",org_id="ORG-A")
    lb=Location.objects.create(location_id="LB",org_id="ORG-B")
    SystemARecord.objects.create(record_id="REC-A",location=la,location_id_raw="LA",total_value="10.00")
    SystemARecord.objects.create(record_id="REC-B",location=lb,location_id_raw="LB",total_value="20.00")
    res=APIClient().get("/api/disagreements/?org=ORG-A")
    assert res.status_code==200
    assert all(r["record_id"]!="REC-B" for r in res.data["results"])
