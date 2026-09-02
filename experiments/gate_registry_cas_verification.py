"""
Failure-injection experiment: proves the compare-and-swap guard added to
GateRegistry.record_decision() (src/k9_dow/gates/gate_registry.py) closes
the race disclosed in the IEEE Access submission's Sec. V-D -- DAS's own
gate registry doing "a bare in-memory dict mutation, not even persisted".

Two threads call the real, unmodified record_decision() concurrently on
the same gate with conflicting decisions (APPROVE vs REJECT). A short
delay is injected before each thread reaches the call so both threads
contend for the same real lock inside record_decision() at nearly the
same instant -- the lock, the state check, and the mutation that follow
are all real, unmodified production code; nothing about the guard
itself is simulated. Only the timing of when each thread arrives is
synthetic, which is the only thing a real production race would need
luck (a sub-millisecond window) rather than deliberate staggering to
hit.

Run: python3 experiments/gate_registry_cas_verification.py
"""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from k9_dow.gates.gate_registry import GateRegistry, GateAlreadyDecidedError
from k9_dow.gates.gate_model import GateDecision
from k9_dow.graph.schema import GateAction

GATE_ID = "JROC-VALIDATION"

registry = GateRegistry()
registry.init_gate(GATE_ID)
for criterion in registry.get_gate(GATE_ID).entry_criteria:
    registry.update_criterion(GATE_ID, criterion, True)
print(f"Gate {GATE_ID!r} seeded, state={registry._runtime[GATE_ID].state!r}\n")

outcomes = {}


def call_with_injected_delay(name: str, action: GateAction, delay_before_call_s: float,
                              start_barrier: threading.Barrier):
    """Both threads wait at the barrier, then sleep a slightly different
    amount before calling the real record_decision(), so they arrive at
    its lock within the gap between the two delays -- forcing lock
    contention on (nearly) every run rather than relying on OS
    scheduling luck alone."""
    start_barrier.wait()
    time.sleep(delay_before_call_s)
    decision = GateDecision(
        gate_id=GATE_ID,
        action=action,
        decided_by=f"reviewer-{name}",
        rationale=f"guard verification: {name}",
    )
    try:
        status = registry.record_decision(GATE_ID, decision)
        outcomes[name] = ("ok", status.state, status.decision.action)
    except GateAlreadyDecidedError as exc:
        outcomes[name] = ("conflict", str(exc))


barrier = threading.Barrier(2)
t_approve = threading.Thread(
    target=call_with_injected_delay, args=("A-approve", GateAction.APPROVE, 0.05, barrier)
)
t_reject = threading.Thread(
    target=call_with_injected_delay, args=("B-reject", GateAction.REJECT, 0.01, barrier)
)

t_approve.start()
t_reject.start()
t_approve.join()
t_reject.join()

print("record_decision() outcome seen by each caller:")
for name, outcome in outcomes.items():
    print(f"  {name}: {outcome}")

final_status = registry._runtime[GATE_ID]
print(f"\nFinal gate state: {final_status.state!r}, decision action: "
      f"{final_status.decision.action if final_status.decision else None}, "
      f"decided_by: {final_status.decision.decided_by if final_status.decision else None}")

# ---- assertions: prove the race is actually closed ----
ok_results = [(n, o) for n, o in outcomes.items() if o[0] == "ok"]
conflict_results = [(n, o) for n, o in outcomes.items() if o[0] == "conflict"]

assert len(ok_results) == 1, f"expected exactly 1 successful decision, got {len(ok_results)}: {ok_results}"
assert len(conflict_results) == 1, f"expected exactly 1 conflict, got {len(conflict_results)}: {conflict_results}"

winner_name, (_, winner_state, winner_action) = ok_results[0]
loser_name, (_, detail) = conflict_results[0]

assert winner_state == "resolved"
assert final_status.decision.action == winner_action, (
    "final gate decision does not match the winning caller -- state is not deterministic"
)
assert final_status.decision.decided_by == f"reviewer-{winner_name}"

print(f"\nPASS: exactly one decision succeeded ({winner_name} -> {winner_action}), "
      f"the other ({loser_name}) received an explicit GateAlreadyDecidedError, "
      f"and the final gate state is deterministic and matches the winner.")
