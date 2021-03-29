import threading

import wx

from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Tools.Uploader import Uploader


class SftpThread(threading.Thread):
    """
    Connects to a SFTP server and transfers files to it.
    """

    def __init__(self, parent, ip: str, port: int, user: str, key: str):
        """
        Sftp thread constructor.
        :param parent: The gui object that should receive the result.
        :param ip: Server IPv4 address.
        :param port: SFTP port.
        :param user: SFTP user name.
        :param key: RSA private SFTP key file.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._uploader = Uploader(ip, port, user, key)

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.s
        """
        try:
            self._uploader.connect()
            #wx.CallAfter(self._parent.on_conversion_done, self, self._doc, self._save_as, self._disable)
        except UnrecognizedFileException as e:
            pass
            #wx.CallAfter(self._parent.on_conversion_fail, e)
