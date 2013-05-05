import sys

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.manhole.telnet import ShellFactory
from twisted.manhole.telnet import Shell


class MyShell(Shell):
    """ Twisted telnet shell replacement. """
    mode = "Command"

    def connectionMade(self):
        self.namespace = globals()
        Shell.connectionMade(self)

    def welcomeMessage(self):
        return chr(12) + "Oh hai" + "\r\n"

    def loginPrompt(self):
        return "\r\n>>> "

    @inlineCallbacks
    def doCommand(self, cmd):
        fn = "$telnet$"
        result = None
        try:
            out = sys.stdout
            sys.stdout = self
            try:
                code = compile(cmd, fn, "eval")
                result = eval(code, self.namespace)
                if isinstance(result, Deferred):
                    result = yield result
            except:
                try:
                    code = compile(cmd, fn, "exec")
                    exec(code in self.namespace)
                except Exception as e:
                    self.write("Internal error: %s.\r\n>>> " % e)
                    return
        finally:
            sys.stdout = out
        if result is not None:
            self.transport.write(repr(result))
            self.transport.write("\r\n")
        self.transport.write(">>> ")


if __name__ == "__main__":
    shell = ShellFactory()
    shell.protocol = MyShell
    # Open a Telnet server that will simulate a Python server
    # with the current environment
    reactor.listenTCP(4243, shell)
    reactor.run()
