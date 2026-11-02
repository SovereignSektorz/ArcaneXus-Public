# ArcaneXus Reality Mode / Developer APK Build Report
Date: 2026-11-02
Device: Samsung SM-G715U1 XCover Pro, Android 13, Termux
Project: ~/ArcaneXus/09_AI_Stack_Developer_App

## Build
- Result: PASS
- Version: 0.4.0 (versionCode 4)
- Package: com.arcanexus.aistack.dev
- APK: ~/ArcaneXus/09_AI_Stack_Developer_App/output/ArcaneXus-AI-Stack-Developer-0.4.0.apk
- Downloads copy: ~/storage/downloads/ArcaneXus-AI-Stack-Developer-0.4.0.apk
- SHA-256: 1242ecfca062d6fbb4975c8d22499e5d553dd8b415aa10d12139671f1c54a310
- Signing: PASS; one RSA 2048-bit signer; APK Signature Schemes v1, v2 and v3 verified.
- Signing certificate SHA-256: 88e340db36e4f8017cd010f662aa5199e2ac21eb4674ca142fa1d66d045b443d
- Source and Downloads APK SHA-256 values matched.

## Runtime endpoint observations from XCover
- Practice Protocol API 127.0.0.1:1131: RESPONDED; health JSON reports status OK and execution disabled.
- Reality Control Center 127.0.0.1:1126: HTTP 200.
- ArcaneXus core 127.0.0.1:1121: UNAVAILABLE during this check (connection refused).
- These are point-in-time endpoint checks, not a full subsystem audit.

## Implemented in APK
- Added REALITY status screen and explicit manual probe.
- GET-only checks with bounded connect/read timeouts.
- Displays ONLINE/UNAVAILABLE rather than substituting mock status.
- Added INTERNET permission.
- Cleartext denied by default with a local-loopback network security exception.
- Preserved existing developer keystore and signing-secret file.
- Existing versioned APK artifacts were not overwritten.

## Not verified / not claimed
- APK installation or UI execution on Android.
- Whether Android's network-security policy accepts the loopback IP exceptions on this exact device at runtime.
- End-to-end app-to-service calls from the installed APK.
- Core port 1121 recovery or production integration.
- Reality Mode operation lifecycle fully completed.
- No production service restart or production database modification was performed.
