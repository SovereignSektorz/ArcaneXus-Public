import tempfile, unittest
from pathlib import Path
import protocol

class PracticeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_root,self.old_ledger,self.old_lock=protocol.ROOT,protocol.LEDGER,protocol.LOCK
        protocol.ROOT=Path(self.tmp.name)
        protocol.LEDGER=protocol.ROOT/"events.jsonl"
        protocol.LOCK=protocol.ROOT/".lock"
    def tearDown(self):
        protocol.ROOT,protocol.LEDGER,protocol.LOCK=self.old_root,self.old_ledger,self.old_lock
        self.tmp.cleanup()
    def op(self):
        return protocol.define("RealityKernel","verify policy gate","gate result matches expected","mismatch or missing evidence","human:1121")[0]
    def bound(self,oid,lease=300):
        return protocol.advance(oid,"BOUND","human:1121",{"resources":["test-fixture"],"allowed_actions":["run-test"],"denied_actions":["production-write"],"lease_seconds":lease})
    def test_full_pass(self):
        oid=self.op(); self.bound(oid)
        protocol.advance(oid,"EXECUTE","adapter:test",{"action":"run-test","authorization_ref":"AUTH-TEST-1"})
        protocol.advance(oid,"OBSERVE","adapter:test",{"result":"gate accepted","evidence_refs":["test://result/1"]})
        protocol.advance(oid,"VERIFY","validator:test",{"passed":True,"evidence_refs":["test://result/1"],"comparison":"observed result equals target"})
        protocol.advance(oid,"CLASSIFY","human:1121",{"classification":"CLOSE","reason":"target met"})
        protocol.advance(oid,"CLOSE","human:1121",{"closure_note":"closed","temporary_access_released":True,"temporary_state_cleared":True,"baseline_restored":True})
        self.assertEqual(protocol.status_report(oid)["status"],"CLOSE")
        self.assertTrue(protocol.verify_chain(protocol.load_events())[0])
    def test_allowlist_blocks_action(self):
        oid=self.op(); self.bound(oid)
        with self.assertRaises(PermissionError):
            protocol.advance(oid,"EXECUTE","adapter:test",{"action":"production-write","authorization_ref":"none"})
    def test_lease_clamped(self):
        oid=self.op()
        with self.assertRaises(ValueError): self.bound(oid,301)
    def test_failed_verify_cannot_close(self):
        oid=self.op(); self.bound(oid)
        protocol.advance(oid,"EXECUTE","adapter:test",{"action":"run-test","authorization_ref":"AUTH-TEST-2"})
        protocol.advance(oid,"OBSERVE","adapter:test",{"result":"target missed","evidence_refs":["test://result/2"]})
        protocol.advance(oid,"VERIFY","validator:test",{"passed":False,"evidence_refs":["test://result/2"],"comparison":"target not met"})
        with self.assertRaises(ValueError):
            protocol.advance(oid,"CLASSIFY","human:1121",{"classification":"CLOSE","reason":"incorrect close"})
    def test_hash_tamper_detected(self):
        oid=self.op()
        rows=protocol.load_events(); rows[0]["payload"]["intent"]="rewritten"
        self.assertFalse(protocol.verify_chain(rows)[0])
    def test_retry_is_new_operation(self):
        first=self.op()
        second,_=protocol.define("RealityKernel","retry policy gate","gate passes","gate fails","human:1121",parent=first)
        self.assertNotEqual(first,second)
        self.assertEqual(protocol.status_report(first)["status"],"DEFINE")

if __name__=="__main__": unittest.main(verbosity=2)
