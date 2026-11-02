"""Non-invasive wrapper for the existing PolicyAndAuditEngine.check_policy method.

This adapter records a policy evaluation. It does not replace the policy engine,
does not grant permissions, and does not execute the requested protected action.
"""
from pathlib import Path
import hashlib, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import protocol

def evaluate_policy(engine, action, payload="", cap_mask=0x71451121,
                    ge=1.0, go=1.0, gc=1.0, actor="unverified-caller",
                    request_ref="request-not-authenticated", expected_decision=None):
    opid, _ = protocol.define(
        "PolicyEngine",
        "Evaluate policy for action " + str(action),
        "Policy decision matches expected decision",
        "Policy decision differs from expected decision or evaluation errors",
        actor
    )
    protocol.advance(opid,"BOUND",actor,{
        "resources":["policy-context"],
        "allowed_actions":["evaluate-policy"],
        "denied_actions":["bypass-policy","execute-protected-action"],
        "lease_seconds":300
    })
    protocol.advance(opid,"EXECUTE",actor,{
        "action":"evaluate-policy",
        "authorization_ref":request_ref,
        "execution_note":"Invoke existing policy check only; protected action is not executed"
    })
    try:
        result=engine.check_policy(action,payload,cap_mask,ge,go,gc)
        evidence="memory://policy-result/"+hashlib.sha256(
            json.dumps(result,sort_keys=True).encode()
        ).hexdigest()
        observed=protocol.advance(opid,"OBSERVE",actor,{
            "result":json.dumps(result,sort_keys=True),
            "evidence_refs":[evidence],
            "failure_observed":False
        })
        passed=(expected_decision is not None and result.get("decision")==expected_decision)
        protocol.advance(opid,"VERIFY","protocol-validator",{
            "passed":passed,
            "evidence_refs":["ledger-event://"+observed["event_hash"]],
            "comparison":"actual decision="+str(result.get("decision"))+"; expected="+str(expected_decision)
        })
        classification="CLOSE" if passed else "REFER"
        protocol.advance(opid,"CLASSIFY",actor,{
            "classification":classification,
            "reason":"Policy result recorded; protected action remains unexecuted"
        })
        protocol.advance(opid,"CLOSE",actor,{
            "closure_note":"Policy evaluation receipt closed",
            "temporary_access_released":True,
            "temporary_state_cleared":True,
            "baseline_restored":True
        })
        return {"operation_id":opid,"policy_result":result,"verified":passed}
    except Exception as exc:
        raise RuntimeError("Policy evaluation operation "+opid+" incomplete; inspect its append-only events: "+str(exc)) from exc
