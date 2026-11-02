# SovScript / SovSh Binding Design

This document defines a language-neutral binding contract. It does not claim to implement or reserve SovScript keywords. Exact grammar must be reconciled against the current SovScript parser before compiler changes.

```text
PRACTICE <operation-name>
  DEFINE
    SYSTEM <system-id>
    INTENT <atomic-intention>
    SUCCESS <measurable-condition>
    FAILURE <observable-failure>
  BOUND
    RESOURCES <explicit-resource-list>
    ALLOW <explicit-action-list>
    DENY <explicit-denial-list>
    LEASE <= 300s
  EXECUTE
    ACTION <allowlisted-action>
    AUTHORIZATION <verified-policy-reference>
  OBSERVE
    RESULT <actual-result>
    EVIDENCE <immutable-evidence-reference>
  VERIFY
    TARGET <original-success-condition>
    RESULT <pass-or-fail>
  CLASSIFY <CLOSE|REVISE|REDUCE|ACT|WAIT|REFER>
  CLOSE
    RELEASE_ACCESS
    CLEAR_TEMPORARY_STATE
    RESTORE_BASELINE
    PRESERVE_HISTORY
END
```

Compiler requirements:
1. Reject a missing DEFINE target, failure condition, BOUND scope or lease.
2. Reject any lease over 300 seconds.
3. Reject EXECUTE unless the action is allowlisted and the policy reference is verified by the actual Policy Engine.
4. Require OBSERVE and VERIFY evidence references.
5. Reject CLOSE classification after failed verification.
6. Require a new operation ID for every retry.
7. Never permit ledger history rewrite.
8. Treat unknown syntax and unknown authority as DENY or REVIEW according to the existing Policy Engine; never silently coerce them to ALLOW.
