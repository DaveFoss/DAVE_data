class OutOfBbox(Exception):
    def __init__(self, errors):
        super().__init__(errors)
        self.errors = errors


class InvalidBbox(Exception):
    def __init__(self, errors):
        super().__init__(errors)
        self.errors = errors


class InvalidEPSG(Exception):
    def __init__(self, errors):
        super().__init__(errors)
        self.errors = errors
