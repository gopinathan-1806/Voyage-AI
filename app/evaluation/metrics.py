"""
Evaluation metrics computation for VoyageAI test suites.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class MetricScore(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate_pct: float
    category_breakdown: Dict[str, Dict[str, int]]
    average_latency_ms: float = 0.0


def compute_evaluation_metrics(test_results: List[Dict[str, Any]]) -> MetricScore:
    """Calculates accuracy, safety pass rate, and category breakdowns."""
    total = len(test_results)
    if total == 0:
        return MetricScore(
            total_tests=0, passed_tests=0, failed_tests=0, pass_rate_pct=0.0, category_breakdown={}
        )

    passed = sum(1 for r in test_results if r["passed"])
    failed = total - passed

    categories: Dict[str, Dict[str, int]] = {}
    for r in test_results:
        cat = r.get("category", "other")
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if r["passed"]:
            categories[cat]["passed"] += 1

    return MetricScore(
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        pass_rate_pct=round((passed / total) * 100.0, 2),
        category_breakdown=categories,
    )
