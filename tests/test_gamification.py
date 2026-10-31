from datetime import date, timedelta

from services.gamification import (  # ADJUST the module path
    calculate_user_streak,
    get_user_level,
    get_user_stats,
    get_current_title,
    build_progress,
)

today = date.today()


def days_ago(n):
    return today - timedelta(days=n)


# --- levels: test the boundary, where off-by-one bugs live ---

def test_level_just_below_boundary():
    assert get_user_level(99) == {"level": 1, "current_xp": 99}


def test_level_at_boundary():
    assert get_user_level(100) == {"level": 2, "current_xp": 0}


# --- streaks (the function expects dates sorted newest first) ---

def test_streak_empty_list_is_zero():
    assert calculate_user_streak([]) == 0


def test_streak_three_consecutive_days():
    assert calculate_user_streak([days_ago(0), days_ago(1), days_ago(2)]) == 3


def test_streak_still_alive_if_newest_is_yesterday():
    assert calculate_user_streak([days_ago(1), days_ago(2)]) == 2


def test_streak_dead_if_newest_is_older_than_yesterday():
    assert calculate_user_streak([days_ago(3), days_ago(4)]) == 0


def test_streak_stops_at_gap():
    assert calculate_user_streak([days_ago(0), days_ago(1), days_ago(3)]) == 2


def test_streak_expects_distinct_dates():
    # The function's contract: one date per day, newest first.
    # Deduplication happens in the query (get_applications_dates uses .distinct()).
    assert calculate_user_streak([days_ago(0), days_ago(1), days_ago(2)]) == 3


# --- titles: assert on titles, not exact XP (the random bonus would make it brittle) ---

def test_no_applications_no_titles():
    assert get_user_stats(0, user_id=1, status_count={})["title"] == []


def test_application_count_unlocks_titles_in_order():
    stats = get_user_stats(5, user_id=1, status_count={})
    assert stats["title"] == ["Job Hunter", "Resume Rookie"]


def test_status_titles_unlock_by_threshold():
    stats = get_user_stats(0, user_id=1, status_count={"Interview": 3})
    assert stats["title"] == ["First Call", "Interview Challenger"]


def test_xp_is_deterministic_for_same_user():
    a = get_user_stats(10, user_id=7, status_count={})
    b = get_user_stats(10, user_id=7, status_count={})
    assert a["xp"] == b["xp"]


def test_current_title():
    assert get_current_title([]) is None
    assert get_current_title(["A", "B"]) == "B"


def test_build_progress_for_brand_new_user():
    progress = build_progress(0, {}, [], user_id=1)
    assert progress == {
        "streak": 0,
        "level": {"level": 1, "current_xp": 0},
        "title": None,
        "unlocked_titles": [],
    }
