import http.server
import socketserver


class Webserver:

    def __init__(self):
        """
        Server constructor.
        """
        self._port: int = 8000

    def run(self) -> None:
        """
        Run the server.
        :return: None
        """
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(('127.0.0.1', self._port), handler) as httpd:
            httpd.serve_forever()


if __name__ == '__main__':
    server = Webserver()
    server.run()
