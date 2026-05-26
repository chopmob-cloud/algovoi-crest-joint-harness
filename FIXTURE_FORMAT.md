# joint-harness-v0 — Joint Receipt Format

**Status:** draft v0, AlgoVoi-side. Pre-share with Crest for review.

## Joint receipt JSON shape

```json
{
  "canon_version": "jcs-rfc8785-v1",
  "joint_version": "joint-harness-v0",
  "payment": {
    "payment_ref": "sha256:<lowercase-hex-64>",
    "chain": "eip155:8453",
    "asset_id": "USDC.6",
    "amount_minor": "<string-decimal>",
    "payer_ref": "sha256:<lowercase-hex-64>",
    "payee_ref": "sha256:<lowercase-hex-64>",
    "timestamp_ms": 1716494400000
  },
  "compliance": {
    "compliance_ref": "sha256:<lowercase-hex-64>",
    "provider_did": "did:web:api.algovoi.co.uk",
    "verdict": "ALLOW",
    "jurisdiction_flags": ["UK", "EU"],
    "evidence_anchor": "sha256:<lowercase-hex-64>"
  },
  "conformance": {
    "conformance_ref": "sha256:<lowercase-hex-64>",
    "provider_did": "did:web:supership.crestsystems.ai",
    "spec": "urn:crest:trust-check-v1",
    "recommendation": "allow",
    "score": 87,
    "score_null_reason": null,
    "evidence_anchor": "sha256:<lowercase-hex-64>"
  },
  "joint_ref": "sha256:<lowercase-hex-64>"
}
```

## Field definitions

### Top level

- `canon_version` — string. MUST equal `"jcs-rfc8785-v1"`.
- `joint_version` — string. MUST equal `"joint-harness-v0"`. Pins the joint receipt format itself, separately from the canonicalisation discipline.
- `payment` — object. The common anchor; both halves reference it.
- `compliance` — object. AlgoVoi-emitted half.
- `conformance` — object. Crest-emitted half.
- `joint_ref` — string `sha256:<lowercase-hex-64>`. SHA-256 over the JCS-canonical bytes of the object with `joint_ref` itself set to the literal string `"sha256:0000…0000"` (64 zeros) — i.e. computed-then-substituted to break the self-reference.

### `payment` block

- `payment_ref` — string `sha256:<lowercase-hex-64>`. Content-addressed identifier of the underlying payment event (chain-native transaction hash hashed under JCS for cross-chain uniformity).
- `chain` — string. CAIP-2 namespace:reference. Example `eip155:8453` (Base mainnet).
- `asset_id` — string. Asset symbol plus minor-unit decimals, dot-separated. Example `USDC.6`.
- `amount_minor` — string. Amount in minor units as decimal string (avoids float precision loss).
- `payer_ref`, `payee_ref` — string `sha256:<lowercase-hex-64>`. Content-addressed counterparty references.
- `timestamp_ms` — integer. Epoch milliseconds, per Substrate Rule 2.

### `compliance` block (AlgoVoi half)

- `compliance_ref` — string `sha256:<lowercase-hex-64>`. SHA-256 over JCS-canonical bytes of the AlgoVoi compliance receipt as emitted by `algovoi_substrate.build_compliance_receipt(...)`.
- `provider_did` — string. AlgoVoi's compliance-screen provider DID.
- `verdict` — string closed enum. One of `"ALLOW"`, `"REFER"`, `"DENY"` per the AlgoVoi compliance-receipt discipline.
- `jurisdiction_flags` — ordered array of ISO-3166-1 codes; primary jurisdiction first.
- `evidence_anchor` — string `sha256:<lowercase-hex-64>`. Hash anchoring the screening evidence chain row referenced by this compliance verdict.

### `conformance` block (Crest half)

- `conformance_ref` — string `sha256:<lowercase-hex-64>`. SHA-256 over JCS-canonical bytes of the Crest Trust Receipt as emitted by Supership / verify.crestsystems.ai.
- `provider_did` — string. Crest's emitting DID.
- `spec` — string. SHOULD equal `"urn:crest:trust-check-v1"` for the v0 harness; OPEN enum for future Crest spec versions.
- `recommendation` — string closed enum per the Supership discovery doc: `"allow"`, `"caution"`, `"deny"`, `"no_data"`.
- `score` — integer or null. Numeric trust score; `null` when `score_null_reason` is non-null.
- `score_null_reason` — string closed enum or null per the Supership discovery doc: `"unknown_service"`, `"insufficient_signal"`, `"evaluation_failed"`, `"no_query_subject"`. MUST be null iff `score` is non-null.
- `evidence_anchor` — string `sha256:<lowercase-hex-64>`. Hash anchoring the Crest evidence-typed array.

## Verification algorithm

A consumer holding a joint receipt `J` verifies it as follows:

1. **Recompute `joint_ref`.** Substitute the literal `"sha256:0000…0000"` (64 zeros) for `J.joint_ref`, JCS-canonicalise the result, SHA-256, compare. MUST match `J.joint_ref`.
2. **Pull the AlgoVoi half.** Fetch (or accept under separate channel) the compliance receipt whose JCS-canonical SHA-256 equals `J.compliance.compliance_ref`. Verify its signature using the published `provider_did` JWKS. MUST equal the asserted `verdict`, `jurisdiction_flags`, `evidence_anchor`.
3. **Pull the Crest half.** Same shape: fetch the Trust Receipt whose JCS-canonical SHA-256 equals `J.conformance.conformance_ref`. Verify Ed25519 JWS signature against the Crest JWKS. MUST equal the asserted `recommendation`, `score`, `score_null_reason`, `evidence_anchor`.
4. **Pull the payment event.** Confirm `J.payment.payment_ref` resolves to a real chain transaction matching `chain`, `asset_id`, `amount_minor`, `timestamp_ms`. Confirm both halves' receipts cite the same `payment_ref` internally.

The joint receipt is `VALID` iff all four steps pass. Any failure invalidates the joint, regardless of which half failed.

## Fixture-file shape

Each fixture in `fixtures/` is a JSON file:

```json
{
  "id": "0001-allow-allow-baseline",
  "description": "Crest allow + AlgoVoi ALLOW. Baseline-clean joint receipt.",
  "inputs": {
    "payment": { "...as above..." },
    "compliance_emitter_input": { "...AlgoVoi build_compliance_receipt kwargs..." },
    "conformance_emitter_input": { "...Crest trust-check request body..." }
  },
  "expected": {
    "compliance_ref": "sha256:...",
    "conformance_ref": "sha256:...",
    "joint_ref": "sha256:...",
    "joint_receipt": { "...full materialised joint receipt..." }
  }
}
```

## Initial coverage matrix

| Fixture id | Crest recommendation | AlgoVoi verdict | Notes |
|---|---|---|---|
| `0001-allow-allow-baseline` | `allow` | `ALLOW` | Clean joint; both pass. |
| `0002-caution-refer-watchlist` | `caution` | `REFER` | Soft-flag both sides; payer warrants ongoing monitoring. |
| `0003-deny-deny-sanctions` | `deny` | `DENY` | Hard halt; counterparty sanctions hit + Crest behavioural deny. |
| `0004-no_data-allow-newpayee` | `no_data` (`unknown_service`) | `ALLOW` | New payee with no Crest history; AlgoVoi compliance still passes. |
| `0005-allow-refer-jurisdiction` | `allow` | `REFER` | Crest sees clean behaviour but AlgoVoi flags REFER on jurisdiction. |
| `0006-deny-allow-fraud_history` | `deny` | `ALLOW` | Compliance clean but Crest behavioural deny on fraud history. |

The asymmetry between the two halves in `0005` and `0006` is the structural reason the joint receipt is operationally informative — neither half alone captures both signals.

## Open questions for Crest review

1. **Spec URN governance:** Should `J.conformance.spec` be a fixed `"urn:crest:trust-check-v1"` in v0 fixtures, or an open enum from day one (so `urn:crest:trust-check-v2` slots in cleanly later)?
2. **Evidence anchor hashing scope:** Does Crest currently hash the `evidence_anchor` over the full typed-evidence array, or over a stable subset? AlgoVoi proposes "full typed-evidence array, JCS-canonical bytes, SHA-256."
3. **Score null semantics:** v0 enforces `score == null ⇔ score_null_reason != null` as a hard invariant. Crest may want a softer "score MAY be present alongside null_reason for transparency" rule. AlgoVoi prefers the hard rule.
4. **Joint-receipt signing:** v0 leaves the joint receipt unsigned (it is a verification artefact, not a primary record). Future revision could add a `joint_signature` block jointly signed by both parties. Defer to v1.
