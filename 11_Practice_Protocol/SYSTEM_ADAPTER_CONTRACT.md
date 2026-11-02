# ArcaneXus Subsystem Adapter Contract

Every adapter must call the shared lifecycle engine before and after its own work. The adapter may not grant itself permissions. It must preserve the subsystem's existing human-approval and policy checks.

## Required event payloads

### DEFINE
`system_id`, `intent`, `success_condition`, `failure_condition`, `actor` are required. Optional `parent_operation_id` links a retry to an earlier operation.

### BOUND
```json
{"resources":["test-fixture"],"allowed_actions":["read-status"],"denied_actions":["write-production-state"],"lease_seconds":300}
```

### EXECUTE
```json
{"action":"read-status","authorization_ref":"POLICY-DECISION-REF","execution_ref":"runtime-receipt-id","execution_note":"Read-only status request"}
```
The engine checks the allowlist and records the authorization reference. The subsystem adapter is responsible for actually obtaining and validating authorization before performing work.

### OBSERVE
```json
{"result":"HTTP 200; state ACTIVE","evidence_refs":["receipt://..."],"failure_observed":false}
```

### VERIFY
```json
{"passed":true,"evidence_refs":["receipt://..."],"comparison":"Observed state matches the DEFINE condition"}
```

### CLASSIFY
```json
{"classification":"CLOSE","reason":"The original target was met"}
```
Allowed classifications: `CLOSE`, `REVISE`, `REDUCE`, `ACT`, `WAIT`, `REFER`.

### CLOSE
```json
{"closure_note":"Read-only operation complete","temporary_access_released":true,"temporary_state_cleared":true,"baseline_restored":true}
```

## Current ArcaneXus integration targets

| Target | Required adapter responsibility | Status |
|---|---|---|
| Reality Kernel | Gate state transitions and invariant checks | NOT INTEGRATED |
| Policy Engine | Record DENY / REVIEW / ALLOW decisions and reasons | ADAPTER PROTOTYPE TESTED; CORE NOT HOOKED |
| Capability System | Scope capability, resource and lease | NOT INTEGRATED |
| State Ledger | Link protocol receipts without rewriting legacy records | NOT INTEGRATED |
| Audit System | Validate and export event-chain evidence | NOT INTEGRATED |
| MorningStar | Treat model output as proposal, never authority | NOT INTEGRATED |
| SovScript / SovSh | Compile lifecycle declarations into checked operations | NOT INTEGRATED |
| Familiar Engine / Soul Sucker | Sandbox simulations and preserve deterministic receipts | NOT INTEGRATED |
| AI Cognitive Mesh | Apply the same scope and approval checks to delegated agents | NOT INTEGRATED |
| ArcaneXus Hub | Show operation status and evidence, no self-approval | NOT INTEGRATED |
| Android developer APK | Display lifecycle and invoke authorized APIs | NOT INTEGRATED |
| macOS registration client | Record identity lifecycle and approval evidence | NOT INTEGRATED |
| XCover edge node | Enforce local operation scope and cleanup | NOT INTEGRATED |
| Dell host node | Enforce host-level policy and provenance | NOT INTEGRATED |
| Pixel 7 edge node | Restrict actions to explicitly provisioned capabilities | NOT INTEGRATED |
| WireGuard / network mesh | Scope peers, routes, port exposure and expiry | NOT INTEGRATED |
| Wallet / TriKoinz / SovCoins | Require transaction intent, chain evidence and explicit approval | NOT INTEGRATED |
| Bounty recovery / revenue | Keep claims, approvals and payments as separate verified events | NOT INTEGRATED |
| Coven control plane | Treat seats as roles/UI, not independent authority | NOT INTEGRATED |
| Hardware / HP-HVNR simulations | Separate simulation output from physical measurements | NOT INTEGRATED |
| Dashboard / Control Center | Render observed evidence and uncertainty accurately | NOT INTEGRATED |

This table is an implementation target catalog derived from currently known ArcaneXus components. It does not claim to be the recovered canonical 19-subsystem map. Reconcile it against the authoritative architecture source before locking exact subsystem IDs.

## Integration acceptance tests

1. Every operation has a unique ID and a DEFINE event.
2. BOUND rejects missing scope and lease values above 300 seconds.
3. EXECUTE rejects any action not explicitly allowed.
4. OBSERVE records result and evidence references, including failure.
5. VERIFY references evidence and compares it with the original target.
6. CLASSIFY rejects unknown decisions and rejects CLOSE after failed verification.
7. Every operation receives a CLOSE event before it is considered terminal.
8. Retry creates a new operation ID and links the parent ID.
9. Event history is append-only and hash-chain validation passes.
10. No adapter bypasses existing authority or turns model output into approval.
