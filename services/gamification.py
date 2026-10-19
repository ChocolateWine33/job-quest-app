from datetime import date, timedelta
import random


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


def get_user_stats(application_count: int, status_count: dict) -> dict:

    xp = 0
    random_xp_number = random.randint(10, 25)
    titles = {
        1: "Job Hunter",
        5: "Resume Rookie",
        10: "Application Scout",
        25: "Opportunity Seeker",
        50: "Career Vanguard",
        60: "Job Pursuer Elite",
        85: "Application Veteran",
        100: "Legendary Job Hunter"
    }
    user_titles = []

    if application_count in titles:
        if titles[application_count] not in user_titles:
            user_titles.append(titles[application_count])
            xp += random_xp_number
        else:
            pass
    else:
        pass

