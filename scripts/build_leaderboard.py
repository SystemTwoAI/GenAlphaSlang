#!/usr/bin/env python3
"""
build_leaderboard.py — long CSV -> docs/data/leaderboard.json

    python3 scripts/build_leaderboard.py [--csv results/scores/opus46_all239_per_dimension_long.csv]
                                         [--out docs/data/leaderboard.json]
                                         [--skip-acceptance]

Hard gate (spec §4): at launch, generated composites for the paper cohort must
equal published Table 2 to two decimals, and n_evaluated must match. On any
mismatch this script prints a diagnostic and refuses to write the JSON.
Paper-cohort numbers must never move when new models are appended.

`last_updated` comes from the git commit date of the scores CSV (falling back
to today only if the file is not yet committed), never hand-typed.
"""
import argparse
import json
import subprocess
import sys
import datetime
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_scores import load_and_clean, PARTIAL_COVERAGE_MODELS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---- fixed metadata (paper baseline) ---------------------------------------
DATASET_VERSION = "v7.4"
N_EXPRESSIONS = 239
JUDGE_MODEL = "claude-opus-4-6-20260401"
JUDGE_TEMPERATURE = 0.0
PAPER = "GenAlphaBench (NeurIPS 2026 D&B submission 3764)"
LINKS = {
    "dataset": "https://huggingface.co/datasets/systemtwoai/GenAlphaBench",
    "paper": "",  # TODO(maintainer): arXiv or OpenReview URL
    "repo": "https://github.com/SystemTwoAI/GenAlphaSlang",
}

# ---- model registry ---------------------------------------------------------
# display name -> (family, vendor_id, evaluated_date, cohort, notes)
# vendor_id left "" where the exact vendor string has not been confirmed by the
# maintainer; the page falls back to the display name.
REGISTRY = {
    "Opus 4.6":         ("Claude", "claude-opus-4-6-20260401", "2026-05", "paper", ""),
    "Opus 4.7":         ("Claude", "", "2026-05", "paper", ""),
    "Opus 4.5":         ("Claude", "", "2026-05", "paper", ""),
    "Opus 4.0":         ("Claude", "", "2026-05", "paper", ""),
    "Sonnet 4.6":       ("Claude", "", "2026-05", "paper", ""),
    "Sonnet 4.0":       ("Claude", "", "2026-05", "paper", ""),
    "Haiku 4.5":        ("Claude", "", "2026-05", "paper", ""),
    "Haiku 3.0":        ("Claude", "", "2026-05", "paper",
                         "evaluated on 81 expressions; excluded from aggregate comparisons in the paper"),
    "o3":               ("OpenAI", "", "2026-05", "paper", ""),
    "GPT-4.1":          ("OpenAI", "", "2026-05", "paper", ""),
    "o4-mini":          ("OpenAI", "", "2026-05", "paper", ""),
    "GPT-4o":           ("OpenAI", "", "2026-05", "paper", ""),
    "GPT-4o-mini":      ("OpenAI", "", "2026-05", "paper", ""),
    "Gemini-2.5-Pro":   ("Google", "", "2026-05", "paper", ""),
    "Gemini-2.5-Flash": ("Google", "", "2026-05", "paper", ""),
    "Gemini-2.0-Flash": ("Google", "", "2026-05", "paper", ""),
}

# ---- launch acceptance test: published Table 2 composites -------------------
# Launch gate values. These are the paper's published Table 2 numbers with two
# maintainer-ratified corrections (2026-07-26):
#   - GPT-4o: 14.17 here vs 14.18 in print. The cleaned mean is 14.1746 over
#     n=236, which rounds to 14.17; the 0.005 difference is disclosed in a
#     standing footnote. The leaderboard shows the value reproducible from the
#     committed data.
#   - GPT-4.1 / GPT-4o-mini n=236 (not 239): expressions 1-3 were never judged
#     for the GPT-4x models; published composites match exactly at n=236.
TABLE2_COMPOSITES = {
    "Opus 4.6": 19.21, "o3": 18.28, "GPT-4.1": 18.04, "Sonnet 4.6": 17.94,
    "Opus 4.7": 17.85, "Opus 4.5": 17.70, "Gemini-2.5-Pro": 17.60,
    "Haiku 4.5": 16.17, "Sonnet 4.0": 15.43, "Gemini-2.5-Flash": 15.34,
    "Opus 4.0": 15.23, "o4-mini": 15.18, "GPT-4o": 14.17,
    "Gemini-2.0-Flash": 13.57, "GPT-4o-mini": 12.84, "Haiku 3.0": 8.19,
}
EXPECTED_N = {
    "Opus 4.6": 239, "o3": 235, "GPT-4.1": 236, "Sonnet 4.6": 238,
    "Opus 4.7": 239, "Opus 4.5": 239, "Gemini-2.5-Pro": 239, "Haiku 4.5": 239,
    "Sonnet 4.0": 239, "Gemini-2.5-Flash": 239, "Opus 4.0": 239, "o4-mini": 233,
    "GPT-4o": 236, "Gemini-2.0-Flash": 198, "GPT-4o-mini": 236, "Haiku 3.0": 81,
}

STANDING_FOOTNOTES = [
    "Haiku 3.0 was evaluated on 81 of 239 expressions and is excluded from aggregate comparisons; it is shown for reference only. Its two judged totals of 0 are retained as real scores, matching the paper.",
    "Cleaning: rows flagged missing are dropped, and any (expression, model) pair whose judged total is exactly 0 is treated as an unjudged/empty response and removed before averaging (affects o3 ×1 and o4-mini ×3).",
    "GPT-4o's cleaned mean is 14.17 (14.1746 over 236 expressions); Table 2 of the paper prints 14.18, a rounding/pipeline difference of 0.005. The leaderboard shows the value reproducible from the committed data.",
    "Expressions 1–3 were never judged for GPT-4.1, GPT-4o, and GPT-4o-mini (n=236); published composites are computed on the judged set.",
]
# Appended by the maintainer when the first post-paper model lands (spec §5.3):
# "Solo-judging calibration: GPT-4.1 scores X.XX solo vs 18.04 in-context; ..."
CALIBRATION_FOOTNOTE = ""


def git_date_of(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            capture_output=True, text=True, cwd=REPO_ROOT, check=True,
        ).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.today().isoformat()  # not yet committed


def mean(xs):
    return sum(xs) / len(xs)


# Expression cohorts (maintainer-defined 2026-07-26): the original benchmark
# is expressions 1-100; the updated set is 101-239.
SPLITS = {
    "original": ("Original benchmark", 1, 100),
    "updated": ("Updated set", 101, 239),
}


def _aggregate(rows):
    """rows -> {model: {dims: {...}, risks: {...}}}"""
    by_model = defaultdict(lambda: defaultdict(list))
    by_model_risk = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_model[r["model"]][r["dimension"]].append(r["score"])
        if r["dimension"] == "total":
            by_model_risk[r["model"]][r["risk_category"]].append(r["score"])
    return by_model, by_model_risk


def _stats(dims, risks):
    return {
        "n_evaluated": len(dims["total"]),
        "composite": round(mean(dims["total"]), 2),
        "dimensions": {
            d: round(mean(dims[d]), 2)
            for d in ("meaning", "context", "safety", "rating") if d in dims
        },
        "by_risk": {rc: round(mean(v), 2) for rc, v in sorted(risks.items())},
    }


def build(rows):
    by_model, by_model_risk = _aggregate(rows)
    split_aggs = {}
    for key, (_label, lo, hi) in SPLITS.items():
        subset = [r for r in rows if lo <= int(r["expression_id"]) <= hi]
        split_aggs[key] = _aggregate(subset)

    entries = []
    for model, dims in sorted(by_model.items()):
        if model not in REGISTRY:
            raise SystemExit(
                f"FATAL: model '{model}' in CSV is not in the registry. "
                f"Add it to REGISTRY in build_leaderboard.py (with cohort "
                f"'post-paper' and an evaluated_date) before building."
            )
        family, vendor_id, evaluated_date, cohort, notes = REGISTRY[model]
        if "total" not in dims:
            raise SystemExit(f"FATAL: no 'total' rows for {model} after cleaning.")
        entry = {
            "model": model,
            "family": family,
            "vendor_id": vendor_id,
            **_stats(dims, by_model_risk[model]),
            "splits": {},
            "critical_failures": None,  # populated when the per-expression source defines it
            "evaluated_date": evaluated_date,
            "cohort": cohort,
            "notes": notes,
            "partial_coverage": model in PARTIAL_COVERAGE_MODELS,
        }
        for key in SPLITS:
            s_dims, s_risks = split_aggs[key]
            if model in s_dims and s_dims[model].get("total"):
                entry["splits"][key] = _stats(s_dims[model], s_risks[model])
        entries.append(entry)

    entries.sort(key=lambda e: (e["partial_coverage"], -e["composite"]))
    return entries


def acceptance_test(entries):
    failures = []
    got = {e["model"]: e for e in entries if e["cohort"] == "paper"}
    for model, expected in TABLE2_COMPOSITES.items():
        if model not in got:
            failures.append(f"missing paper-cohort model: {model}")
            continue
        g = got[model]
        if abs(g["composite"] - expected) > 0.005:
            failures.append(
                f"composite mismatch {model}: got {g['composite']:.2f}, Table 2 says {expected:.2f}"
            )
        if g["n_evaluated"] != EXPECTED_N[model]:
            failures.append(
                f"n_evaluated mismatch {model}: got {g['n_evaluated']}, expected {EXPECTED_N[model]}"
            )
    if failures:
        print("\nACCEPTANCE TEST FAILED — refusing to write leaderboard.json")
        for f in failures:
            print(f"  - {f}")
        o3 = got.get("o3", {}).get("composite")
        o4 = got.get("o4-mini", {}).get("composite")
        if (o3 and abs(o3 - 18.20) <= 0.005) or (o4 and abs(o4 - 14.99) <= 0.005):
            print(
                "  DIAGNOSTIC: o3/o4-mini at 18.20/14.99 means the zero-drop rule "
                "(validate_scores.py rule 3) is not being applied."
            )
        sys.exit(1)
    print("Acceptance test PASSED: Table 2 reproduced exactly; expected n's match.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="results/scores/opus46_all239_per_dimension_long.csv")
    ap.add_argument("--out", default="docs/data/leaderboard.json")
    ap.add_argument("--skip-acceptance", action="store_true",
                    help="Skip the Table-2 gate (never use for a published build).")
    args = ap.parse_args()

    csv_path = REPO_ROOT / args.csv
    rows, report = load_and_clean(csv_path, verbose=True)
    if report["problems"]:
        print(f"\nFATAL: validate_scores reported {len(report['problems'])} problem(s); fix before building.")
        sys.exit(1)

    entries = build(rows)
    if not args.skip_acceptance:
        acceptance_test(entries)

    footnotes = list(STANDING_FOOTNOTES)
    if CALIBRATION_FOOTNOTE:
        footnotes.append(CALIBRATION_FOOTNOTE)
    if any(e["cohort"] == "post-paper" for e in entries) and not CALIBRATION_FOOTNOTE:
        print(
            "WARNING: post-paper entries exist but CALIBRATION_FOOTNOTE is empty. "
            "Spec §5.3 requires publishing the solo-judging calibration delta."
        )

    payload = {
        "meta": {
            "dataset_version": DATASET_VERSION,
            "n_expressions": N_EXPRESSIONS,
            "judge_model": JUDGE_MODEL,
            "judge_temperature": JUDGE_TEMPERATURE,
            "last_updated": git_date_of(csv_path),
            "paper": PAPER,
            "links": LINKS,
            "splits": {
                key: {"label": label, "expressions": f"{lo}–{hi}", "n": hi - lo + 1}
                for key, (label, lo, hi) in SPLITS.items()
            },
            "footnotes": footnotes,
        },
        "entries": entries,
    }

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
