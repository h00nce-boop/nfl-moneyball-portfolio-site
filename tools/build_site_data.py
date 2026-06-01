#!/usr/bin/env python3
"""Export NFL Moneyball CSV outputs into the portfolio site's site-data.js file.

Usage from your main nfl-moneyball-roster-value repo root:

    python tools/export_site_data.py --repo-root . --out portfolio_site/site-data.js

This script intentionally uses only the Python standard library so it can run in a
fresh clone without pandas.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_META = {
    "projectTitle": "NFL Moneyball Roster Value",
    "owner": "Hannah Levy",
    "tagline": "Find underpriced NFL production before the market fully prices it.",
    "seasonWindow": "2021-2025",
    "currentWatchlistSeason": 2025,
    "dataVersion": "V4 backtest + latest watchlist",
    "githubUrl": "https://github.com/h00nce-boop/nfl-moneyball-roster-value",
    "streamlitUrl": "https://nfl-moneyball-roster-value.streamlit.app/",
    "resumeUrl": "Hannah_Levy_Resume.pdf",
    "email": "",
    "linkedinUrl": "",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        print(f"warning: missing {path}")
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def as_float(row: Dict[str, str], key: str, default: Optional[float] = None) -> Optional[float]:
    value = row.get(key, "")
    if value in (None, "", "NA", "nan", "None"):
        return default
    try:
        return float(value)
    except ValueError:
        return default


def as_int(row: Dict[str, str], key: str, default: Optional[int] = None) -> Optional[int]:
    value = as_float(row, key, None)
    if value is None:
        return default
    return int(value)


def as_bool(row: Dict[str, str], key: str, default: bool = False) -> bool:
    value = str(row.get(key, "")).strip().lower()
    if value in {"true", "1", "yes", "y"}:
        return True
    if value in {"false", "0", "no", "n"}:
        return False
    return default


def pick(row: Dict[str, str], *keys: str, default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return default


def build_players(rows: Iterable[Dict[str, str]], limit: int = 80) -> List[Dict[str, Any]]:
    players: List[Dict[str, Any]] = []
    for row in rows:
        players.append({
            "season": as_int(row, "season"),
            "player_name": pick(row, "player_name", "player", "name"),
            "team": pick(row, "team", "recent_team"),
            "position": pick(row, "position_final", "position"),
            "production_score": as_float(row, "production_score", 0.0),
            "player_surplus_gap": as_float(row, "player_surplus_gap", 0.0),
            "player_surplus_rank": as_float(row, "player_surplus_rank"),
            "cap_number": as_float(row, "cap_number", 0.0),
            "draft_year": as_int(row, "draft_year"),
            "draft_round": as_int(row, "draft_round"),
            "draft_pick": as_int(row, "draft_pick"),
            "years_since_drafted": as_float(row, "years_since_drafted"),
            "draft_capital_bucket": pick(row, "draft_capital_bucket"),
            "estimated_contract_stage": pick(row, "estimated_contract_stage"),
            "is_likely_rookie_contract": as_bool(row, "is_likely_rookie_contract", False),
            "overall_confidence": pick(row, "overall_confidence", default="unknown"),
            "watchlist_note": pick(row, "watchlist_note", default="Matches current candidate profile."),
        })
    players.sort(key=lambda item: (item.get("player_surplus_gap") or 0), reverse=True)
    return players[:limit]


def build_focus_teams(rows: Iterable[Dict[str, str]]) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    for row in rows:
        output.append({
            "season": as_int(row, "season"),
            "team": pick(row, "team"),
            "overall_rank": as_float(row, "overall_rank"),
            "cap_cost_rank": as_float(row, "cap_cost_rank"),
            "performance_score": as_float(row, "performance_score"),
            "cost_score": as_float(row, "cost_score"),
            "surplus_rank_gap": as_float(row, "surplus_rank_gap", 0.0),
            "surplus_tier": pick(row, "surplus_tier"),
            "surplus_value_rank": as_float(row, "surplus_value_rank"),
            "team_role": pick(row, "team_role"),
        })
    output.sort(key=lambda item: (str(item.get("team")), item.get("season") or 0))
    return output


def build_threshold_curve(rows: Iterable[Dict[str, str]]) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    for row in rows:
        position = pick(row, "position_final", "position", default="ALL")
        if position != "ALL":
            continue
        output.append({
            "threshold": as_float(row, "threshold", 0.0),
            "position": position,
            "players_model": as_int(row, "players_model", 0),
            "players_baseline": as_int(row, "players_baseline", 0),
            "hit_rate_model": as_float(row, "hit_rate_model", 0.0),
            "hit_rate_baseline": as_float(row, "hit_rate_baseline", 0.0),
            "hit_rate_lift": as_float(row, "hit_rate_lift", 0.0),
            "appearance_rate_lift": as_float(row, "appearance_rate_lift", 0.0),
            "next_surplus_gap_lift": as_float(row, "next_surplus_gap_lift", 0.0),
            "next_production_score_lift": as_float(row, "next_production_score_lift", 0.0),
        })
    output.sort(key=lambda item: item.get("threshold") or 0)
    return output


def build_position_backtest(rows: Iterable[Dict[str, str]], threshold: float = 5.0) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    for row in rows:
        position = pick(row, "position_final", "position", default="")
        row_threshold = as_float(row, "threshold")
        if position == "ALL" or row_threshold != threshold:
            continue
        output.append({
            "threshold": row_threshold,
            "position": position,
            "players_model": as_int(row, "players_model", 0),
            "players_baseline": as_int(row, "players_baseline", 0),
            "hit_rate_model": as_float(row, "hit_rate_model", 0.0),
            "hit_rate_baseline": as_float(row, "hit_rate_baseline", 0.0),
            "hit_rate_lift": as_float(row, "hit_rate_lift", 0.0),
            "next_surplus_gap_lift": as_float(row, "next_surplus_gap_lift", 0.0),
        })
    position_order = {"QB": 0, "RB": 1, "WR": 2, "TE": 3}
    output.sort(key=lambda item: position_order.get(item.get("position"), 99))
    return output


def build_metrics(threshold_curve: List[Dict[str, Any]], default_threshold: float = 5.0) -> Dict[str, Any]:
    selected = next((row for row in threshold_curve if row.get("threshold") == default_threshold), None)
    if selected is None and threshold_curve:
        selected = threshold_curve[0]
    selected = selected or {}
    return {
        "seasonsModeled": "2021-2025",
        "teamsEvaluated": 32,
        "positionsModeled": "QB / RB / WR / TE",
        "candidateHitRate": selected.get("hit_rate_model", 0.0),
        "baselineHitRate": selected.get("hit_rate_baseline", 0.0),
        "hitRateLift": selected.get("hit_rate_lift", 0.0),
        "nextSurplusGapLift": selected.get("next_surplus_gap_lift", 0.0),
        "defaultThreshold": default_threshold,
        "modelCandidates": selected.get("players_model", 0),
        "baselinePlayers": selected.get("players_baseline", 0),
    }


def static_methodology() -> Dict[str, Any]:
    return {
        "timeline": [
            {"version": "V1", "title": "Baseline surplus framework", "body": "Compared team performance rank and player production rank against public contract-cost rank."},
            {"version": "V2", "title": "Confidence and data quality", "body": "Added missing-contract handling, low-sample separation, confidence labels, and diagnostic audit outputs."},
            {"version": "V3", "title": "Draft and contract-cycle context", "body": "Added draft round, draft pick, contract-stage labels, rookie-contract flags, and surplus context."},
            {"version": "V4", "title": "Backtest and watchlist", "body": "Tested whether high-confidence rookie-contract surplus candidates outperform a comparable not-flagged baseline."},
        ],
        "methodologyCards": [
            {"label": "Team surplus", "formula": "surplus_rank_gap = cap_cost_rank - overall_performance_rank", "body": "Positive values mean a team performed better than its cost rank would suggest."},
            {"label": "Player surplus", "formula": "player_surplus_gap = cost_rank_position - production_rank_position", "body": "Positive values mean a player produced better than his position-specific cost rank."},
            {"label": "Candidate flag", "formula": "rookie_contract + high_confidence + surplus_gap >= threshold", "body": "The default backtest threshold is +5, but the site lets you inspect how lift changes as the threshold moves."},
            {"label": "Caveat", "formula": "public cost proxy != official cap accounting", "body": "The project is a decision-support prototype, not a final scouting or salary-cap model."},
        ],
    }


def build_site_data(repo_root: Path) -> Dict[str, Any]:
    watchlist_rows = read_csv(repo_root / "outputs_v4" / "backtests" / "candidate_review_2025_watchlist.csv")
    focus_team_rows = read_csv(repo_root / "outputs" / "focus_team_surplus_2021_2025.csv")
    threshold_rows = read_csv(repo_root / "outputs_v4" / "backtests" / "threshold_sensitivity_lift.csv")

    threshold_curve = build_threshold_curve(threshold_rows)
    default_threshold = 5.0
    data = {
        "meta": {**DEFAULT_META, "lastUpdated": date.today().isoformat()},
        "metrics": build_metrics(threshold_curve, default_threshold=default_threshold),
        "players": build_players(watchlist_rows),
        "focusTeams": build_focus_teams(focus_team_rows),
        "thresholdCurve": threshold_curve,
        "positionBacktest": build_position_backtest(threshold_rows, threshold=default_threshold),
    }
    data.update(static_methodology())
    return data


def write_site_data(data: Dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    out_path.write_text(f"window.NFL_MONEYBALL_DATA = {payload};\n", encoding="utf-8")
    print(f"wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export CSV outputs into portfolio site data.")
    parser.add_argument("--repo-root", default=".", help="Path to nfl-moneyball-roster-value repo root")
    parser.add_argument("--out", default="site-data.js", help="Output site-data.js path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_path = Path(args.out).resolve()
    data = build_site_data(repo_root)
    write_site_data(data, out_path)


if __name__ == "__main__":
    main()
