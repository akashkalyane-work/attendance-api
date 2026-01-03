from enum import Enum

class AttendanceRequestType(str, Enum):
    FORGOT_CLOCK_IN = "FORGOT_CLOCK_IN"
    FORGOT_CLOCK_OUT = "FORGOT_CLOCK_OUT"
    TIME_EDIT = "TIME_EDIT"


class AttendanceRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"