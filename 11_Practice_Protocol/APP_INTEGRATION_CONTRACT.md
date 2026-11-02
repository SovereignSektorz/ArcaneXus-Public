# Application Integration Contract

All ArcaneXus apps use the same lifecycle API contract; none embeds a second, divergent state machine.

## Local API
- GET /api/v1/practice/health
- GET /api/v1/practice/operations
- GET /api/v1/practice/operations/{operation_id}
- POST /api/v1/practice/operations creates DEFINE
- POST /api/v1/practice/operations/{operation_id}/{stage} appends one stage

The current API facade binds only to 127.0.0.1 and defaults to port 1131. It has no remote authentication and must never be exposed through Wi-Fi, WireGuard, public IP, reverse proxy or a tunnel. It records workflow metadata only and does not execute the described action. The actor field and authorization reference are caller-supplied labels, not authenticated identity or verified policy decisions. Never use this facade as an authority gate.

## Android Hub / Developer APK
- Add a lifecycle view showing operation ID, current stage, classification and evidence references.
- The Android app must call a future authenticated adapter endpoint, not the loopback API from a remote device.
- Keep existing APK permissions and signing identity unchanged until a separately reviewed build.
- No Android source or APK has been modified by this protocol package.

## macOS Network Registration client
- Registration, login, approval and revocation are identity operations.
- Each identity operation should create a lifecycle record in the identity backend after authentication and server-side authorization.
- The current macOS source has no lifecycle API integration yet.
- Do not send passwords, bootstrap tokens, session tokens or private keys into lifecycle event payloads.

## Control Center / Web interfaces
- The current local console is served from the same loopback origin as the protocol API.
- It is an operator interface for recording stages, not a general-purpose remote admin panel.
- Render only server-returned events and clearly label missing evidence and offline state.

## MorningStar / agent clients
- Model proposals are inputs to DEFINE or REVIEW only.
- A model cannot author an authorization reference that the Policy Engine has not independently validated.
- Agent-generated actions remain proposals until a human or existing trusted policy authority authorizes them.
