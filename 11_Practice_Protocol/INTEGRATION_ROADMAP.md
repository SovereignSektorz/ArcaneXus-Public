# ArcaneXus Practice Protocol Integration Roadmap

## Phase 0 — Shared protocol core
Status: IMPLEMENTED AND TESTED
- Schema, append-only event chain, CLI, loopback API, browser console.
- 8/8 unit and adapter tests passed.
- No existing production source or database changed.

## Phase 1 — Governance kernel
Targets: Reality Kernel, Policy Engine, Capability System, State Ledger, Audit System.
- Policy Engine wrapper prototype exists and passes fake-engine tests.
- Next: bind the adapter to the exact active core implementation only after source/runtime provenance is reconciled.
- Add capability lease evidence and state-transition preconditions.
- Add ledger bridge as a parallel receipt stream first; do not merge or rewrite legacy ledger records.
- Require human authority for state-changing actions.

## Phase 2 — Reasoning and language
Targets: MorningStar, SovScript, SovSh, AI Cognitive Mesh, Familiar Engine, Soul Sucker.
- Every model output is a proposal, not an authorization.
- Add operation IDs and evidence references to inference traces.
- Extend the actual SovScript grammar and parser only after compiler fixtures and backward-compatibility tests exist.
- Preserve deterministic simulation ticks and separate simulation from physical measurement.

## Phase 3 — User applications
Targets: ArcaneXus Hub, Android Developer APK, macOS Network Registration, Control Center.
- Add a lifecycle timeline and evidence viewer.
- Use authenticated server APIs for remote devices.
- Do not expose the unauthenticated loopback API over the mesh.
- Keep identity credentials, passwords and tokens out of event payloads.
- Build and sign apps on their native target platforms; Termux is not a macOS build host.

## Phase 4 — Device and network nodes
Targets: XCover, Dell XPS 8700, Pixel 7, WireGuard, SSH, mesh.
- Scope each operation to one node, peer, route and time lease.
- Verify observed device/network state before and after.
- Keep device-specific authority and provenance distinct.
- No route, firewall, boot, service or SSH changes without a separately authorized operation.

## Phase 5 — Economic and physical systems
Targets: Wallet, TriKoinz, SovCoins, bounty recovery, revenue, Coven control plane, HP-HVNR and other hardware prototypes.
- Separate intent, quote, approval, signing, broadcast, confirmation and settlement.
- Never treat a simulated telemetry value as a physical measurement.
- Never treat a bounty estimate or pending claim as paid revenue.
- Coven seats are workflow roles, not independent root authorities.

## Gate for every phase
A phase is complete only when the subsystem adapter exists, integration tests pass against the real subsystem in a safe fixture, event evidence is inspectable, negative tests prove denied actions remain denied, and an authorized reviewer accepts the integration receipt.
