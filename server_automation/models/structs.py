import enum


class EnvironmentTypes(enum.Enum):
    """
    Types of environment.
    """

    QA = 1
    DEV = 2
    PROD = 3


class ResponseCode(enum.Enum):
    """
    Types of server responses
    """

    Ok = 200  # server return ok status
    ChangeOk = 201  # server was return ok for changing
    ValidationErrors = 400  # bad request
    StatusNotFound = 404  # status\es not found on db
    DuplicatedError = 409  # in case of requesting package with same name already exists
    GatewayTimeout = 504  # some server didn't respond
    ServerError = 500  # problem with error


class JobStatus(enum.Enum):
    """
    Types of job statuses
    """

    Completed = "Completed"
    Failed = "Failed"
    InProgress = "In-Progress"
    Pending = "Pending"
