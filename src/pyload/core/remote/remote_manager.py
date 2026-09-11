# -*- coding: utf-8 -*-
# AUTHOR: mkaay

from builtins import object
from threading import Thread


class BackendBase(Thread):
    def __init__(self, manager):
        super().__init__()
        self.m = self.manager = manager
        self.pyload = manager.pyload
        self._ = manager.pyload._
        self.enabled = True

    def run(self):
        try:
            self.serve()
        except Exception as exc:
            self.pyload.log.error(
                self._("Remote backend error: {}").format(exc),
                exc_info=self.pyload.debug > 1,
                stack_info=self.pyload.debug > 2,
            )

    def setup(self, host, port):
        pass

    def checkDeps(self):
        return True

    def serve(self):
        pass

    def shutdown(self):
        pass

    def stop(self):
        self.enabled = False  #: set flag and call shutdowm message, so thread can react
        self.shutdown()


class RemoteManager(object):
    available = []

    def __init__(self, core):
        self.pyload = core
        self._ = core._
        self.backends = []

    def start_backends(self):
        return
