# -*- coding: utf-8 -*-
"""食谱事实：步骤里写了时间，minutes 必须落在那个区间里。"""
import json
from pathlib import Path

import recipe_facts as rf

ROOT = Path(__file__).resolve().parents[1]


def test_stated_minutes_reads_ranges():
    assert rf.stated_minutes("约2–2.5小时，4人份。") == (120, 150)
    assert rf.stated_minutes("约45分钟，3人份。") == (45, 45)
    assert rf.stated_minutes("豆腐切块。") is None
    assert rf.stated_minutes("大火煮至熟透（约25分钟），捞出放凉。") is None


def test_minutes_stay_inside_the_time_the_first_step_states():
    data = json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))
    misses = []
    for recipe in data["recipes"]:
        steps = recipe.get("steps") or []
        bound = rf.stated_minutes(steps[0] if steps else "")
        if not bound:
            continue
        minutes = recipe.get("minutes")
        lo, hi = bound
        if not isinstance(minutes, int) or not (lo <= minutes <= hi):
            misses.append("%s minutes=%s 步骤=%s–%s" % (recipe["id"], minutes, lo, hi))
    assert misses == []
