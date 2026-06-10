class ProcessorCanceled(Exception):
    """Raised when the running external processor is interrupted."""

    def __init__(self, message: str = "Procesamiento cancelado") -> None:
        super().__init__(message)
        self.message = message
