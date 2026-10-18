from datetime import date, timedelta


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
