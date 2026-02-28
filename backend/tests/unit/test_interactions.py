"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 1),
        _make_log(3, 1, 2),
    ]

    result = _filter_by_item_id(interactions, 1)

    assert len(result) == 2
    assert result[0].id in (1, 2)
    assert result[1].id in (1, 2)
    assert all(log.item_id == 1 for log in result)


def test_filter_returns_empty_for_nonexistent_item_id() -> None:
    """Test that filtering by an item_id that doesn't exist returns empty list."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 3, 3),
    ]

    result = _filter_by_item_id(interactions, 999)  # Несуществующий ID

    assert result == []


def test_filter_handles_negative_item_id() -> None:
    """Test that filtering by negative item_id returns empty list (edge case)."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 1),
    ]

    result = _filter_by_item_id(interactions, -1)

    assert result == []


def test_filter_returns_all_matching_items_with_same_id() -> None:
    """Test that all interactions with the same item_id are returned."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 6),
        _make_log(5, 5, 6),
    ]

    result = _filter_by_item_id(interactions, 5)

    assert len(result) == 3
    assert all(log.item_id == 5 for log in result)
    assert {log.id for log in result} == {1, 2, 3}


def test_filter_preserves_original_order() -> None:
    """Test that filtering maintains the original order of interactions."""
    interactions = [
        _make_log(1, 1, 2),
        _make_log(2, 2, 1),
        _make_log(3, 3, 2),
        _make_log(4, 4, 1),
        _make_log(5, 5, 2),
    ]

    result = _filter_by_item_id(interactions, 2)

    # Проверяем, что IDs идут в том же порядке: 1, 3, 5
    assert [log.id for log in result] == [1, 3, 5]


def test_filter_handles_zero_item_id() -> None:
    """Test that filtering by zero item_id (if valid) returns correct results."""
    interactions = [
        _make_log(1, 1, 0),
        _make_log(2, 2, 1),
        _make_log(3, 3, 0),
    ]

    result = _filter_by_item_id(interactions, 0)

    assert len(result) == 2
    assert all(log.item_id == 0 for log in result)
    assert {log.id for log in result} == {1, 3}
