class IndexException(Exception):
    """
    Exception representing an error while working with index.html.
    """

    def __init__(self, message: str):
        """
        Create new exception and store the user readable message.
        :param message: User readable message.
        """
        # Call the base class constructor with the parameters it needs
        super(IndexException, self).__init__(message)
        self._message: str = message

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self._message
