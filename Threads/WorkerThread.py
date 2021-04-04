import threading

import wx


class WorkerThread(threading.Thread):
    """
    Runs the function passed in arguments and calls the callback passed in arguments with the result of the function.
    """

    def __init__(self, parent, function, args, callback):
        """
        Convertor thread constructor. This thread runs a function from arguments and returns the result back to gui
        using wx.CallAfter and a callback function from the arguments..
        :param parent: The gui object that should receive the result.
        :param function: callable function.
        :param args: function arguments.
        :param callback: callable function for wx.CallAfter.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._function = function
        self._callback = callback
        self._args = args

    def run(self) -> None:
        """
        Runs a function with it's arguments and passes the result back into gui using wx.CallAfter and the callback
        function, the result of function is passed into the callback function as one argument.
        :return: None, this method calls the wx.CallAfter to pass the result back into GUI.
        """
        result = self._function(*self._args)
        wx.CallAfter(self._callback, result)
