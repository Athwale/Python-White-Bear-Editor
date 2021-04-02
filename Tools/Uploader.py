import os
import wx
import paramiko

from Constants.Constants import Strings, Numbers
from Exceptions.AccessException import AccessException
from Exceptions.TransferException import TransferException


class Uploader:

    def __init__(self, parent, ip: str, port: int, user: str, key: str, passphrase: str):
        """
        Constructor of the SFTP class.
        :param parent: The gui object that should receive the results.
        :param ip: Server IPv4 address.
        :param port: SFTP port.
        :param user: SFTP user name.
        :param key: RSA private SFTP key file.
        :param passphrase: RSA key passphrase.
        """
        self._parent = parent
        self._ip = ip
        self._port = port
        self._user = user
        self._priv_key = key
        self._passphrase = passphrase
        self._sftp_connection = None
        self._ssh_connection = None

    def connect(self) -> None:
        """
        Connect to a SFTP server using a SSH RSA key.
        :return: None
        """
        # Public part of the user's RSA keys must be in the right place on the proftpd SFTP server.
        # The SFTP server has it's own RSA private and public (host) key used to authenticate it self to the client.
        # The public SFTP key must be added to known hosts using ssh key scan.
        try:
            if self._passphrase:
                key = paramiko.RSAKey.from_private_key_file(self._priv_key, password=self._passphrase)
                del self._passphrase
            else:
                key = paramiko.RSAKey.from_private_key_file(self._priv_key)
        except paramiko.PasswordRequiredException as e:
            raise paramiko.PasswordRequiredException(e)
        except paramiko.SSHException as _:
            raise AccessException(Strings.warning_rsa_passphrase_wrong)
        # Connect SSH client.
        self._ssh_connection = paramiko.SSHClient()
        self._ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh_connection.connect(self._ip, self._port, self._user, pkey=key, timeout=Numbers.connection_timeout)
        self._sftp_connection = self._ssh_connection.open_sftp()
        # Keep a reference to the SSH client in the SFTP client as to prevent the former from being garbage
        # collected and the connection from being closed.
        self._sftp_connection.sshclient = self._ssh_connection

    def upload_file(self, paths: (str, str)) -> str:
        """
        Upload one file to the SFTP server to the same location it is in inside the whitebear web working directory.
        :param paths: A tuple of local path and expected path on the server which is supposed to have the same folder
        structure. ('/home/other/test_web_xml/test.html', './test.html')
        :return: The uploaded filename if successful, exception if failed.
        """
        self._sftp_connection: paramiko.SFTPClient
        try:
            self._sftp_connection.put(paths[0], paths[1], confirm=True, callback=self.fail_upload)
        except (TransferException, IOError, OSError, EOFError) as _:
            raise TransferException(Strings.exception_sftp_fail, paths[0])
        return paths[0]

    def fail_upload(self, transferred: int, total: int) -> None:
        """
        Calculate percentage of transferred file and post the results into the gui.
        :param transferred: Bytes so far transferred.
        :param total: Total size of the file in bytes.
        :return: None
        """
        percentage = round(((100 / total) * transferred), 1)
        wx.CallAfter(self._parent.on_percentage_update, percentage)

    def check_folder_structure(self) -> bool:
        """
        Check that the folder structure on the server is what the website expects and create any missing folders.
        :return: True if no repairs were done.
        """
        result = True
        for folder in [os.path.join('.', Strings.folder_images),
                       os.path.join('.', Strings.folder_files),
                       os.path.join('.', Strings.folder_images, Strings.folder_logos),
                       os.path.join('.', Strings.folder_images, Strings.folder_originals),
                       os.path.join('.', Strings.folder_images, Strings.folder_thumbnails)]:
            try:
                self._sftp_connection.listdir(folder)
            except FileNotFoundError as _:
                result = False
                self._sftp_connection.mkdir(folder)
        return result

    def close_all(self) -> None:
        """
        Close all connections.
        :return: None
        """
        if self._sftp_connection is not None:
            self._sftp_connection.close()
        if self._ssh_connection is not None:
            self._ssh_connection.close()

