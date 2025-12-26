from datetime import date, timedelta

def get_month_range(year: int, month: int) -> tuple[date, date]:
        start = date(year, month, 1)

        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        return start, end