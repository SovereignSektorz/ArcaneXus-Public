# SPEC-ANX-PRACTICE-PROTOCOL-001

**Status:** Canonical operational standard proposed for adoption  
**Lifecycle:** Active as a local protocol implementation; subsystem integrations remain staged  
**Authority:** 1121 ROOT

## Governing rule

Shortcuts may reduce effort, but they may never remove verification, responsibility, or auditability.

## Lifecycle

`DEFINE -> BOUND -> EXECUTE -> OBSERVE -> VERIFY -> CLASSIFY -> CLOSE`

Every operation has one immutable ID. A retry is a new operation with `parent_operation_id`; it never rewrites the previous record. Events are append-only JSONL records linked by SHA-256. Chain verification detects changed, missing, reordered or inserted records. This is tamper-evident, not a digital signature or proof against an attacker who can rewrite the entire ledger and recompute every hash.

## Implemented files

- `operation.schema.json`: machine-readable operation envelope.
- `protocol.py`: lifecycle validator, CLI and append-only event ledger.
- `protocol_server.py`: loopback-only HTTP API.
- `console.html`: local browser console served by the API.
- `run_console.sh`: foreground launcher for the local console.
- `adapters/python_adapter.py`: starter adapter for Python subsystems.
- `adapters/policy_engine_adapter.py`: non-invasive wrapper prototype for policy evaluations.
- `test_protocol.py` and `test_adapters.py`: isolated lifecycle, integrity and adapter tests.
- `SYSTEM_ADAPTER_CONTRACT.md`: rules for subsystem integrations.

## Safety boundaries

- The engine records an authorized action; it does not execute arbitrary shell commands, code, hardware operations or network changes.
- `BOUND.lease_seconds` is clamped to 1..300 seconds.
- Execution records require an action on the declared allowlist and an authorization reference. The engine does NOT authenticate the actor or validate that reference against the Policy Engine; it records caller-supplied claims only. A real adapter must independently authenticate the principal and verify policy before acting.
- `CLOSE` classification is rejected after failed verification.
- Closure requires explicit values for temporary access release, temporary-state cleanup and baseline restoration.
- Every close preserves the historical record.
- The event ledger is separate from `~/ArcaneXus/ledger/unified_state_ledger.jsonl`; no automatic ledger migration or merge occurs.
- No existing runtime, boot script, production database, network service or device permission is changed by this package.

## CLI

```bash
cd ~/ArcaneXus/11_Practice_Protocol
python protocol.py define --system RealityKernel --intent "Check one policy invariant" --success "Invariant passes" --failure "Invariant fails" --actor "1121_ROOT"
python protocol.py status
python protocol.py verify-ledger
```

Each stage after DEFINE is a separate command. See `SYSTEM_ADAPTER_CONTRACT.md` for payloads. A caller must capture the operation ID printed by DEFINE and pass it to every later stage.

## Verification performed

On XCover Pro Termux, `python3 -m unittest -v test_protocol.py` passed 6/6 tests: full lifecycle, allowlist enforcement, failed verification close rejection, lease clamp, hash tamper detection and new-operation retry lineage.

## Integration status

The protocol core is implemented and tested in isolation. It is not yet wired into Reality Kernel, Policy Engine, Capability System, State Ledger, Audit System, MorningStar, SovScript, SovSh, Android APK, Mac app, Hub, Dell node, XCover node, mesh, wallet, bounty recovery, revenue, Coven or hardware simulations. Those require subsystem-specific adapters and separate verification. Do not mark them compliant merely because this shared engine exists.

## Local browser console

Run in Termux:

```bash
cd ~/ArcaneXus/11_Practice_Protocol
bash run_console.sh
```

Then open `http://127.0.0.1:1131/` in the same device browser. Keep the server bound to loopback. Stop it with Ctrl-C. Do not expose this unauthenticated metadata API to another device.
