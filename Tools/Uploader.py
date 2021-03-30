import paramiko


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

    def connect(self) -> None:
        """
        Connect to a SFTP server using a SSH RSA key.
        :return: None
        """
        print(self._ip, self._port, self._user, self._priv_key)
        # Public part of the user's RSA keys must be in the right place on the proftpd SFTP server.
        # The SFTP server has it's own RSA private and public (host) key used to authenticate it self to the client.
        # The public SFTP key must be added to known hosts using ssh key scan.
        if self._passphrase:
            key = paramiko.RSAKey.from_private_key_file(self._priv_key, password=self._passphrase)
            del self._passphrase
        else:
            key = paramiko.RSAKey.from_private_key_file(self._priv_key)
        # Connect SSH client.
        ssh = paramiko.SSHClient()
        # todo close sftp and ssh on exception
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self._ip, self._port, self._user, pkey=key)
        sftp = ssh.open_sftp()
        # Keep a reference to the SSH client in the SFTP client as to prevent the former from being garbage collected
        # and the connection from being closed.
        sftp.sshclient = ssh

        print(sftp.listdir('.'))
