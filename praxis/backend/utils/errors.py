class ExperimentError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class DataError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class ModelError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class AssetAcquisitionError(RuntimeError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class ProtocolCancelledError(Exception):
    def __init__(self, message="Protocol run was cancelled."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
