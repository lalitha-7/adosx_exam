# Decisions

## Decision: compare B with A's total_value
- Rejected: compare against base_value.
- Why: B records the complete event amount; A's total includes base plus adjustment.

## Decision: preserve original text and parse money as Decimal or null
- Rejected: coercing blanks/junk to zero or dropping rows.
- Why: zero is a real value; raw text is needed for audit/recovery.

## Decision: normalize references to REC-<digits>
- Rejected: exact string matching.
- Why: `rec1034`, ` REC - 1070 `, and `1112` are alternate formats for the same reference.

## Decision: a split is valid only when all parts are valid and sum to A's total
- Rejected: flag every repeated reference.
- Why: a reconciled split is not a disagreement.

## Decision: B entry against VOIDED A record is flagged
- Rejected: treat it as expected.
- Why: a voided transaction should not remain posted in B.

## Decision: date and location differences are disagreements
- Rejected: ignore metadata.
- Why: they affect the event's audit trail.

## Decision: cross-org matched mismatch is visible only to A's org, with B-side fields redacted
- Rejected: reveal both organizations' details to either tenant.
- Why: A location is the matched record's ownership anchor; redaction avoids disclosing B's other-org location/value. Orphans are scoped by B location.
