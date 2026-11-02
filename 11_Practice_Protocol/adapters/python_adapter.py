"""Minimal Python adapter. The caller executes its own action only after local policy approval."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import protocol

class PracticeOperation:
    def __init__(self, system_id, intent, success, failure, actor, parent=None):
        self.operation_id, _ = protocol.define(system_id,intent,success,failure,actor,parent)
        self.actor=actor
    def bound(self, resources, allowed_actions, denied_actions, lease_seconds=300):
        return protocol.advance(self.operation_id,"BOUND",self.actor,{
            "resources":resources,"allowed_actions":allowed_actions,
            "denied_actions":denied_actions,"lease_seconds":lease_seconds})
    def record_execution(self, action, authorization_ref, execution_ref=None, note="Adapter executed approved action"):
        return protocol.advance(self.operation_id,"EXECUTE",self.actor,{
            "action":action,"authorization_ref":authorization_ref,
            "execution_ref":execution_ref,"execution_note":note})
    def observe(self, result, evidence_refs, failure_observed=False):
        return protocol.advance(self.operation_id,"OBSERVE",self.actor,{
            "result":result,"evidence_refs":evidence_refs,"failure_observed":failure_observed})
    def verify(self, passed, evidence_refs, comparison):
        return protocol.advance(self.operation_id,"VERIFY",self.actor,{
            "passed":passed,"evidence_refs":evidence_refs,"comparison":comparison})
    def classify(self, classification, reason):
        return protocol.advance(self.operation_id,"CLASSIFY",self.actor,{
            "classification":classification,"reason":reason})
    def close(self, note, access_released, temp_cleared, baseline_restored):
        return protocol.advance(self.operation_id,"CLOSE",self.actor,{
            "closure_note":note,"temporary_access_released":access_released,
            "temporary_state_cleared":temp_cleared,"baseline_restored":baseline_restored})
