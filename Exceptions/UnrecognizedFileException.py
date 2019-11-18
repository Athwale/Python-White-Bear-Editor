class UnrecognizedFileException(Exception):
    """Exception representing and unrecognized file type that does not belong to the whitebear website
    """
    __message: str

    def __init__(self, message: str):
        """Create new exception and store the user readable message.
        :param message: User readable message.
        """
        # Call the base class constructor with the parameters it needs
        super(UnrecognizedFileException, self).__init__(message)
        self.__message = message

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__message
