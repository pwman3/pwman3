#!/usr/bin/env python

import sys
import os
from signal import SIGTERM


class Daemon(object):

    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, name, pidfile, stdin='/dev/null', stdout='/dev/null',
                 stderr='/dev/null', noisy=False):
        """
        initialize some properties needed later.
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.name = name
        self.noisy = noisy

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            print("SSSSSDDD")
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)

        pid = str(os.getpid())
        print("[%s pid: %s]" % (self.name, pid))
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+', 0)

        if not self.noisy:
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

        open(self.pidfile, 'w+').write("%s\n" % (pid))

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
            os.remove(self.pidfile)
        except IOError:
            pid = None
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            os.kill(pid, SIGTERM)
        except OSError, err:
            err = str(err)
            print err
            sys.exit(1)

    def check_proc(self):
        """
        check for pid file
        """
        # Check for a pidfile to see if the daemon already runs
        # instead opening self pidfile many times, we should just
        # set self.controlpid
        try:
            pf = open(self.pidfile, 'r')
            proc = pf.read()
            pid = int(proc.strip())
            pf.close()
            return pid
        except IOError:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def exit_running(self):
        """
        do not start if already running
        """
        if os.path.exists(self.pidfile):
            pf = open(self.pidfile, 'r')
            proc = pf.read()
            running = int(proc.strip())
            message = "pidfile %s already exists. Daemon already running?\n"
            message += "check if process %d still exists\n"
            sys.stderr.write(message % (self.pidfile, running))
            sys.exit(1)

    def startd(self):
        raise Exception("You should override this method!")

    def run(self):
        """
        You should override this method when you subclass Daemon. It will
        be called after the process has been
        daemonized by start() or restart().
        """
        raise Exception("You should override this method!")
