import multiprocessing

DEFAULT_IP_ADDRESS = '0.0.0.0'
DEFAULT_PORT_PATTERN = '4%03d2'
DEFAULT_WORKERS_COUNT = multiprocessing.cpu_count() * 2 + 1
