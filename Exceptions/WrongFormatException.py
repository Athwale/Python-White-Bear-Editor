class WrongFromatException(Exception):
    __message = None

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(WrongFromatException, self).__init__(message)
        self.__message = message

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__message
