import multiprocessing

"""
Note that gunicorn_binary should be in, and implies, an app-specific
virtual_env for each server instance.
"""

INSTANCE_MAP = {
        '100': {
            'app_basedir': '/home/peter/git/webfiles',
            'app_gunicorn_spec': 'webfiles:app',
            'gunicorn_binary': '/home/peter/pyenv/webfiles/bin/gunicorn',
            'workers': multiprocessing.cpu_count() * 2 + 1,
            },
        '400': {
            'app_basedir': '/home/ppierce/git/video_credentials',
            'app_gunicorn_spec': 'incredible:app',
            'gunicorn_binary': '/home/ppierce/pyenv/vcreds/bin/gunicorn',
            'workers': multiprocessing.cpu_count() * 2 + 1,
            },
        }
