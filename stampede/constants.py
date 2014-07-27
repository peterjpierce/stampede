import multiprocessing

DEFAULT_IP_ADDRESS = '0.0.0.0'
DEFAULT_PORT_PATTERN = '4%03d2'
DEFAULT_WORKERS_COUNT = multiprocessing.cpu_count() * 2 + 1

DEBUG = True

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'basic': {
                'format': '%(asctime)s [%(process)5d] (%(name)s) %(levelname)s - %(message)s',
                },
            },
        'handlers': {
            'logfile': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': None, # populated by module stampede.context
                'when': 'W6',
                'backupCount': 26,
                'level': 'DEBUG' if DEBUG else 'INFO',
                'formatter': 'basic',
                },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG' if DEBUG else 'INFO',
                'formatter': 'basic',
                'stream': 'ext://sys.stdout',
                },
            },
        'root': {
            # most verbose here, let handlers be the filters
            'level': 'DEBUG',
            'handlers': ['logfile', 'console'] if DEBUG else ['logfile',],
            },
        }
