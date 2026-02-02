from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def get_month_range(year: int, month: int) -> tuple[date, date]:
        start = date(year, month, 1)

        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        return start, end

def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)

def utc_to_local_time(dt: datetime | None) -> str:
    if not dt:
        return ""

    if dt.tzinfo is None:
        # assume UTC if naive
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    local_dt = dt.astimezone(IST)
    return local_dt.strftime("%I:%M %p")

def resolve_date_range(
    start_date: date | None,
    end_date: date | None,
):
    today = date.today()

    if not end_date:
        end_date = today

    if not start_date:
        start_date = end_date - relativedelta(months=3)

    return start_date, end_date