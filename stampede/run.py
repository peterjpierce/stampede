#!/usr/bin/env python

import logging
import os
from os.path import join
import signal
import subprocess
import sys

from stampede import context


def _call_os(os_args):
    """Run an OS command."""
    try:
        subprocess.check_call(os_args)
    except subprocess.CalledProcessError as err:
        return None
    return True


def _pidfile(pidfile_dir, instance):
    """Get path for the instance's pidfile."""
    return join(pidfile_dir, 'wsgi%s.pid' % instance)


def _start(instance_map, pidfile_dir, instance, log):
    """Start an instance."""
    cfg = instance_map[instance]
    server_args = {
            'bind': '0.0.0.0:4%s2' % instance,
            'chdir': cfg['app_basedir'],
            'workers': cfg['workers'],
            'pid': _pidfile(pidfile_dir, instance),
            'name': 'wsgi%s' % instance,
            }
    os_args = [cfg['gunicorn_binary'], cfg['app_gunicorn_spec'], '--daemon']
    for k,v in server_args.items():
        os_args.append('--%s=%s' % (k,v))
    log.info('starting instance %s' % instance)
    log.debug('args are: %s' % str(os_args))
    was_success = _call_os(os_args)
    return was_success


def _stop(pidfile_dir, instance, log):
    """Stop an instance."""
    try:
        with open(_pidfile(pidfile_dir, instance), 'r') as f:
            pid = f.read()
    except IOError as err:
       raise
    os.kill(int(pid), signal.SIGTERM)


def run(*args):

    pidfile_dir, config, instance_map, args = context.setup()
    log = logging.getLogger(__name__)
    print(args)

#    func = getattr(sys.modules[__name__], '_%s' % args.task)
#    for instance in instances:
#        func(instance)

    for instance in args.instances:

        if args.task == 'start':
            _start(instance_map, pidfile_dir, instance, log)

        elif args.task == 'stop':
            _stop(pidfile_dir, instance, log)


if __name__ == '__main__':
    run()
