from datetime import date, datetime, timezone

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