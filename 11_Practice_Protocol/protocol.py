#!/usr/bin/env python3
"""ArcaneXus Practice Protocol v1.0. Append-only lifecycle recorder; never executes payloads."""
from __future__ import annotations
import argparse, hashlib, json, os, secrets, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "practice_events.jsonl"
LOCK = ROOT / ".ledger.lock"
MAX_LEASE = 300
STAGES = ["DEFINE", "BOUND", "EXECUTE", "OBSERVE", "VERIFY", "CLASSIFY", "CLOSE"]
CLASSIFICATIONS = {"CLOSE", "REVISE", "REDUCE", "ACT", "WAIT", "REFER"}

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def load_events():
    if not LEDGER.exists(): return []
    rows = []
    with LEDGER.open("r", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip(): continue
            try: rows.append(json.loads(line))
            except Exception as e: raise RuntimeError(f"Invalid ledger JSON at line {n}: {e}")
    return rows

def verify_chain(rows):
    previous = "0" * 64
    for i, row in enumerate(rows, 1):
        claimed = row.get("event_hash")
        body = {k:v for k,v in row.items() if k != "event_hash"}
        if row.get("sequence") != i: return False, f"sequence mismatch at line {i}"
        if row.get("previous_event_hash") != previous: return False, f"previous hash mismatch at line {i}"
        if digest(body) != claimed: return False, f"event hash mismatch at line {i}"
        previous = claimed
    return True, f"{len(rows)} events verified"

def append_event(operation_id, event_type, actor, payload):
    ROOT.mkdir(parents=True, exist_ok=True)
    fd = None
    try:
        fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise RuntimeError("Ledger writer lock exists. Inspect it; do not delete blindly.")
    try:
        rows = load_events()
        ok, message = verify_chain(rows)
        if not ok: raise RuntimeError("Ledger integrity failure: " + message)
        prev = rows[-1]["event_hash"] if rows else "0" * 64
        body = {
            "schema_version":"1.0.0",
            "sequence":len(rows)+1,
            "event_id":"ANX-EV-" + secrets.token_hex(8).upper(),
            "operation_id":operation_id,
            "event_type":event_type,
            "occurred_at":utcnow(),
            "actor":actor,
            "payload":payload,
            "previous_event_hash":prev
        }
        row = dict(body, event_hash=digest(body))
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        out = os.open(str(LEDGER), flags, 0o600)
        try:
            os.write(out, canonical(row) + b"\n")
            os.fsync(out)
        finally: os.close(out)
        return row
    finally:
        if fd is not None: os.close(fd)
        try: os.unlink(LOCK)
        except FileNotFoundError: pass

def operation_events(rows, opid):
    return [r for r in rows if r.get("operation_id") == opid]

def latest_status(events):
    return events[-1]["event_type"] if events else None

def require_text(value, field, limit=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{field} must be non-empty text (max {limit})")
    return value.strip()

def new_id():
    return "ANX-OP-" + secrets.token_hex(8).upper()

def define(system_id, intent, success, failure, actor, parent=None):
    system_id = require_text(system_id, "system_id", 128)
    intent = require_text(intent, "intent")
    success = require_text(success, "success_condition")
    failure = require_text(failure, "failure_condition")
    actor = require_text(actor, "actor", 128)
    if parent:
        rows = load_events()
        if not operation_events(rows, parent): raise ValueError("parent operation does not exist")
    opid = new_id()
    row = append_event(opid, "DEFINE", actor, {
        "system_id":system_id, "intent":intent, "success_condition":success,
        "failure_condition":failure, "parent_operation_id":parent
    })
    return opid, row

def advance(opid, stage, actor, data):
    actor = require_text(actor, "actor", 128)
    rows = load_events()
    ok, message = verify_chain(rows)
    if not ok: raise RuntimeError("Ledger integrity failure: " + message)
    events = operation_events(rows, opid)
    if not events: raise ValueError("unknown operation_id")
    status = latest_status(events)
    expected = {
        "BOUND":"DEFINE", "EXECUTE":"BOUND", "OBSERVE":"EXECUTE",
        "VERIFY":"OBSERVE", "CLASSIFY":"VERIFY", "CLOSE":"CLASSIFY"
    }
    if stage not in expected: raise ValueError("unsupported stage")
    if status != expected[stage]:
        raise ValueError(f"{stage} requires previous stage {expected[stage]}; current={status}")
    if stage == "BOUND":
        resources = data.get("resources", [])
        allowed = data.get("allowed_actions", [])
        denied = data.get("denied_actions", [])
        lease = data.get("lease_seconds")
        if not all(isinstance(x, list) and all(isinstance(v,str) and v.strip() for v in x) for x in [resources,allowed,denied]):
            raise ValueError("resources, allowed_actions and denied_actions must be string arrays")
        if not isinstance(lease,int) or lease < 1 or lease > MAX_LEASE:
            raise ValueError(f"lease_seconds must be 1..{MAX_LEASE}")
        if set(allowed) & set(denied): raise ValueError("an action cannot be both allowed and denied")
        data = {"resources":resources,"allowed_actions":allowed,"denied_actions":denied,"lease_seconds":lease}
    elif stage == "EXECUTE":
        action = require_text(data.get("action"), "action", 256)
        auth = require_text(data.get("authorization_ref"), "authorization_ref", 256)
        bound = events[-1]["payload"]
        if action not in bound["allowed_actions"] or action in bound["denied_actions"]:
            raise PermissionError("action is outside the declared allowlist")
        data = {"action":action,"authorization_ref":auth,"execution_ref":data.get("execution_ref"),
                "execution_note":require_text(data.get("execution_note","Execution delegated to subsystem adapter"),"execution_note",1000)}
    elif stage == "OBSERVE":
        data = {"result":require_text(data.get("result"),"observed result"),
                "evidence_refs":data.get("evidence_refs",[]),
                "failure_observed":bool(data.get("failure_observed",False))}
        if not isinstance(data["evidence_refs"],list): raise ValueError("evidence_refs must be an array")
    elif stage == "VERIFY":
        if not isinstance(data.get("passed"),bool): raise ValueError("passed must be boolean")
        refs = data.get("evidence_refs",[])
        if not isinstance(refs,list) or not refs or not all(isinstance(x,str) and x.strip() for x in refs):
            raise ValueError("verification requires at least one evidence reference")
        data = {"passed":data["passed"],"evidence_refs":refs,
                "comparison":require_text(data.get("comparison"),"comparison")}
    elif stage == "CLASSIFY":
        choice = str(data.get("classification","")).upper()
        if choice not in CLASSIFICATIONS: raise ValueError("classification must be CLOSE, REVISE, REDUCE, ACT, WAIT or REFER")
        verified = events[-1]["payload"]["passed"]
        if choice == "CLOSE" and not verified: raise ValueError("failed verification cannot be classified CLOSE")
        data = {"classification":choice,"reason":require_text(data.get("reason"),"classification reason"),
                "verified_pass":verified}
    elif stage == "CLOSE":
        data = {"closure_note":require_text(data.get("closure_note"),"closure_note"),
                "temporary_access_released":data.get("temporary_access_released"),
                "temporary_state_cleared":data.get("temporary_state_cleared"),
                "baseline_restored":data.get("baseline_restored"),
                "record_preserved":True}
        for key in ["temporary_access_released","temporary_state_cleared","baseline_restored"]:
            if not isinstance(data[key],bool): raise ValueError(key + " must be explicitly true or false")
        if not data["record_preserved"]: raise ValueError("record preservation is mandatory")
    return append_event(opid, stage, actor, data)

def status_report(opid=None):
    rows = load_events()
    ok, message = verify_chain(rows)
    if not ok: raise RuntimeError("Ledger integrity failure: " + message)
    if opid:
        events = operation_events(rows, opid)
        return {"integrity":message,"operation_id":opid,"status":latest_status(events),
                "events":events}
    ids = list(dict.fromkeys(r["operation_id"] for r in rows))
    return {"integrity":message,"operations":[
        {"operation_id":oid,"status":latest_status(operation_events(rows,oid)),
         "system_id":next((e["payload"].get("system_id") for e in operation_events(rows,oid) if e["event_type"]=="DEFINE"),None)}
        for oid in ids]}

def main():
    ap=argparse.ArgumentParser(description="ArcaneXus Practice Protocol lifecycle recorder")
    sub=ap.add_subparsers(dest="cmd",required=True)
    d=sub.add_parser("define"); d.add_argument("--system",required=True); d.add_argument("--intent",required=True)
    d.add_argument("--success",required=True); d.add_argument("--failure",required=True); d.add_argument("--actor",required=True); d.add_argument("--parent")
    for name in ["bound","execute","observe","verify","classify","close"]:
        q=sub.add_parser(name); q.add_argument("operation_id"); q.add_argument("--actor",required=True); q.add_argument("--json",required=True)
    s=sub.add_parser("status"); s.add_argument("--operation")
    v=sub.add_parser("verify-ledger")
    args=ap.parse_args()
    try:
        if args.cmd=="define":
            oid,row=define(args.system,args.intent,args.success,args.failure,args.actor,args.parent)
            print(json.dumps({"operation_id":oid,"status":"DEFINE","event_hash":row["event_hash"]},indent=2))
        elif args.cmd=="status": print(json.dumps(status_report(args.operation),indent=2))
        elif args.cmd=="verify-ledger":
            ok,msg=verify_chain(load_events()); print(json.dumps({"valid":ok,"result":msg},indent=2)); sys.exit(0 if ok else 2)
        else:
            data=json.loads(args.json)
            row=advance(args.operation_id,args.cmd.upper(),args.actor,data)
            print(json.dumps({"operation_id":args.operation_id,"stage":row["event_type"],"event_hash":row["event_hash"]},indent=2))
    except Exception as exc:
        print(json.dumps({"error":str(exc)},indent=2),file=sys.stderr); sys.exit(2)

if __name__=="__main__": main()
