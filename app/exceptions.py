from __future__ import annotations


class AppException(Exception):
    def __init__(self, message: str, code: str = "ERROR", status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Credenciales inválidas") -> None:
        super().__init__(message, code="AUTH_ERROR", status_code=401)


class AuthorizationError(AppException):
    def __init__(self, message: str = "No tiene permisos para esta acción") -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Recurso", resource_id: int | str = 0) -> None:
        super().__init__(
            f"{resource} con ID {resource_id} no encontrado",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


class ConflictError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFLICT", status_code=409)


class ShiftBlockedError(AppException):
    def __init__(self, message: str = "Turno fuera de horario programado") -> None:
        super().__init__(message, code="SHIFT_BLOCKED", status_code=403)


class HourLimitExceededError(AppException):
    def __init__(self, employee: str, hours: float, limit: float = 44.0) -> None:
        super().__init__(
            f"{employee}: {hours:.1f}h semanales exceden límite de {limit}h",
            code="HOUR_LIMIT_EXCEEDED",
            status_code=409,
        )


class CashDrawerError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CASH_ERROR", status_code=409)


class DIANError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="DIAN_ERROR", status_code=502)


class PrinterError(AppException):
    def __init__(self, message: str = "Error de impresión") -> None:
        super().__init__(message, code="PRINTER_ERROR", status_code=500)


class StockInsufficientError(AppException):
    def __init__(self, product: str, available: float, requested: float) -> None:
        super().__init__(
            f"Stock insuficiente para '{product}': disponible {available}, solicitado {requested}",
            code="STOCK_INSUFFICIENT",
            status_code=409,
        )
