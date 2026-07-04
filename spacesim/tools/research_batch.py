"""Research Analytics: seeded Monte-Carlo batch runner (IP-3010, FS-301 / FR-10210).

Drives N independent seeded ``SessionManager`` instances of one vignette to collect IP-2010's
per-run rubric output at scale, for structured export via ``session/research_export.py``. Never
introduces non-determinism inside ``engine/`` — variability comes only from varying the seed
externally, per DOM-005 §6 / NFR-1500. Each run starts from a clean seeded initial state; no
mutable state is shared between runs.
"""

from __future__ import annotations

from typing import Optional

from spacesim.content.vignette import load_vignette
from spacesim.session.assessment import assessment_report
from spacesim.session.manager import SessionManager
from spacesim.session.research_export import RunRecord


def run_batch(
    vignette_id: str,
    seeds: list[int],
    condition_label: str,
    n_steps_or_until: Optional[float] = None,
) -> list[RunRecord]:
    """Run ``vignette_id`` once per seed in ``seeds``, each from a fresh ``SessionManager``.

    ``n_steps_or_until`` is sim-seconds to advance from each run's own start; omitted (``None``)
    means run to the vignette's own estimated-duration horizon ("run to completion"). Returns one
    ``RunRecord`` per seed, in the same order as ``seeds``, each carrying exactly
    ``session/assessment.py``'s ``assessment_report`` output for that run — called once per run,
    never reimplemented.
    """
    records: list[RunRecord] = []
    for seed in seeds:
        vignette = load_vignette(vignette_id)
        mgr = SessionManager(vignette, seed=seed)
        mgr.start()
        target = mgr.horizon if n_steps_or_until is None else mgr.sim.clock.now + int(n_steps_or_until * 1_000_000)
        mgr.advance_to(target)
        records.append(RunRecord(
            vignette_id=vignette_id,
            seed=seed,
            condition_label=condition_label,
            assessment=assessment_report(mgr),
        ))
    return records
