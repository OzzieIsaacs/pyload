# -*- coding: utf-8 -*-

import logging
import threading

from cheroot import wsgi
from cheroot.ssl.builtin import BuiltinSSLAdapter

from .app import App


# TODO: make configurable to serve API
class WebServerThread(threading.Thread):
    def __init__(self, pycore):
        super().__init__()
        self.daemon = True

        self.pyload = pycore

        self.develop = self.pyload.config.get("webui", "develop")

        self.use_ssl = self.pyload.config.get("webui", "use_ssl")  #: recheck
        self.certfile = self.pyload.config.get("webui", "ssl_certfile")
        self.keyfile = self.pyload.config.get("webui", "ssl_keyfile")
        self.certchain = self.pyload.config.get("webui", "ssl_certchain") or None

        self.host = self.pyload.config.get("webui", "host")
        self.port = self.pyload.config.get("webui", "port")
        self.prefix = self.pyload.config.get("webui", "prefix")
        locale = self.pyload.config.get("general", "language")

        # NOTE: Is really the right choice pass the pycore obj directly to app?!
        #       Or should we pass just core.api and server.logger instead?
        self.app = App(self.pyload, self.develop, self.prefix, locale)
        self.log = self.app.logger

    def _run_develop(self):
        # TODO: inject our custom logger in werkzeug code?
        # NOTE: use_reloader=True -> 'ValueError: signal only works in main thread'
        self.app.run(self.host, self.port, use_reloader=False)

    def _run_produc(self):
        bind_path = "/"
        if self.host == '':
            self.host = '0.0.0.0'
        bind_addr = (self.host, self.port)
        wsgi_app = wsgi.PathInfoDispatcher({bind_path: self.app})
        self.server = wsgi.Server(bind_addr, wsgi_app)

        if self.use_ssl:
            self.server.ssl_adapter = BuiltinSSLAdapter(
                self.certfile, self.keyfile, self.certchain
            )

        #: hack cheroot to use our custom logger
        self.server.error_log = lambda *args, **kwgs: self.log.log(
            kwgs.get("level", logging.ERROR), args[0], exc_info=self.pyload.debug
        )

        self.server.start()

    def stop(self):
        if not self.develop:
            try:
                self.server.stop()
            except AttributeError:
                pass
        else:
            pass
            # ToDo: Not implemented


    def run(self):
        self.log.info("Starting webserver: {scheme}://{host}:{port}".format(
                scheme="https" if self.use_ssl else "http", host=self.host, port=self.port
            )
        )

        try:
            if self.develop:
                self._run_develop()
            else:
                self._run_produc()

        except OSError as exc:
            #: Unfortunately, CherryPy raises socket.error without setting errno :(
            if exc.errno == 98 or isinstance(exc.args[0], str) and "Errno 98" in exc.args[0]:
                self.log.fatal(
                    self._("** FATAL ERROR ** Could not start web server - Address Already in Use | Exiting pyLoad")
                )
                self.pyload.api.kill()
            else:
                raise
