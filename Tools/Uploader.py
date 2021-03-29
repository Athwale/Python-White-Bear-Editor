import pysftp


class Uploader:

    def __init__(self, ip: str, port: int, user: str, key: str):
        """
        Constructor of the SFTP class.
        :param ip: Server IPv4 address.
        :param port: SFTP port.
        :param user: SFTP user name.
        :param key: RSA private SFTP key file.
        """
        self._ip = ip
        self._port = port
        self._user = user
        self._priv_key = key
        self._connection = None

    def connect(self) -> None:
        """
        Connect to a SFTP server using a SSH RSA key.
        :return: None
        """
        print(self._ip, self._port, self._user, self._priv_key)
        # todo use this to do verify the server.
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        self._connection = pysftp.Connection(host=self._ip,
                                             port=self._port,
                                             username=self._user,
                                             private_key=self._priv_key,
                                             cnopts=cnopts,
                                             private_key_pass='')
        print(self._connection.listdir())
        self._connection.close()

