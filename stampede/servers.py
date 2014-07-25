import logging
import os
import psutil
import time

from stampede import errors

log = logging.getLogger(__name__)


PAUSE_SECONDS = 3
MAX_TRIES = 5

class GunicornServer():

    def __init__(self, instance, instance_map, pidfile_dir):
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
        self.pidfile = os.path.join(pidfile_dir, '%s.pid' % self.name)
        pid = self._read_pidfile()
        self.process = psutil.Process(pid) if pid else None

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
    def port(self):
        return '4%03d2' % int(self.instance)

    def start(self):
        """Start an instance."""
        if self.running:
            log.info('%s is already running' % self.name)

        else:
            server_args = {
                    'bind': '0.0.0.0:%s' % self.port,
                    'chdir': self.cfg['app_basedir'],
                    'workers': self.cfg['worker_count'],
                    'pid': self.pidfile,
                    'name': self.name,
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

    def _read_pidfile(self):
        if not os.path.exists(self.pidfile):
            return None
        try:
            with open(self.pidfile, 'r') as f:
                pid = f.read()
        except IOError as err:
           raise
        return int(pid)
