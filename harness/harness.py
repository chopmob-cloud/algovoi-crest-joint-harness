"""joint-harness-v0 reference harness.

Reads a fixture, materialises a joint receipt under the AlgoVoi
canonicalisation discipline, and asserts byte equality of every
declared content-addressed hash.

Run:  python harness.py ../fixtures/0001-allow-allow-baseline.json
"""

import hashlib
import json
import sys
from pathlib import Path

try:
    from algovoi_substrate import canonicalize, sha256_jcs, build_compliance_receipt
except ImportError:
    print("ERROR: algovoi-substrate not installed. Run: pip install algovoi-substrate", file=sys.stderr)
    sys.exit(2)


ZERO_REF = "sha256:" + "0" * 64
JOINT_VERSION = "joint-harness-v0"
CANON_VERSION = "jcs-rfc8785-v1"


def jcs_sha256_hex(obj: dict) -> str:
    """JCS-canonicalise obj and return sha256:<hex>."""
    canon = canonicalize(obj)
    if isinstance(canon, str):
        canon = canon.encode("utf-8")
    return "sha256:" + hashlib.sha256(canon).hexdigest()


def synthesize_crest_trust_receipt(inputs: dict) -> dict:
    """Stub Crest trust-check response.

    In production this is what supership.crestsystems.ai would emit
    (Ed25519-signed JWS, response_ref = SHA-256(JCS(core_fields))).
    For fixture purposes we materialise the bytes Crest would canonicalise
    and emit the receipt deterministically.
    """
    core = {
        "spec": "urn:crest:trust-check-v1",
        "canon_version": CANON_VERSION,
        "payment_ref": inputs["payment_ref"],
        "subject": inputs["subject"],
        "recommendation": inputs["recommendation"],
        "score": inputs["score"],
        "score_null_reason": inputs["score_null_reason"],
        "evidence_array": inputs["evidence_array"],
        "issued_at_ms": inputs["issued_at_ms"],
        "verifier_did": inputs["verifier_did"],
    }
    return core


def build_joint_receipt(payment: dict, compliance_half: dict, conformance_half: dict) -> dict:
    """Build the joint receipt with joint_ref computed via zero-substitution."""
    receipt_no_ref = {
        "canon_version": CANON_VERSION,
        "compliance": compliance_half,
        "conformance": conformance_half,
        "joint_ref": ZERO_REF,
        "joint_version": JOINT_VERSION,
        "payment": payment,
    }
    joint_ref = jcs_sha256_hex(receipt_no_ref)
    receipt = dict(receipt_no_ref)
    receipt["joint_ref"] = joint_ref
    return receipt


def verify_joint_receipt(receipt: dict) -> dict:
    """Re-derive every content-addressed hash and report results."""
    asserted_joint_ref = receipt["joint_ref"]
    recomputed = dict(receipt)
    recomputed["joint_ref"] = ZERO_REF
    derived_joint_ref = jcs_sha256_hex(recomputed)
    return {
        "asserted_joint_ref": asserted_joint_ref,
        "derived_joint_ref": derived_joint_ref,
        "joint_ref_match": asserted_joint_ref == derived_joint_ref,
        "canon_version_pin_ok": receipt.get("canon_version") == CANON_VERSION,
        "joint_version_pin_ok": receipt.get("joint_version") == JOINT_VERSION,
    }


def run_fixture(fixture_path: Path) -> dict:
    with open(fixture_path, encoding="utf-8") as f:
        fixture = json.load(f)

    inputs = fixture["inputs"]
    expected = fixture["expected"]
    payment = inputs["payment"]

    # AlgoVoi half: build_compliance_receipt
    ce = inputs["compliance_emitter_input"]
    compliance_receipt_full = build_compliance_receipt(
        payer_ref=ce["payer_ref"],
        screen_result=ce["screen_result"],
        screen_timestamp_ms=ce["screen_timestamp_ms"],
        screen_provider_did=ce["screen_provider_did"],
        jurisdiction_flags=ce["jurisdiction_flags"],
    )
    if not isinstance(compliance_receipt_full, dict):
        compliance_receipt_full = compliance_receipt_full.__dict__
    compliance_ref = jcs_sha256_hex(dict(compliance_receipt_full))
    compliance_half = {
        "compliance_ref": compliance_ref,
        "evidence_anchor": ce.get("evidence_anchor", ZERO_REF),
        "jurisdiction_flags": ce["jurisdiction_flags"],
        "provider_did": ce["screen_provider_did"],
        "verdict": ce["screen_result"],
    }

    # Crest half: synthesize trust-check core
    crest_input = inputs["conformance_emitter_input"]
    crest_core = synthesize_crest_trust_receipt(crest_input)
    conformance_ref = jcs_sha256_hex(crest_core)
    conformance_half = {
        "conformance_ref": conformance_ref,
        "evidence_anchor": crest_input.get("evidence_anchor", ZERO_REF),
        "provider_did": crest_input["verifier_did"],
        "recommendation": crest_input["recommendation"],
        "score": crest_input["score"],
        "score_null_reason": crest_input["score_null_reason"],
        "spec": "urn:crest:trust-check-v1",
    }

    # Compose joint
    joint = build_joint_receipt(payment, compliance_half, conformance_half)
    verification = verify_joint_receipt(joint)

    # Compare against expected
    checks = {
        "fixture_id": fixture["id"],
        "compliance_ref_derived": compliance_ref,
        "compliance_ref_expected": expected.get("compliance_ref"),
        "compliance_ref_match": (
            expected.get("compliance_ref") is None or compliance_ref == expected.get("compliance_ref")
        ),
        "conformance_ref_derived": conformance_ref,
        "conformance_ref_expected": expected.get("conformance_ref"),
        "conformance_ref_match": (
            expected.get("conformance_ref") is None or conformance_ref == expected.get("conformance_ref")
        ),
        "joint_ref_derived": joint["joint_ref"],
        "joint_ref_expected": expected.get("joint_ref"),
        "joint_ref_match": (
            expected.get("joint_ref") is None or joint["joint_ref"] == expected.get("joint_ref")
        ),
        "self_verification": verification,
        "joint_receipt": joint,
    }
    return checks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: run all fixtures in ../fixtures/
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        fixture_paths = sorted(fixtures_dir.glob("*.json"))
    else:
        fixture_paths = [Path(p) for p in sys.argv[1:]]

    if not fixture_paths:
        print("No fixtures found.", file=sys.stderr)
        sys.exit(1)

    overall_pass = True
    for fp in fixture_paths:
        print(f"=== {fp.name} ===")
        r = run_fixture(fp)
        for k in ("compliance_ref_match", "conformance_ref_match", "joint_ref_match"):
            ok = r[k]
            if not ok:
                overall_pass = False
            print(f"  {k:25s} {'PASS' if ok else 'FAIL'}")
        sv = r["self_verification"]
        for k in ("joint_ref_match", "canon_version_pin_ok", "joint_version_pin_ok"):
            ok = sv[k]
            if not ok:
                overall_pass = False
            print(f"  self.{k:20s} {'PASS' if ok else 'FAIL'}")
        print(f"  compliance_ref derived: {r['compliance_ref_derived']}")
        print(f"  conformance_ref derived: {r['conformance_ref_derived']}")
        print(f"  joint_ref       derived: {r['joint_ref_derived']}")
        print()

    sys.exit(0 if overall_pass else 1)
