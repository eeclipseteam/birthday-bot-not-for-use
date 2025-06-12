from datetime import datetime, timedelta

def calculate_birthday_time(birthday_date, user_utc):
    now = datetime.utcnow() + timedelta(hours=user_utc)
    this_year_birthday = birthday_date.replace(year=now.year)

    if this_year_birthday < now:
        this_year_birthday = this_year_birthday.replace(year=now.year + 1)

    diff = this_year_birthday - now
    parts = []
    days = diff.days
    seconds = diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if days > 0: parts.append(f"{days} д")
    if hours > 0: parts.append(f"{hours} ч")
    if minutes > 0: parts.append(f"{minutes} м")
    if seconds > 0: parts.append(f"{seconds} с")

    return " ".join(parts)
