"""IP-1160 (FS-116; FR-3510/FR-3520, ADS-3500) — role-scoped command enforcement.

A Role Assignment (IP-1151) binds an *operator seat* to {asset-or-group, bus|payload|both}. The
gate runs in ``SessionManager.issue_order`` / ``validate_order`` before ``OrderSystem`` is touched:
an order that names its operator ``seat`` and targets a role-gated asset is refused when the seat
is not assigned to that asset or the verb belongs to the other role. A refusal is a normal rejected
``OrderAck``; it registers no order, consumes no order id and writes no event-log entry.

"Operator seat" (the key of ``role_assignments``) is NOT the console seat (``cell`` = white/blue/red/
observer): the console-seat rules (Observer 403, White-only controls) run first and are unchanged.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from spacesim.content.vignette import RoleRequirement, list_vignettes, load_vignette
from spacesim.engine.buscommands import BUS_VERBS, COMMAND_VERBS, DEFENSE_VERBS, PAYLOAD_VERBS
from spacesim.engine.orders import Order
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import ROLE_SCOPE_BY_VERB, SessionManager
from spacesim.ui_web.server import create_app

pytestmark = pytest.mark.verifies("FR-3520")

SAT = "ISR-EO-1"
BUS_DEF = {"def.frequency_hop", "def.patch_cyber", "def.set_threat_warning", "def.maneuver_evade",
           "def.escort_posture", "def.disperse"}
PAYLOAD_DEF = {"def.harden", "def.set_deception_mode"}
ROLE_CODES = {"role_scope_not_assigned", "role_scope_out_of_scope"}


def _mgr(roles=(("ISR-EO-1", "both"),), *, group=None, seed=1, start=True) -> SessionManager:
    vig = load_vignette("leo-isr-denial").model_copy(update={
        "roles_needed": [RoleRequirement(asset_or_constellation=a, role=r, mandatory=False)
                         for a, r in roles]})
    mgr = SessionManager(vig, seed=seed)
    if group:
        mgr.sim.world.assets[SAT].group = group
    if start:
        mgr.start()
    return mgr


def _cmd(verb, actor=SAT, **params):
    return Order(cell="blue", actor=actor, action="command", params={"verb": verb, "via": "GS-NORTH", **params})


def _snapshot(mgr):
    return (len(mgr.osys.orders), mgr.osys._order_counter, len(mgr.sim.eventlog.entries),
            json.dumps(mgr.sim.eventlog.model_dump(), sort_keys=True, default=str))


def _refused_without_trace(mgr, verb, seat, code, actor=SAT):
    before = _snapshot(mgr)
    ack = mgr.issue_order("blue", _cmd(verb, actor), seat=seat)
    assert ack.ok is False and ack.status == "rejected" and ack.reason == code, ack
    assert not ack.id
    assert _snapshot(mgr) == before
    return ack


def _not_role_refused(mgr, verb, seat):
    ack = mgr.issue_order("blue", _cmd(verb), seat=seat)
    assert ack.reason not in ROLE_CODES, (verb, ack)
    return ack


# -- 1-5: scope matrix -----------------------------------------------------------------------------
def test_01_bus_only_seat_cannot_send_a_payload_verb_and_leaves_no_trace():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    _refused_without_trace(mgr, "isr.collect_now", "bus-op", "role_scope_out_of_scope")


def test_02_bus_only_seat_cannot_send_the_two_payload_scoped_defense_verbs():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    for verb in sorted(PAYLOAD_DEF):
        _refused_without_trace(mgr, verb, "bus-op", "role_scope_out_of_scope")


def test_03_bus_only_seat_is_not_role_refused_for_bus_verbs_and_the_six_bus_defense_verbs():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    for verb in ["eps.shed_load", *sorted(BUS_DEF)]:
        _not_role_refused(mgr, verb, "bus-op")


def test_04_payload_only_seat_mirrors_the_bus_only_seat():
    mgr = _mgr()
    mgr.assign_role("pl-op", SAT, "payload")
    _refused_without_trace(mgr, "eps.shed_load", "pl-op", "role_scope_out_of_scope")
    for verb in sorted(BUS_DEF):
        _refused_without_trace(mgr, verb, "pl-op", "role_scope_out_of_scope")
    for verb in ["isr.collect_now", *sorted(PAYLOAD_DEF)]:
        _not_role_refused(mgr, verb, "pl-op")


def test_05_both_seat_is_never_role_refused_for_any_command_verb():
    mgr = _mgr()
    mgr.assign_role("all-op", SAT, "both")
    for verb in sorted(COMMAND_VERBS):
        ack = mgr.issue_order("blue", _cmd(verb), seat="all-op")
        assert ack.reason not in ROLE_CODES, (verb, ack)


# -- 6-9: assignment resolution --------------------------------------------------------------------
def test_06_a_seat_with_no_binding_is_not_assigned():
    mgr = _mgr()
    _refused_without_trace(mgr, "eps.shed_load", "nobody", "role_scope_not_assigned")


def test_07_a_seat_bound_to_a_different_asset_is_not_assigned():
    mgr = _mgr()
    mgr.assign_role("other-op", "SOME-OTHER-SAT", "both")
    _refused_without_trace(mgr, "eps.shed_load", "other-op", "role_scope_not_assigned")


def test_08_a_seat_bound_to_a_group_id_covers_the_assets_in_that_group():
    mgr = _mgr(roles=(("GRP-A", "both"),), group="GRP-A")
    mgr.assign_role("grp-bus", "GRP-A", "bus")
    _not_role_refused(mgr, "eps.shed_load", "grp-bus")
    _refused_without_trace(mgr, "isr.collect_now", "grp-bus", "role_scope_out_of_scope")


def test_09_an_unknown_role_value_grants_nothing_fail_closed():
    mgr = _mgr()
    mgr.assign_role("admin-op", SAT, "admin")
    _refused_without_trace(mgr, "eps.shed_load", "admin-op", "role_scope_not_assigned")


# -- 10-12: no gate -> byte-identical --------------------------------------------------------------
def test_10_an_omitted_or_empty_seat_skips_the_gate_and_acks_exactly_as_before():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    twin = _mgr()
    a0 = twin.issue_order("blue", _cmd("isr.collect_now"))
    for seat in (None, ""):
        m = _mgr()
        m.assign_role("bus-op", SAT, "bus")
        a = m.issue_order("blue", _cmd("isr.collect_now"), seat=seat)
        assert a == a0 and a.ok is True
        assert _snapshot(m) == _snapshot(twin)


def test_11_an_asset_no_roles_needed_entry_covers_is_not_gated_even_with_a_seat():
    mgr = _mgr(roles=(("SOME-OTHER-SAT", "both"),))
    twin = _mgr(roles=(("SOME-OTHER-SAT", "both"),))
    a = mgr.issue_order("blue", _cmd("isr.collect_now"), seat="whoever")
    assert a == twin.issue_order("blue", _cmd("isr.collect_now")) and a.ok is True
    assert _snapshot(mgr) == _snapshot(twin)


def test_12_base_actions_are_never_role_gated():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    for action, params in (("maneuver", {"dv": [0.1, 0, 0], "via": "GS-NORTH"}),
                           ("observe", {"intent": "characterize"}),
                           ("jam", {})):
        o = Order(cell="blue", actor=SAT, action=action, target="RED-ASAT", params=params)
        assert mgr.issue_order("blue", o, seat="bus-op").reason not in ROLE_CODES
        # even a seat with no binding at all: the base actions are out of FS-116's scope
        o = Order(cell="blue", actor=SAT, action=action, target="RED-ASAT", params=params)
        assert mgr.issue_order("blue", o, seat="nobody").reason not in ROLE_CODES


# -- 13: dry-run mirror ----------------------------------------------------------------------------
def test_13_validate_order_mirrors_the_refusals_and_registers_nothing():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    before = _snapshot(mgr)
    a = mgr.validate_order("blue", _cmd("isr.collect_now"), seat="bus-op")
    assert (a.ok, a.reason, a.status) == (False, "role_scope_out_of_scope", "rejected")
    a = mgr.validate_order("blue", _cmd("eps.shed_load"), seat="nobody")
    assert (a.ok, a.reason) == (False, "role_scope_not_assigned")
    a = mgr.validate_order("blue", _cmd("isr.collect_now"))             # no seat: as today
    assert a.ok is True
    assert _snapshot(mgr) == before


# -- 14: table partition ---------------------------------------------------------------------------
def test_14_the_scope_table_partitions_the_command_catalog():
    assert set(ROLE_SCOPE_BY_VERB) == COMMAND_VERBS
    assert set(ROLE_SCOPE_BY_VERB.values()) == {"bus", "payload"}
    assert {v for v in DEFENSE_VERBS if ROLE_SCOPE_BY_VERB[v] == "bus"} == BUS_DEF
    assert {v for v in DEFENSE_VERBS if ROLE_SCOPE_BY_VERB[v] == "payload"} == PAYLOAD_DEF
    assert all(ROLE_SCOPE_BY_VERB[v] == "bus" for v in BUS_VERBS)
    assert all(ROLE_SCOPE_BY_VERB[v] == "payload" for v in PAYLOAD_VERBS)


# -- 15: persistence -------------------------------------------------------------------------------
def test_15_role_assignments_survive_save_and_load_and_an_old_save_loads_empty():
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    state = json.loads(json.dumps(mgr.save_state()))
    assert state["role_assignments"] == {"bus-op": {"asset_or_constellation": SAT, "role": "bus"}}
    SessionManager.validate_save(state)
    back = SessionManager.from_state(state)
    assert back.role_assignments == mgr.role_assignments
    _refused_without_trace(back, "isr.collect_now", "bus-op", "role_scope_out_of_scope")
    _not_role_refused(back, "eps.shed_load", "bus-op")

    old = json.loads(json.dumps(mgr.save_state()))
    del old["role_assignments"]                                          # a save written before IP-1160
    SessionManager.validate_save(old)
    legacy = SessionManager.from_state(old)
    assert legacy.role_assignments == {}
    assert legacy.issue_order("blue", _cmd("isr.collect_now")).ok is True   # seat omitted: as today


@pytest.mark.parametrize("bad", ["x", [], {"s": "x"}, {"s": {"asset_or_constellation": 1, "role": "bus"}},
                                 {"s": {"asset_or_constellation": "A"}}])
def test_15b_a_malformed_role_assignments_key_is_refused_before_replay(bad):
    state = json.loads(json.dumps(_mgr().save_state()))
    state["role_assignments"] = bad
    with pytest.raises(ValueError, match="role_assignments"):
        SessionManager.validate_save(state)


# -- 16: determinism / replay ----------------------------------------------------------------------
@pytest.mark.verifies("IP-1160")
def test_16_accepted_role_scoped_orders_replay_byte_identically_and_refusals_write_nothing():
    def run(with_refusals):
        m = _mgr(seed=7)
        m.assign_role("bus-op", SAT, "bus")
        assert m.issue_order("blue", _cmd("eps.shed_load"), seat="bus-op").ok
        if with_refusals:
            m.issue_order("blue", _cmd("isr.collect_now"), seat="bus-op")
            m.issue_order("blue", _cmd("eps.shed_load"), seat="stranger")
        m.advance_to(m.sim.clock.now + 600 * 1_000_000)
        return m

    plain, refused = run(False), run(True)
    assert json.dumps(plain.sim.eventlog.model_dump(), sort_keys=True, default=str) == \
        json.dumps(refused.sim.eventlog.model_dump(), sort_keys=True, default=str)
    assert plain.sim.world.model_dump_json() == refused.sim.world.model_dump_json()
    assert refused.osys._order_counter == 1
    again = SessionManager.from_state(json.loads(json.dumps(refused.save_state())))
    assert again.sim.world.model_dump_json() == refused.sim.world.model_dump_json()


# -- read-only scope resolver ----------------------------------------------------------------------
def test_role_scope_for_reports_only_the_named_seat_within_the_callers_cell():
    mgr = _mgr(roles=((SAT, "both"),))
    mgr.assign_role("bus-op", SAT, "bus")
    mgr.assign_role("pl-op", SAT, "payload")
    s = mgr.role_scope_for("bus-op", "blue")
    assert s["seat"] == "bus-op" and s["bound"] is True and s["role"] == "bus"
    assert s["asset_or_constellation"] == SAT
    assert s["gated_assets"] == [SAT] and s["bound_assets"] == [SAT]
    assert s["verbs"] == ROLE_SCOPE_BY_VERB
    assert "pl-op" not in json.dumps(s)                                  # another seat's binding is not leaked
    u = mgr.role_scope_for("nobody", "white")
    assert u["bound"] is False and u["role"] is None and u["bound_assets"] == []
    assert u["gated_assets"] == [SAT]                                    # White sees every gated asset
    assert _mgr(roles=()).role_scope_for("x", "white")["gated_assets"] == []
    # Red owns none of the gated assets: nothing about Blue's assets or bindings is reportable
    r = mgr.role_scope_for("bus-op", "red")
    assert r["bound"] is False and r["gated_assets"] == [] and r["bound_assets"] == []
    assert SAT not in json.dumps(r) and r["role"] is None and r["asset_or_constellation"] is None


# -- M-1: a non-string verb is never a 500 ---------------------------------------------------------
BAD_VERBS = [[1], ["isr.collect_now"], {"a": 1}, 5, 1.5, None, True, False, "", "x" * 20000, "isr.nope"]


@pytest.mark.verifies("NFR-1600")
@pytest.mark.parametrize("seat", ["bus-op", "stranger"])
def test_m1_any_verb_value_gets_the_same_ack_as_without_a_seat_at_manager_level(seat):
    mgr = _mgr()
    mgr.assign_role("bus-op", SAT, "bus")
    for verb in BAD_VERBS:
        o = Order(cell="blue", actor=SAT, action="command", params={"verb": verb, "via": "GS-NORTH"})
        plain = mgr.validate_order("blue", o)
        o = Order(cell="blue", actor=SAT, action="command", params={"verb": verb, "via": "GS-NORTH"})
        seated = mgr.validate_order("blue", o, seat=seat)
        if isinstance(verb, str) and verb in ROLE_SCOPE_BY_VERB:
            continue
        if seat == "stranger" and (verb is None or isinstance(verb, str)):
            assert seated.reason == "role_scope_not_assigned"            # a string verb: gate as before
        else:
            assert (seated.ok, seated.reason, seated.status) == (plain.ok, plain.reason, plain.status), verb
    o = Order(cell="blue", actor=SAT, action="command", params={"via": "GS-NORTH"})   # no verb key at all
    assert mgr.validate_order("blue", o, seat="bus-op").ok == mgr.validate_order("blue", o).ok


@pytest.mark.verifies("NFR-1600")
def test_m1_any_verb_value_is_a_normal_200_ack_over_http_on_both_routes():
    c, api, sid = _http()
    api._sessions[sid].assign_role("bus-op", SAT, "bus")
    for route in ("order", "order/validate"):
        for verb in BAD_VERBS:
            base = {"cell": "blue", "actor": SAT, "action": "command", "params": {"verb": verb, "via": "GS-NORTH"}}
            plain = c.post(f"/api/sessions/{sid}/{route}", json=base)
            seated = c.post(f"/api/sessions/{sid}/{route}", json={**base, "seat": "bus-op"})
            assert plain.status_code == 200 and seated.status_code == 200, (route, verb, seated.text)
            p, q = plain.json(), seated.json()
            assert (q["ok"], q["reason"], q["status"]) == (p["ok"], p["reason"], p["status"]), (route, verb)


# -- M-2: GET /roles/scope discloses nothing about other cells' assets or assignments ----------------
@pytest.mark.verifies("FR-6220")
def test_m2_the_public_scope_read_is_only_the_static_verb_table():
    c, api, sid = _http()
    api._sessions[sid].assign_role("bus-op", SAT, "bus")
    r = c.get(f"/api/sessions/{sid}/roles/scope")
    assert r.status_code == 200 and r.json() == {"verbs": ROLE_SCOPE_BY_VERB}
    assert SAT not in r.text and "bus-op" not in r.text


@pytest.mark.verifies("FR-6220")
def test_m2_red_cannot_learn_blues_role_gated_assets_or_assignments():
    c, api, sid = _http()
    api._sessions[sid].assign_role("bus-op", SAT, "bus")
    for q in ({"seat": "bus-op", "cell": "red"}, {"seat": "ghost", "cell": "red"}):
        r = c.get(f"/api/sessions/{sid}/roles/scope", params=q)
        assert r.status_code == 200
        j = r.json()
        assert j["bound"] is False and j["gated_assets"] == [] and j["bound_assets"] == []
        assert SAT not in r.text
        assert j == c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "nobody-at-all", "cell": "red"}).json() | {"seat": q["seat"]}
    # a seat-specific read must name a console seat; the Observer has none
    assert c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "bus-op"}).status_code == 403
    assert c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "bus-op", "cell": "observer"}).status_code == 403
    # Blue gets its own; White gets any seat
    for cell in ("blue", "white"):
        j = c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "bus-op", "cell": cell}).json()
        assert j["bound"] is True and j["bound_assets"] == [SAT] and j["gated_assets"] == [SAT]


def test_lows_roles_assign_rejects_seat_names_the_order_route_rejects():
    c, api, sid = _http()
    body = {"cell": "white", "seat": "é/x", "asset_or_constellation": SAT, "role": "bus"}
    assert c.post(f"/api/sessions/{sid}/roles/assign", json=body, params={"cell": "white"}).status_code == 422
    assert api._sessions[sid].role_assignments == {}


# -- 17: HTTP --------------------------------------------------------------------------------------
def _http(mgr=None):
    api = InProcessSession()
    api._sessions["sess-1"] = mgr or _mgr()
    api._counter = 1
    return TestClient(create_app(api)), api, "sess-1"


def _body(verb, cell="blue", **extra):
    return {"cell": cell, "actor": SAT, "action": "command",
            "params": {"verb": verb, "via": "GS-NORTH"}, **extra}


def test_17_http_refusal_is_a_200_order_ack_not_an_error_and_console_seat_rules_run_first():
    c, api, sid = _http()
    api._sessions[sid].assign_role("bus-op", SAT, "bus")
    for route in ("order", "order/validate"):
        r = c.post(f"/api/sessions/{sid}/{route}", json=_body("isr.collect_now", seat="bus-op"))
        assert r.status_code == 200
        assert r.json()["ok"] is False and r.json()["reason"] == "role_scope_out_of_scope"
        assert r.json()["status"] == "rejected"
        # Observer console seat: still 403 first, even with a seat
        r = c.post(f"/api/sessions/{sid}/{route}", json=_body("isr.collect_now", cell="observer", seat="bus-op"))
        assert r.status_code == 403
        # a malformed seat is a 422 like a bad actor
        for bad in ("x" * 65, "a;b", "a/b", "<b>"):
            r = c.post(f"/api/sessions/{sid}/{route}", json=_body("eps.shed_load", seat=bad))
            assert r.status_code == 422, bad
        # a non-finite number in the body is still a 400 (IP-1082), never reaching the gate
        r = c.post(f"/api/sessions/{sid}/{route}", headers={"content-type": "application/json"},
                   content='{"cell":"blue","actor":"ISR-EO-1","action":"command","seat":"bus-op","params":{"x":NaN}}')
        assert r.status_code == 400
    assert api._sessions[sid].osys._order_counter == 0
    ok = c.post(f"/api/sessions/{sid}/order", json=_body("eps.shed_load", seat="bus-op")).json()
    assert ok["ok"] is True and ok["id"] == "ord-1"
    # roles/assign stays White-only by the query seat
    body = {"cell": "white", "seat": "x", "asset_or_constellation": SAT, "role": "bus"}
    assert c.post(f"/api/sessions/{sid}/roles/assign", json=body, params={"cell": "blue"}).status_code == 403
    assert c.post(f"/api/sessions/{sid}/roles/assign", json=body, params={"cell": "white"}).status_code == 200


def test_17b_http_roles_scope_shape_and_seat_validation():
    c, api, sid = _http()
    api._sessions[sid].assign_role("bus-op", SAT, "bus")
    r = c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "bus-op", "cell": "blue"})
    assert r.status_code == 200
    j = r.json()
    assert set(j) == {"seat", "bound", "asset_or_constellation", "role", "verbs", "gated_assets", "bound_assets"}
    assert j["role"] == "bus" and j["bound_assets"] == [SAT] and j["verbs"]["isr.collect_now"] == "payload"
    assert c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "a;b", "cell": "blue"}).status_code == 422
    assert c.get(f"/api/sessions/{sid}/roles/scope", params={"seat": "x" * 65, "cell": "blue"}).status_code == 422
    assert c.get("/api/sessions/nope/roles/scope", params={"seat": "x", "cell": "blue"}).status_code == 404


# -- 18: regression across the shipped library -----------------------------------------------------
@pytest.mark.verifies("IP-1160")
def test_18_a_request_without_a_seat_is_unchanged_on_every_shipped_vignette():
    ids = [v["id"] for v in list_vignettes()]
    assert len(ids) >= 19
    for vid in ids:
        vig = load_vignette(vid)
        assert vig.roles_needed == [], vid                                # none gates: the gate never applies
        mgr = SessionManager(vig, seed=1)
        mgr.start()
        sat = next((a.id for a in mgr.sim.world.assets.values() if a.kind == "satellite" and a.owner == "blue"), None)
        if sat is None:
            continue
        with_seat = mgr.validate_order("blue", _cmd("eps.shed_load", sat), seat="anybody")
        without = mgr.validate_order("blue", _cmd("eps.shed_load", sat))
        assert with_seat == without and with_seat.reason not in ROLE_CODES, vid
        for act in ("maneuver", "observe", "downlink", "jam", "engage", "cyber"):
            o = Order(cell="blue", actor=sat, action=act, target=None, params={})
            assert mgr.validate_order("blue", o).reason not in ROLE_CODES
