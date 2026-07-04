"""Research Analytics: structured multi-run/cohort export of IP-2010's rubric output (IP-3010,
FS-301 / FR-10210). ``RunRecord`` carries run-identifying metadata plus exactly what
``session/assessment.py``'s ``assessment_report`` computed for that run — never a reimplementation
of any dimension's scoring (FS-301's own explicit non-goal). Export functions extend
``aar.export_csv()``'s flattening pattern (csv module, one row per record) to a multi-run table.
"""

from __future__ import annotations

import csv
import io
import json

from pydantic import BaseModel, Field


class RunRecord(BaseModel):
    vignette_id: str
    seed: int
    condition_label: str
    assessment: dict = Field(default_factory=dict)  # session/assessment.py's assessment_report(mgr)


def export_csv(records: list[RunRecord]) -> str:
    """One row per run, one column per metadata/dimension field."""
    buf = io.StringIO()
    w = csv.writer(buf)
    pairs: list[tuple[str, str]] = []
    for rec in records:
        for cell, dims in rec.assessment.items():
            for dim in dims:
                pair = (cell, dim)
                if pair not in pairs:
                    pairs.append(pair)
    w.writerow(["vignette_id", "seed", "condition_label"] + [f"{c}_{d}" for c, d in pairs])
    for rec in records:
        row = [rec.vignette_id, rec.seed, rec.condition_label]
        for c, d in pairs:
            row.append(rec.assessment.get(c, {}).get(d, ""))
        w.writerow(row)
    return buf.getvalue()


def export_json(records: list[RunRecord]) -> str:
    return json.dumps([r.model_dump() for r in records], indent=2)
