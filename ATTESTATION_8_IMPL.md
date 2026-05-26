# joint-harness-v0 — 8-implementation cross-validation attestation

**Date:** 2026-05-26
**Vector set:** `joint_harness_v0_vectors.json` (6 vectors, frozen)
**Discipline:** `urn:x402:canonicalisation:jcs-rfc8785-v1`
**Result:** **48 / 48 byte-for-byte agreements PASS**

## Methodology

Each of the 6 joint-receipt fixtures was reduced to its JCS preimage (joint receipt with `joint_ref` field zero-substituted to `sha256:0000…0000`). The preimage was independently JCS-canonicalised in each of the 8 implementations listed below, SHA-256-hashed, and compared byte-for-byte to:

1. **`expected_jcs_bytes_b64`** — the base64-encoded JCS canonical bytes (full sequence equality)
2. **`expected_content_hash`** — the SHA-256 hex over the canonical bytes (which is the asserted `joint_ref` without the `sha256:` prefix)

A vector PASSES iff both fields match.

## Per-implementation result

| Implementation | Library / version | Vectors PASS |
|---|---|---|
| Python | `rfc8785@0.1.4` (via `algovoi-substrate@0.3.0`) | **6 / 6** |
| Node.js | `canonicalize@3.0.0` | **6 / 6** |
| Ruby | `json-canonicalization` (rubygem) | **6 / 6** |
| PHP | `root23/json-canonicalization` | **6 / 6** |
| Go | `github.com/gowebpki/jcs v1.0.1` | **6 / 6** |
| Rust | `serde_jcs@0.2.0` | **6 / 6** |
| Java | `cyberphone/json-canonicalization` | **6 / 6** |
| .NET | `Baqhub` | **6 / 6** |
| **Total** | | **48 / 48** |

## Per-fixture content hashes

| Fixture id | Crest recommendation | AlgoVoi verdict | `joint_ref` (content hash over JCS preimage) |
|---|---|---|---|
| `0001-allow-allow-baseline` | `allow` | `ALLOW` | `b035d7f0b838f284c1ea205ff1343a82c7f0461456df040dc429bb64ec63f3c2` |
| `0002-caution-refer-watchlist` | `caution` | `REFER` | `79fd3afcc23e1f8d85cb1e9a499347392e0499280335df3a8dc1b8862b26f3e9` |
| `0003-deny-deny-sanctions` | `deny` | `DENY` | `81ea312260253d870d203b70cd00ca338db630ecd5185c010298f98c2f6852b4` |
| `0004-no_data-allow-newpayee` | `no_data` | `ALLOW` | `a7f4f547bb6ecb917aaaa7ad74ac4d0422c7a857fca17f4c83d280f11a0f45df` |
| `0005-allow-refer-jurisdiction` | `allow` | `REFER` | `438c3639cfa54633678369ee749ec9e440b7aacec1a101bfb9712fb7cda8c10b` |
| `0006-deny-allow-fraud_history` | `deny` | `ALLOW` | `db77d2dbbeec8d6c388366767e8db9b3e848ef087cf98bb228e88c1120b63e92` |

All 8 implementations produced exactly these 6 hash values from the corresponding fixtures' JCS preimages.

## Compliance-ref and conformance-ref hashes (Python-derived, byte-stable across all 8 impls)

| Fixture | compliance_ref (AlgoVoi half) | conformance_ref (Crest half) |
|---|---|---|
| 0001 | `sha256:25e75b64be4d7eb7c285b1aa748bbf4ad5ee867c43d4f5e922ef5eefc32b6894` | `sha256:0303177e6fdb0b847923fd83fb3823b2e64f3c9f28ec124e271f135aeedf3ce7` |
| 0002 | `sha256:543a27bbde4c2c80b3aa12cee66955d377a9dd885f34bf74949e04a716d28da5` | `sha256:9adfee1ade353d3833801774aa0106c9b3a8afd74642907d6af95934b59da9ab` |
| 0003 | `sha256:1e6eb361f7365b73056304900f8efc678717a0e25f40a5db452408b70ea98db9` | `sha256:47ae17c2eb6acfb8d617482df7414f58fb93a0ca68e07ddaa8c6594dc3d4353c` |
| 0004 | `sha256:df41307b3b607deb2a8b9064f34521662db8eaa2821bf6680a2d7d271764b37c` | `sha256:1ebfeefeb857ef21cd3005b427ee0f7379d584b7d5dd1ff3ac1e8692ea5dc41f` |
| 0005 | `sha256:ec093554ad388ebb7389b05dd9bb05840b667872d3e9c11763f7ed020cbc13f1` | `sha256:cf9971e40d0bd6a6c34217fde04ae166db69d71748b63188f55006c565819485` |
| 0006 | `sha256:17eb62955f260e9430f7207a2fc0400502f2ff284d1966d3c73c0aa761afc7a8` | `sha256:7ff807b0a0b2fd0a6c60fa60b3b721cee2870088455ea86ec5608eee08d2cc80` |

Each `compliance_ref` is `SHA-256(JCS(compliance_receipt))` where the compliance receipt is emitted by `algovoi_substrate.build_compliance_receipt(...)`. Each `conformance_ref` is `SHA-256(JCS(crest_core))` where `crest_core` is the canonical preimage Crest's Supership service would sign.

## What is demonstrated

1. **Byte-deterministic composition.** The joint receipt is byte-stable across 8 independent JCS implementations in 8 languages. Anyone holding the joint receipt can verify the `joint_ref` derivation in their language of choice using a standards-compliant JCS implementation, with no AlgoVoi or Crest tooling required.
2. **No spec extension required.** The composition uses the existing `urn:x402:canonicalisation:jcs-rfc8785-v1` discipline. No new canonicalisation rules, no new field semantics, no schema fork.
3. **Self-reference resolved cleanly.** The zero-substitution pattern for computing `joint_ref` over a document that contains `joint_ref` is byte-stable across all 8 impls — confirming the convention is implementation-agnostic.
4. **Operationally-distinct cell coverage.** Six byte-distinct hash values for six operationally-distinct compliance × conformance compositions, including the structurally-informative asymmetric cells (0005 allow-REFER and 0006 deny-ALLOW) where one half flags and the other passes.

## Cumulative cross-validation totals

As of 2026-05-26, the AlgoVoi substrate stack has been cross-validated byte-for-byte at the following scales:

| Workstream | Implementations | Vectors | Agreements |
|---|---|---|---|
| Substrate JCS matrix (5 receipt-format sets) | 8 | 24 | 192 / 192 |
| PQC cross-product matrix | 4 producers × 6 verifiers | 1 | 24 / 24 |
| **joint-harness-v0** | **8** | **6** | **48 / 48** |
| **Cumulative** | | | **264 / 264** |

## Runner sources

The 8 implementations used for this run are sourced from the existing AlgoVoi cross-validation harness at `algovoi-jcs-conformance-vectors/_attestations/2026-05-25-8-impl-5-format-cross-validation/`. Library versions are pinned in that harness's `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, and `.csproj` files. Sources are public on `chopmob-cloud/algovoi-jcs-conformance-vectors`.
