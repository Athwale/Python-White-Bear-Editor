import socket
import threading
from typing import List, Tuple

import wx
from paramiko.ssh_exception import PasswordRequiredException
from paramiko.ssh_exception import SSHException

from Constants.Constants import Strings
from Exceptions.AccessException import AccessException
from Exceptions.TransferException import TransferException
from Tools.Uploader import Uploader


class SftpThread(threading.Thread):
    """
    Connects to a SFTP server and transfers files to it.
    """

    def __init__(self, parent, ip: str, port: int, user: str, key: str, password, files: List[Tuple[str, str]]):
        """
        Sftp thread constructor.
        :param parent: The gui object that should receive the result.
        :param ip: Server IPv4 address.
        :param port: SFTP port.
        :param user: SFTP username.
        :param key: RSA private SFTP key file.
        :param password: RSA passphrase.
        :param files: List of file paths to upload
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._uploader = Uploader(parent, ip, port, user, key, password)
        self._stop_event = threading.Event()
        self._files_to_upload = files

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass results back into GUI.
        """
        try:
            self._uploader.connect()
            wx.CallAfter(self._parent.on_connection_established, Strings.status_established)
            result = self._uploader.check_folder_structure()
            if not result:
                wx.CallAfter(self._parent.on_structure_repair)

            for file in self._files_to_upload:
                # Show which file is being uploaded.
                wx.CallAfter(self._parent.on_file_upload_start, file[0])
                wx.CallAfter(self._parent.on_percentage_update, 0)
                if self._stop_event.is_set():
                    break
                try:
                    finished_upload = self._uploader.upload_file(file)
                    wx.CallAfter(self._parent.on_file_upload_finished, finished_upload, False)
                except TransferException as e:
                    # Report fail and continue with other files.
                    wx.CallAfter(self._parent.on_file_upload_finished, e.get_file(), True)

            wx.CallAfter(self._parent.on_connection_closed, Strings.status_closed)
            wx.CallAfter(self._parent.on_file_upload_start, Strings.status_finished)
        except (socket.timeout, socket.error) as e:
            wx.CallAfter(self._parent.on_connection_closed, f'{Strings.status_failed}: {e}')
        except PasswordRequiredException as _:
            wx.CallAfter(self._parent.on_key_password_required)
        except AccessException as _:
            wx.CallAfter(self._parent.on_key_password_wrong)
        except (SSHException, TimeoutError) as e:
            wx.CallAfter(self._parent.on_connection_closed, f'{Strings.status_failed}: {e}')
        except ValueError:
            wx.CallAfter(self._parent.on_connection_closed, f'{Strings.status_failed}: '
                                                            f'{Strings.warning_rsa_encryption_fail}')
        finally:
            self._uploader.close_all()

    def stop(self, force=False) -> None:
        """
        Stop the execution of this thread at the end of the previous upload operation.
        :param force: If true the connection is closed even during transfer, this may produce EOFError. This is unsafe
        and may leave corrupted files on the server.
        :return: None
        """
        if force:
            try:
                self._uploader.close_all()
            except EOFError as _:
                pass
        self._stop_event.set()
