from twisted.internet import reactor
from twisted.conch.insults import insults
from twisted.conch import manhole, manhole_ssh
from twisted.cred.checkers import (
    InMemoryUsernamePasswordDatabaseDontUse as MemoryDB)
from twisted.cred.portal import Portal


class Shell(object):
    """
    Open SSH server giving a Python Shell with the current environment
    """

    def __init__(self, port, username, password):
        sshRealm = manhole_ssh.TerminalRealm()

        def chainedProtocolFactory():
            return insults.ServerProtocol(manhole.Manhole, globals())
        sshRealm.chainedProtocolFactory = chainedProtocolFactory

        portal = Portal(sshRealm, [MemoryDB(**{username: password})])
        reactor.listenTCP(port, manhole_ssh.ConchFactory(portal),
                          interface="127.0.0.1")
        reactor.run()

if __name__ == '__main__':

    s = Shell(4242, "user", "pw")
