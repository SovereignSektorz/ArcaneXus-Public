import tempfile, unittest
from pathlib import Path
import protocol
from adapters.policy_engine_adapter import evaluate_policy

class FakePolicy:
    def __init__(self, decision): self.decision=decision
    def check_policy(self, action, payload="", cap_mask=0, ge=1.0, go=1.0, gc=1.0):
        return {"decision":self.decision,"action":action,"reason":"fixture"}

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old=(protocol.ROOT,protocol.LEDGER,protocol.LOCK)
        protocol.ROOT=Path(self.tmp.name); protocol.LEDGER=protocol.ROOT/"events.jsonl"; protocol.LOCK=protocol.ROOT/".lock"
    def tearDown(self):
        protocol.ROOT,protocol.LEDGER,protocol.LOCK=self.old
        self.tmp.cleanup()
    def test_policy_adapter_records_verified_decision(self):
        result=evaluate_policy(FakePolicy("ALLOW"),"read-status",actor="test-actor",request_ref="test-request",expected_decision="ALLOW")
        self.assertTrue(result["verified"])
        self.assertEqual(protocol.status_report(result["operation_id"])["status"],"CLOSE")
    def test_policy_adapter_refers_unexpected_decision(self):
        result=evaluate_policy(FakePolicy("DENY"),"read-status",actor="test-actor",request_ref="test-request",expected_decision="ALLOW")
        self.assertFalse(result["verified"])
        events=protocol.status_report(result["operation_id"])["events"]
        classification=next(e for e in events if e["event_type"]=="CLASSIFY")
        self.assertEqual(classification["payload"]["classification"],"REFER")

if __name__=="__main__": unittest.main(verbosity=2)
