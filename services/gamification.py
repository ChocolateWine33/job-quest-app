from datetime import date, timedelta
import random


TITLES = {
    1: "Job Hunter",
    5: "Resume Rookie",
    10: "Application Scout",
    25: "Opportunity Seeker",
    50: "Career Vanguard",
    60: "Job Pursuer Elite",
    85: "Application Veteran",
    100: "Legendary Job Hunter"
}

STATUS_TITLES = {
    "Interview":{
        1: "First Call",
        3: "Interview Challenger",
        5: "Interview Ace",
        10: "Interview Legend"
    },
    "Offer":{
        1: "Offer Magnet",
        3: "Rising Prospect",
        5: "Top Candidate",
        10: "Career Conqueror"
    }
}
STATUS_XP = {"Interview": 50, "Offer": 100}
LEVEL_THRESHOLD = 100
XP_PER_APPLICATION = 10

def calculate_user_streak(application_dates: list) -> int:

    today = date.today()

    if not application_dates:
        return 0

    # dead if the newest date is older than yesterday
    if today - application_dates[0] > timedelta(days=1):
        return 0

    streak = 0
    expected = application_dates[0]  # the date I need to see next

    for d in application_dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break  # gap found, streak ends

    return streak


def get_user_stats(application_count: int, user_id: int, status_count: dict) -> dict:

    applications_xp = application_count * XP_PER_APPLICATION
    user_stats = {
        "title": [],
        "xp": applications_xp
    }


    for key in TITLES:
        if application_count >= key:
            user_stats["title"].append(TITLES[key])
            user_stats["xp"] += (random.Random(f"{user_id}-{key}").randint(50, 75))

    for status in STATUS_TITLES:
        count = status_count.get(status, 0)
        for threshold, title in STATUS_TITLES[status].items():
            if count >= threshold:
                user_stats["title"].append(title)
                user_stats["xp"] += STATUS_XP[status]
            else:
                break

    return user_stats

def get_user_level(xp: int) -> dict:

    level = (xp // LEVEL_THRESHOLD) + 1
    current_xp = xp % LEVEL_THRESHOLD

    return {
        "level" : level,
        "current_xp": current_xp
    }


def get_current_title(titles: list) -> str | None:

    return titles[-1] if titles else None


def build_progress(application_count, status_count, dates, user_id):
    user_stats = get_user_stats(application_count, user_id, status_count)
    return {
        "streak": calculate_user_streak(dates),
        "level": get_user_level(user_stats["xp"]),
        "title": get_current_title(user_stats["title"]),
        "unlocked_titles": user_stats["title"],
    }
