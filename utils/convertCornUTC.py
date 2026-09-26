import calendar
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from croniter import croniter
from cron_descriptor import ExpressionDescriptor, Options


# Timezone to assume when a cron has no "TZ=" prefix.
# This must match how your scheduler treats such crons.
DEFAULT_TIMEZONE = "Asia/Kolkata"

MINUTES_PER_DAY = 24 * 60


def convert_schedules(schedules):
    """
    Convert a list of schedules to UTC.

    Each input item looks like {"cron": "TZ=Asia/Calcutta 6 19 * * *"}.
    Each output item looks like {"cron": "36 13 * * *", "scheduleSummary": "Daily at 13:36 UTC"}.

    If a schedule can't be converted, the original item is returned
    with an "error" field explaining why. The other schedules are
    still converted normally.
    """
    results = []

    for schedule in schedules:
        try:
            utc_cron, summary = convert_to_utc(schedule["cron"])
            results.append({"cron": utc_cron, "scheduleSummary": summary})
        except Exception as error:
            failed_item = dict(schedule)
            failed_item["error"] = str(error)
            results.append(failed_item)

    return results


def convert_to_utc(cron_text):
    """Convert one cron string to UTC. Returns (utc_cron, summary)."""
    timezone_name, fields = split_timezone_and_fields(cron_text)
    minute, hour, day_of_month, month, day_of_week = fields

    if not minute.isdigit() or not hour.isdigit():
        raise ValueError("Minute and hour must be fixed numbers (for example '6 19')")

    offset_minutes = get_utc_offset_in_minutes(timezone_name)

    # Work in "minutes since midnight" so we don't have to handle
    # hours and minutes separately.
    local_minutes = int(hour) * 60 + int(minute)
    utc_minutes = local_minutes - offset_minutes

    # If the UTC time lands before midnight or after the end of the day,
    # the run moves to the previous or next day.
    day_shift = 0
    if utc_minutes < 0:
        utc_minutes += MINUTES_PER_DAY
        day_shift = -1
    elif utc_minutes >= MINUTES_PER_DAY:
        utc_minutes -= MINUTES_PER_DAY
        day_shift = 1

    utc_hour = utc_minutes // 60
    utc_minute = utc_minutes % 60

    if day_shift != 0:
        day_of_week = shift_day_of_week(fields, day_shift)
        day_of_month, month = shift_day_of_month(fields, day_shift)

    utc_cron = f"{utc_minute} {utc_hour} {day_of_month} {month} {day_of_week}"

    local_cron = " ".join(fields)
    check_both_crons_run_at_same_times(local_cron, timezone_name, utc_cron)

    summary = build_summary(utc_cron, utc_hour, utc_minute)
    return utc_cron, summary


def split_timezone_and_fields(cron_text):
    """
    Separate the optional "TZ=..." prefix from the five cron fields.

    "TZ=Asia/Calcutta 6 19 * * *"  ->  ("Asia/Calcutta", ["6", "19", "*", "*", "*"])
    """
    parts = cron_text.split()
    timezone_name = DEFAULT_TIMEZONE

    if parts and (parts[0].startswith("TZ=") or parts[0].startswith("CRON_TZ=")):
        prefix = parts.pop(0)
        timezone_name = prefix.split("=", 1)[1].strip("\"'")

    if len(parts) != 5:
        raise ValueError(f"Expected 5 cron fields, got {len(parts)}")

    return timezone_name, parts


def get_utc_offset_in_minutes(timezone_name):
    """
    Return how far the timezone is ahead of UTC, in minutes (IST = 330).

    Timezones with daylight saving time are rejected, because their
    offset changes during the year and a single UTC cron can't follow that.
    """
    zone = ZoneInfo(timezone_name)

    winter_offset = datetime(2026, 1, 1, tzinfo=zone).utcoffset()
    summer_offset = datetime(2026, 7, 1, tzinfo=zone).utcoffset()

    if winter_offset != summer_offset:
        raise ValueError(
            f"{timezone_name} uses daylight saving time, so it can't be "
            "converted to a single fixed UTC cron"
        )

    return int(winter_offset.total_seconds() // 60)


def shift_day_of_week(fields, day_shift):
    """
    Move the day-of-week field by one day.
    For example, Monday 03:00 IST is Sunday 21:30 UTC.
    """
    day_of_week = fields[4]
    if day_of_week == "*":
        return day_of_week

    # croniter turns things like "MON", "1-5" or "7" into plain day numbers.
    expanded_fields = croniter.expand(" ".join(fields))[0]
    local_days = expanded_fields[4]

    utc_days = set()
    for day in local_days:
        utc_days.add((int(day) + day_shift) % 7)

    return ",".join(str(day) for day in sorted(utc_days))


def shift_day_of_month(fields, day_shift):
    """
    Move the day-of-month field by one day. Returns (day_of_month, month).

    We work out the real UTC date for every month the schedule runs in.
    Examples:
      - 4th of every month, 03:00 IST   -> 3rd of every month in UTC
      - 1 January, 02:30 IST            -> 31 December in UTC
      - 31st of every month, 03:00 IST  -> 30th of Jan, Mar, May, Jul, Aug, Oct, Dec
        (the 31st only exists in those months, so the job only ever ran then)

    It fails when the UTC dates can't be written as one cron line, for example
    "1st of every month, 03:00 IST", which lands on the 31st, 30th, 28th or
    29th of the previous month in UTC.
    """
    day_of_month, month = fields[2], fields[3]

    if day_of_month == "*":
        if month != "*":
            raise ValueError(
                "This month-specific schedule crosses into another month in UTC "
                "and can't be converted exactly"
            )
        return day_of_month, month

    if not day_of_month.isdigit():
        raise ValueError(f"Can't shift a complex day-of-month value: '{day_of_month}'")

    local_day = int(day_of_month)

    if month == "*":
        months = range(1, 13)
    else:
        # croniter turns things like "JAN", "1-3" or "1,4,7,10" into month numbers.
        months = croniter.expand(" ".join(fields))[0][3]

    utc_dates = set()
    for month_number in months:
        month_number = int(month_number)

        # Check the date in a leap year (2024) and a normal year (2025),
        # because the end of February differs between them.
        exists_in_leap_year = local_day <= calendar.monthrange(2024, month_number)[1]
        exists_in_normal_year = local_day <= calendar.monthrange(2025, month_number)[1]

        if not exists_in_leap_year and not exists_in_normal_year:
            continue  # e.g. 31 April: the job never runs in this month

        if exists_in_leap_year != exists_in_normal_year:
            raise ValueError(
                "29 February only exists in leap years, and that run moves to "
                "28 February in UTC, so it can't be converted exactly"
            )

        leap_year_result = date(2024, month_number, local_day) + timedelta(days=day_shift)
        normal_year_result = date(2025, month_number, local_day) + timedelta(days=day_shift)

        if (leap_year_result.month, leap_year_result.day) != (normal_year_result.month, normal_year_result.day):
            raise ValueError(
                "This date shifts across the end of February in UTC, which "
                "changes in leap years, so it can't be converted exactly"
            )

        utc_dates.add((normal_year_result.day, normal_year_result.month))

    utc_days = sorted({day for day, _ in utc_dates})
    if len(utc_days) != 1:
        raise ValueError(
            "In UTC these runs land on different days of the month "
            f"({', '.join(str(day) for day in utc_days)}), which one cron line can't express"
        )

    utc_months = sorted({month_number for _, month_number in utc_dates})
    if len(utc_months) == 12:
        month_field = "*"
    else:
        month_field = ",".join(str(month_number) for month_number in utc_months)

    return str(utc_days[0]), month_field


def check_both_crons_run_at_same_times(local_cron, timezone_name, utc_cron):
    """
    Safety check: step through future run times of both crons and make
    sure they are identical. We check up to 2034 so leap years
    (2028, 2032) are covered.
    """
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    local_runs = croniter(local_cron, start.astimezone(ZoneInfo(timezone_name)))
    utc_runs = croniter(utc_cron, start)

    for _ in range(1000):
        local_run = local_runs.get_next(datetime)
        utc_run = utc_runs.get_next(datetime)

        if local_run != utc_run:
            raise ValueError(
                f"Conversion check failed: original runs at {local_run.isoformat()}, "
                f"but the UTC cron runs at {utc_run.isoformat()}"
            )

        if local_run.year > 2034:
            break


def build_summary(utc_cron, utc_hour, utc_minute):
    """Create a readable description, e.g. 'Daily at 13:36 UTC'."""
    time_text = f"{utc_hour:02d}:{utc_minute:02d}"

    runs_every_day = utc_cron.endswith("* * *")
    if runs_every_day:
        return f"Daily at {time_text} UTC"

    # For weekly, monthly and yearly schedules, let cron-descriptor write
    # the sentence, then add "UTC" right after the time.
    options = Options()
    options.use_24hour_time_format = True
    description = str(ExpressionDescriptor(utc_cron, options))

    return description.replace(time_text, f"{time_text} UTC", 1)
