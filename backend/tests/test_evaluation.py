from __future__ import annotations

import pytest

from services.evaluation import average_precision, ndcg_at_k, ranking_report


def test_perfect_ranking_scores_one():
    assert average_precision([1, 1, 0, 0]) == 1.0
    assert ndcg_at_k([3, 2, 1, 0]) == pytest.approx(1.0)


def test_average_precision_worked_example():
    # Relevant candidates at ranks 1 and 3 -> (1/1 + 2/3) / 2
    assert average_precision([1, 0, 1, 0]) == pytest.approx((1 + 2 / 3) / 2)


def test_worse_order_lowers_ndcg():
    assert ndcg_at_k([0, 1, 2, 3]) < ndcg_at_k([3, 2, 1, 0])


def test_report_averages_over_queries():
    report = ranking_report([[1, 0], [0, 1]], k=2)
    assert report["query_count"] == 2
    assert report["map"] == pytest.approx(0.75)
