# joint-harness-v0 — Scope

**Status:** draft, AlgoVoi-side. Pre-share with Crest for review.

## Purpose

A shared conformance harness that, given an x402 payment event, produces a single byte-deterministic **joint receipt** carrying both:

- a **compliance disposition** from AlgoVoi (`ALLOW` / `REFER` / `DENY` under `urn:x402:canonicalisation:jcs-rfc8785-v1`), and
- a **conformance proof** from Crest (Trust Receipt under `urn:crest:trust-check-v1` plus optional service-trust evaluation under Supership).

The joint receipt is itself JCS-canonicalised, content-addressed by `joint_ref = SHA-256(JCS(joint_receipt))`, and independently verifiable by either side using only public data.

## In scope (v0)

1. **Joint receipt format** — a single JSON document with three top-level sections: `payment`, `compliance` (AlgoVoi), `conformance` (Crest). Pinned to `canon_version: jcs-rfc8785-v1`.
2. **Cross-reference primitive** — `compliance.compliance_ref` and `conformance.conformance_ref` are each `sha256:<lowercase-hex-64>` over the JCS-canonical bytes of their respective sub-document. The two refs make the halves independently re-derivable.
3. **Verification semantics** — joint receipt is `VALID` iff both halves verify under their own discipline AND `joint_ref` recomputes byte-for-byte. Either half failing fails the joint.
4. **Fixture format** — input fixtures specify a synthetic payment event; expected outputs are the AlgoVoi half, the Crest half, and the recomputed `joint_ref`.
5. **Reference harness** — Python + Node.js runners that consume a fixture, call (or stub) each side's emitter, and assert byte equality of all three hashes.
6. **Coverage matrix** — at least one fixture per recommendation × compliance verdict combination (`{allow, caution, deny, no_data} × {ALLOW, REFER, DENY}`). Cells covering operationally-impossible combinations (e.g. Crest `no_data` × AlgoVoi `DENY` with sanctions hit) are explicitly excluded with a note.

## Out of scope (v0)

- **No new spec text.** This harness consumes existing AlgoVoi and Crest specs; it does not propose new fields, new enums, or new lifecycle states.
- **No bilateral receipt fork.** The joint receipt is a verification artefact, not a substitute for either party's primary receipt.
- **No automated submission to either party's signing key.** Reference fixtures use deterministic test keys (Ed25519 keypair embedded in `fixtures/test_keys.json`). Production keys never leave their owners' infrastructure.
- **No real-time call into `verify.crestsystems.ai` or `api.algovoi.co.uk` from the test runner.** The harness uses fixture inputs only; live-endpoint integration is a separate work item.
- **No payment-rail extension beyond x402.** Composition with AP2 / A2A / MPP rails is a follow-up.

## Authorship and licence

- AlgoVoi authors the joint-receipt schema and the compliance half of fixtures.
- Crest authors the conformance half of fixtures and the verifier-side runner pass.
- Apache 2.0, dual-owned. Repo home TBD (candidates: a new `algovoi-crest-joint-harness`, or a subtree in either of the existing conformance-vector repos).

## Cross-references

- AlgoVoi canonicalisation discipline: `urn:x402:canonicalisation:jcs-rfc8785-v1` — IETF I-D [draft-hopley-x402-canonicalisation-jcs-v1](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/).
- AlgoVoi compliance receipt: IETF I-D [draft-hopley-x402-compliance-receipt](https://datatracker.ietf.org/doc/draft-hopley-x402-compliance-receipt/).
- Crest trust-check spec: `urn:crest:trust-check-v1` discovery at [supership.crestsystems.ai/.well-known/risk-check.json](https://supership.crestsystems.ai/.well-known/risk-check.json).
- Crest action-ref-verify repo: [andysalvo/action-ref-verify](https://github.com/andysalvo/action-ref-verify).
