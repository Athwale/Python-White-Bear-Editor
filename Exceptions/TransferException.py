class TransferException(Exception):
    """
    Exception representing an error while transferring a file.
    """

    def __init__(self, message: str, file: str):
        """
        Create new exception and store the user readable message.
        :param message: User readable message.
        """
        # Call the base class constructor with the parameters it needs
        super(TransferException, self).__init__(message)
        self._message: str = message
        self._file: str = file

    def get_file(self) -> str:
        """
        Return the file path that failed.
        :return: The file path that failed.
        """
        return self._file

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self._message
