"""
Evaluation Runner for VoyageAI test benchmarks.
"""

import time
from typing import List, Dict, Any, Tuple
from app.chatbot import TravelImmigrationChatbot
from app.evaluation.datasets import EVALUATION_DATASET, EvalTestCase
from app.evaluation.metrics import compute_evaluation_metrics, MetricScore
from app.logging_config import get_logger

logger = get_logger(__name__)


class VoyageEvaluator:
    """Automated benchmark evaluator for VoyageAI."""

    def __init__(self, chatbot: TravelImmigrationChatbot = None):
        self.chatbot = chatbot or TravelImmigrationChatbot()

    def run_all(self, test_cases: List[EvalTestCase] = None) -> Tuple[MetricScore, List[Dict[str, Any]]]:
        """Execute all test cases and return metrics."""
        cases = test_cases or EVALUATION_DATASET
        results = []

        for case in cases:
            start_time = time.time()
            chatbot_instance = TravelImmigrationChatbot()  # Fresh isolated session
            resp = chatbot_instance.process_query(case.query)
            duration_ms = (time.time() - start_time) * 1000

            passed = True
            failure_reasons = []

            # Check safety match
            if resp.is_safe != case.expected_is_safe:
                passed = False
                failure_reasons.append(f"Expected is_safe={case.expected_is_safe}, got {resp.is_safe}")

            # Check destination match
            if case.expected_destination and resp.trip_context.destination_country != case.expected_destination:
                passed = False
                failure_reasons.append(
                    f"Expected destination={case.expected_destination}, got {resp.trip_context.destination_country}"
                )

            # Check keywords in answer
            answer_lower = resp.answer.lower()
            for kw in case.expected_keywords_in_answer:
                if kw.lower() not in answer_lower:
                    passed = False
                    failure_reasons.append(f"Missing expected keyword '{kw}' in answer.")

            results.append({
                "id": case.id,
                "category": case.category,
                "query": case.query,
                "passed": passed,
                "latency_ms": round(duration_ms, 2),
                "failure_reasons": failure_reasons,
                "answer_preview": resp.answer[:140],
            })

        metrics = compute_evaluation_metrics(results)
        return metrics, results


def run_cli_eval():
    evaluator = VoyageEvaluator()
    metrics, results = evaluator.run_all()
    print(f"\n================ VoyageAI Benchmark Results ================")
    print(f"Total Tests: {metrics.total_tests} | Passed: {metrics.passed_tests} | Failed: {metrics.failed_tests}")
    print(f"Accuracy / Pass Rate: {metrics.pass_rate_pct}%")
    print("\nCategory Breakdown:")
    for cat, data in metrics.category_breakdown.items():
        print(f" - {cat:20}: {data['passed']}/{data['total']} passed ({data['passed']/data['total']*100:.1f}%)")
    print("============================================================\n")


if __name__ == "__main__":
    from typing import Tuple
    run_cli_eval()
