import time
import paramiko

from Constants.Constants import Strings
from Exceptions.AccessException import AccessException


class Uploader:

    def __init__(self, ip: str, port: int, user: str, key: str, passphrase: str):
        """
        Constructor of the SFTP class.
        :param ip: Server IPv4 address.
        :param port: SFTP port.
        :param user: SFTP user name.
        :param key: RSA private SFTP key file.
        :param passphrase: RSA key passphrase.
        """
        self._ip = ip
        self._port = port
        self._user = user
        self._priv_key = key
        self._passphrase = passphrase
        self._sftp_connection = None
        self._ssh_connection = None

    def connect(self) -> bool:
        """
        Connect to a SFTP server using a SSH RSA key.
        :return: True if connection was successful.
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
        self._ssh_connection.connect(self._ip, self._port, self._user, pkey=key)
        self._sftp_connection = self._ssh_connection.open_sftp()
        # Keep a reference to the SSH client in the SFTP client as to prevent the former from being garbage
        # collected and the connection from being closed.
        self._sftp_connection.sshclient = self._ssh_connection

    def upload_file(self) -> None:
        """
        Upload one file
        :return: Something maybe
        """
        # todo this
        print(self._sftp_connection.listdir('.'))
        time.sleep(1)

    def close_all(self) -> None:
        """
        Close all connections.
        :return: None
        """
        if self._sftp_connection is not None:
            self._sftp_connection.close()
        if self._ssh_connection is not None:
            self._ssh_connection.close()

