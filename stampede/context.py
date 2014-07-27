from argparse import ArgumentParser
import datetime
import logging
import logging.config
import os

from stampede import constants, util

COLUMNS = 140


class ArgsWrapper():
    """Wraps argparse."""

    def __init__(self):
        self.parser = ArgumentParser(description='Manage gunicorn servers')
        self._build()

    def parse(self):
        """Parse the command line and return results."""
        args = self.parser.parse_args()
        if args.task in ['status',]:
            console_level = 'ERROR'
        elif args.verbose:
            console_level = 'DEBUG'
        elif args.quiet:
            console_level = 'ERROR'
        else:
            console_level = 'INFO'
        return (args, console_level)

    def _build(self):
        """Initialize with arguments."""
        self.parser.add_argument(
                    'task', help='operation to perform',
                    choices=['stop', 'start', 'status', 'restart'])
        self.parser.add_argument(
                'instances', metavar='instance', nargs='+', help='server numbers')
        exclusive = self.parser.add_mutually_exclusive_group()
        exclusive.add_argument('-v', '--verbose', action='store_true',
                help='show debug logging on console')
        exclusive.add_argument('-q', '--quiet', action='store_true',
                help='suppress non-error logging on console')


def setup():
    """Learn and return context."""
    args_parser = ArgsWrapper()
    args, console_logging_level = args_parser.parse()

    # context
    os.environ['COLUMNS'] = str(COLUMNS)
    basedir = os.path.abspath('%s/..' % os.path.dirname(__file__))
    util.make_dir('%s/var/run' % basedir)

    # instance map
    instance_map = util.read_yaml('%s/etc/instances.yml' % basedir)
    for inst_num, cfg in instance_map.items():
        # normalize keys to be strings
        if not isinstance(inst_num, str):
            instance_map[str(inst_num)] = cfg
            del instance_map[inst_num]
        # apply defaults where needed
        if not 'ip_address' in cfg:
            cfg['ip_address'] = constants.DEFAULT_IP_ADDRESS
        if not 'port' in cfg:
            cfg['port'] = constants.DEFAULT_PORT_PATTERN % int(inst_num)
        if not 'workers_count' in cfg:
            cfg['workers_count'] = constants.DEFAULT_WORKERS_COUNT

    # logging
    year = datetime.datetime.now().strftime('%Y')
    logfile = '%s/var/log/stampede.log.%s' % (basedir, year)
    logconfig = dict(constants.LOGGING)
    logconfig['handlers']['logfile']['filename'] = logfile
    logconfig['handlers']['console']['level'] = console_logging_level
    util.make_parent_dir(logfile)
    logging.config.dictConfig(logconfig)

    return (args, instance_map)
