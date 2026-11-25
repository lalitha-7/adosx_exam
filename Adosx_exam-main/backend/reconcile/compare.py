from collections import defaultdict
from decimal import Decimal


def compare_records(a_rows, b_rows):
    a_by = {a.record_id: a for a in a_rows}
    groups = defaultdict(list)
    out = []

    for b in b_rows:
        groups[b.record_ref].append(b)

    def add(reason, rid, a=None, b=None, detail=""):
        cross = bool(
            a and b
            and a.location and b.location
            and a.location.org_id != b.location.org_id
        )

        owner = (
            a.location.org_id if a and a.location
            else (b.location.org_id if b and b.location else None)
        )

        out.append({
            "org": owner,
            "reason": reason,
            "record_id": rid,
            "location": (
                a.location_id_raw if a
                else (b.location_id_raw if b else None)
            ),
            "a_value": (
                str(a.total_value)
                if a and a.total_value is not None
                else None
            ),
            "b_value": (
                str(b.value)
                if b and b.value is not None
                else None
            ),
            "difference": (
                str(b.value - a.total_value)
                if a and b
                and a.total_value is not None
                and b.value is not None
                else None
            ),
            "a_location": a.location_id_raw if a else None,
            "b_location": b.location_id_raw if b else None,
            "details": detail,
            "date": str(
                (a.event_date if a else None)
                or (b.recorded_on if b else "")
            ),
            "_cross": cross,
        })

    # Report nonblank B references that have no matching A record.
    # Blank/un-normalizable references are handled once in the final loop.
    for ref, entries in groups.items():
        if ref and ref not in a_by:
            for b in entries:
                add(
                    "ORPHAN_IN_B",
                    ref,
                    b=b,
                    detail="B reference has no A record.",
                )

    for a in a_rows:
        entries = groups.get(a.record_id, [])

        if a.state.upper() == "VOIDED":
            for b in entries:
                add(
                    "VOIDED_ENTRY_IN_B",
                    a.record_id,
                    a,
                    b,
                    "B contains an entry for a voided A record.",
                )
            continue

        if not entries:
            add(
                "MISSING_IN_B",
                a.record_id,
                a=a,
                detail="A record has no B entry.",
            )
            continue

        if len(entries) > 1:
            vals = [b.value for b in entries]

            if any(v is None for v in vals) or a.total_value is None:
                add(
                    "INVALID_AMOUNT",
                    a.record_id,
                    a,
                    entries[0],
                    "At least one amount in the group is blank or invalid.",
                )
            elif sum(vals, Decimal("0.00")) != a.total_value:
                add(
                    "DUPLICATE_IN_B",
                    a.record_id,
                    a,
                    entries[0],
                    "Multiple B entries do not sum to A total.",
                )
            else:
                for b in entries:
                    if b.location_id_raw != a.location_id_raw:
                        add(
                            "LOCATION_MISMATCH",
                            a.record_id,
                            a,
                            b,
                            "Locations differ.",
                        )
                    if b.recorded_on != a.event_date:
                        add(
                            "DATE_MISMATCH",
                            a.record_id,
                            a,
                            b,
                            "Dates differ.",
                        )
            continue

        b = entries[0]

        if b.value is None or a.total_value is None:
            add(
                "INVALID_AMOUNT",
                a.record_id,
                a,
                b,
                "A total or B amount is blank/invalid.",
            )
        elif b.value != a.total_value:
            add(
                "VALUE_MISMATCH",
                a.record_id,
                a,
                b,
                "B value differs from A total.",
            )

        if b.location_id_raw != a.location_id_raw:
            add(
                "LOCATION_MISMATCH",
                a.record_id,
                a,
                b,
                "Locations differ.",
            )

        if b.recorded_on != a.event_date:
            add(
                "DATE_MISMATCH",
                a.record_id,
                a,
                b,
                "Dates differ.",
            )

    # Report blank/un-normalizable B references exactly once.
    for b in b_rows:
        if not b.record_ref:
            add(
                "ORPHAN_IN_B",
                b.record_ref_raw or b.entry_id,
                b=b,
                detail="Reference cannot be normalized.",
            )

    return out


def tenant_view(issue, org):
    if issue["org"] != org:
        return None

    row = {k: v for k, v in issue.items() if not k.startswith("_")}

    if issue.get("_cross"):
        row.update(
            b_location=None,
            b_value=None,
            difference=None,
        )
        row["details"] += " B-side fields redacted for cross-org privacy."

    return row