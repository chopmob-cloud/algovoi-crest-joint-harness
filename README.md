# joint-harness-v0

Shared conformance harness for the **AlgoVoi compliance receipt × Crest service-trust attestation** composition.

Given an x402 payment event, the harness produces a single byte-deterministic **joint receipt** carrying:

- a **compliance disposition** from AlgoVoi (`ALLOW` / `REFER` / `DENY` under `urn:x402:canonicalisation:jcs-rfc8785-v1`), and
- a **conformance proof** from Crest (Trust Receipt under `urn:crest:trust-check-v1` / Supership).

The joint receipt is itself JCS-canonicalised, content-addressed by `joint_ref = SHA-256(JCS(joint_receipt))`, and independently verifiable by either side using only public data.

## Status

**Draft v0 — AlgoVoi-authored response to the joint-harness scoping ask from PR #1 on `chopmob-cloud/algovoi-jcs-conformance-vectors`.** Pre-share with Crest for review.

| Stage | Status |
|---|---|
| Scope doc | Complete (`SCOPE.md`) |
| Joint-receipt schema | Complete (`FIXTURE_FORMAT.md`) |
| Reference harness (Python) | Complete (`harness/harness.py`) |
| Fixture coverage matrix (6 cells) | Complete (`fixtures/0001-0006.json`, all frozen) |
| Self-validation | **36/36 PASS** (6 fixtures × 6 internal checks) |
| 8-implementation cross-validation | **48/48 PASS** (8 JCS impls × 6 fixtures) |
| TS / Node.js port of harness | Pending Crest input |
| Live-endpoint integration | Out of v0 scope |

## Quick start

```bash
pip install algovoi-substrate
cd harness
python harness.py
```

Expected output: 6 fixtures, 6 PASS lines each, 36/36 PASS total.

## Files

```
SCOPE.md                              Scope: in / out / authorship / references
FIXTURE_FORMAT.md                     Joint-receipt schema + verification algo + open questions
harness/harness.py                    Python reference runner
fixtures/0001-allow-allow-baseline.json
fixtures/0002-caution-refer-watchlist.json
fixtures/0003-deny-deny-sanctions.json
fixtures/0004-no_data-allow-newpayee.json
fixtures/0005-allow-refer-jurisdiction.json
fixtures/0006-deny-allow-fraud_history.json
joint_harness_v0_vectors.json         8-impl-runner-compatible vector set
ATTESTATION_8_IMPL.md                 48/48 byte-for-byte cross-validation result
```

## Open questions for Crest review

Logged in `FIXTURE_FORMAT.md` § "Open questions for Crest review":

1. `J.conformance.spec` — fixed string in v0, or open enum from day one?
2. Evidence-anchor hashing scope — full typed-evidence array under JCS, or stable subset?
3. Score null-semantics — hard `score == null ⇔ score_null_reason != null` invariant?
4. Joint-receipt signing — leave unsigned in v0, add joint signature in v1?

## Cross-references

- AlgoVoi canonicalisation discipline: `urn:x402:canonicalisation:jcs-rfc8785-v1` — IETF I-D [draft-hopley-x402-canonicalisation-jcs-v1](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/)
- AlgoVoi compliance receipt: IETF I-D [draft-hopley-x402-compliance-receipt](https://datatracker.ietf.org/doc/draft-hopley-x402-compliance-receipt/)
- AlgoVoi composite trust query: IETF I-D [draft-hopley-x402-composite-trust-query](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/)
- Crest trust-check spec: `urn:crest:trust-check-v1` discovery at [supership.crestsystems.ai/.well-known/risk-check.json](https://supership.crestsystems.ai/.well-known/risk-check.json)
- Crest action-ref-verify repo: [andysalvo/action-ref-verify](https://github.com/andysalvo/action-ref-verify)
- Originating scoping ask: [chopmob-cloud/algovoi-jcs-conformance-vectors PR #1](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors/pull/1#issuecomment-4548707008)

## Licence

Apache 2.0.

## Authors

- AlgoVoi (Christopher Hopley) — joint-receipt schema, AlgoVoi compliance half, fixture coverage matrix, Python reference harness, 8-impl cross-validation matrix.
- Crest Deployment Systems LLC (Andy Salvo) — Crest service-trust half input, joint-harness scoping ask (PR #1 follow-up comment 2026-05-26).
