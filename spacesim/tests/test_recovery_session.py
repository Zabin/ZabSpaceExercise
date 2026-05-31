"""Safe-mode recovery wired through the session layer (`begin_recovery` / `recovery_status`).

The engine RecoverySystem is unit-tested in test_recovery.py; this checks the SessionManager seam
the UI recovery strip (§5.5) uses: fog, the safed precondition, the multi-pass chain executing over
real command windows, re-safe while the root cause persists, recovery sticking once patched — all
while staying replay-safe. Built on the training-basics vignette (Blue ISR-EO-1 + station GS-TRN).
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.bus import enter_safe_mode
from spacesim.session.manager import SessionManager


def _mgr(difficulty="quick", patched=False):
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.recovery.difficulty = difficulty       # control the pass count for the test
    sat = mgr.world.assets["ISR-EO-1"]
    sat.cyber_vulnerabilities = [{"vector": "ground_modem", "patchable": True, "patched": patched}]
    enter_safe_mode(sat.bus_state, now=mgr.sim.clock.now, cause="cyber")
    mgr.sim._initial_state = mgr.world.model_dump()   # re-baseline AFTER safing so replay reproduces it
    mgr.start()
    return mgr


def test_recovery_status_reports_safe_mode_and_fog():
    mgr = _mgr()
    st = mgr.recovery_status("blue", "ISR-EO-1")
    assert st["safe_mode"] is True and st["passes_needed"] == 1 and st["blocked_reason"] is None
    assert st["steps"][0] == "establish_contact" and st["steps"][-1] == "verify_nominal"
    assert mgr.recovery_status("red", "ISR-EO-1") is None      # fog: not Red's asset


def test_begin_recovery_requires_safed_asset():
    mgr = _mgr()
    sat = mgr.world.assets["ISR-EO-1"].bus_state
    sat.mode = "nominal"; sat.safe_mode.active = False
    assert mgr.begin_recovery("blue", "ISR-EO-1", "GS-TRN")["reason"] == "not_safed"
    assert mgr.begin_recovery("red", "ISR-EO-1", "GS-TRN")["reason"] == "not_owner"


def test_recovery_resafes_until_patched_then_sticks_and_replays():
    mgr = _mgr(difficulty="quick", patched=False)
    res = mgr.begin_recovery("blue", "ISR-EO-1", "GS-TRN")
    assert res["ok"], res
    mgr.advance_to(res["finish_at"] + 1)
    st = mgr.recovery_status("blue", "ISR-EO-1")
    assert st["safe_mode"] is True and st["blocked_reason"] is not None    # re-safed: root cause persists
    # Recovery is replay-safe (confirm/finish fired as logged events).
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()

    # Patch the vulnerability, recover again → it sticks.
    for v in mgr.world.assets["ISR-EO-1"].cyber_vulnerabilities:
        v["patched"] = True
    res2 = mgr.begin_recovery("blue", "ISR-EO-1", "GS-TRN")
    assert res2["ok"], res2
    mgr.advance_to(res2["finish_at"] + 1)
    assert mgr.world.assets["ISR-EO-1"].bus_state.mode == "nominal"
