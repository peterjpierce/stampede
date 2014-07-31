import logging
import os
import psutil
import time

from stampede import errors

log = logging.getLogger(__name__)


PAUSE_SECONDS = 3
MAX_TRIES = 5
BASEDIR = os.path.abspath('%s/..' % os.path.dirname(__file__))
PIDFILE_DIR = '%s/var/run' % os.path.abspath('%s/..' % os.path.dirname(__file__))


class GunicornServer():

    def __init__(self, instance, instance_map):
        """Arg instance is the unique instance number, like 100.

       Current convention is that instance numbers are three digits
       in length and that servers bind to unprivileged ports in
       the 4xxx2 range, where xxx is the instance number.
        """
        try:
            self.cfg = instance_map[instance]
        except KeyError as err:
            raise errors.InvalidServerError(err)

        self.instance = instance
        self.pidfile = PIDFile(instance)
        self.process = psutil.Process(self.pidfile.pid) if self.pidfile.pid else None

    @property
    def running(self):
        if self.process and psutil.pid_exists(self.process.pid):
            return True
        else:
            return False

    @property
    def name(self):
        return 'wsgi%s' % self.instance

    @property
    def server_log(self):
        return os.path.join(BASEDIR, 'var', 'log', '%s.log' % self.name)

    def start(self):
        """Start an instance."""
        if self.running:
            log.info('%s is already running' % self.name)

        else:
            server_args = {
                    'bind': '%s:%s' % (self.cfg['ip_address'], self.cfg['port']),
                    'chdir': self.cfg['app_basedir'],
                    'workers': self.cfg['workers_count'],
                    'pid': self.pidfile.path,
                    'name': self.name,
                    'log-file': self.server_log,
                    }

            os_args = [
                    self.cfg['gunicorn_binary'],
                    self.cfg['app_gunicorn_spec'],
                    '--daemon',
                    ]

            for k,v in server_args.items():
                os_args.append('--%s=%s' % (k,v))

            log.info('starting %s' % self.name)
            log.debug('args are: %s' % str(os_args))
            self.process = psutil.Popen(os_args)

            if not self.running:
                log.error('server %s did not start' % self.name)

        return self.running

    def stop(self):
        """Stop an instance."""
        if self.running:
            cnt = 0
            identifier = '%s (%d)' % (self.name, self.process.pid)
            while cnt < MAX_TRIES and self.running:
                msg = '%s not stopped yet, retrying' if cnt else 'stopping %s'
                log.info(msg % identifier)
                self.process.terminate()
                time.sleep(PAUSE_SECONDS)
                cnt += 1

            if self.running:
                err = 'server %s did not stop' % identifier
                log.error(err)
                raise errors.ServerStopError(err)
            else:
                log.info('%s has stopped' % identifier)
                self.process = None

        else:
            log.info('%s is already stopped' % self.name)

    def status(self):
        """Get status for an instance."""
        if self.running:
            print('%s (%d) is running with %d child processes' % (
                    self.name,
                    self.process.pid,
                    len(self.process.children())))
        else:
            print('%s is not running' % self.name)

    def restart(self):
        """Restart an instance."""
        log.info('restarting %s' % self.name)
        self.stop()
        self.start()


class PIDFile():
    """Abstraction around and utilities for PID files."""

    def __init__(self, instance_num):
        self.instance = int(instance_num)

    @property
    def path(self):
        return os.path.join(BASEDIR, 'var', 'run', 'wsgi%03d.pid' % self.instance)

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def pid(self):
        value = self._read_pidfile()
        if value:
            if psutil.pid_exists(value):
                return value
            else:
                log.warn('removing stale pidfile %s (%d)' % (self.basename, value))
                os.remove(self.path)
        return None

    def _read_pidfile(self):
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path, 'r') as f:
                pid = f.read()
        except IOError as err:
           raise
        return int(pid)
