# stampede

Framework for running many Gunicorn WSGI containers.

Provides:
+ Unified way to run one or many [Gunicorn](http://gunicorn.org/) servers
+ Simple configuration with override-able defaults
+ Ability to start/stop/status/restart one, multiple or all servers at once
+ Defaults to running on unprivileged ports (in user space) for convenience and security
+ Logging

## Installation

Stampede has been tested on FreeBSD and Linux and requires two Python libraries: PyYAML and psutil.  These procedures assume that Stampede and your applications each have, and run in, their own Python virtual environments.

### Step 1: Install Stampede

Untar this project into the folder (and with the user) of your choice.

Good practice suggests you set up a dedicated virtual environment to accomplish this. Many teams will create this enviroment under an ```env/``` sub-directory at the top of your newly untarred project directory.  When ready, you can install the Stampede dependencies using ```pip install setup/requirements.txt```

Your application's own environment will remain isolated from the one you establish for Stampede.

### Step 2: Ready Your Application

Add Gunicorn to your app's virtual environment.
+ Activate its virtual env
+ ```pip install gunicorn```

### Step 3: Configure Stampede

Edit Stampede's ```etc/instances.yml``` for each instance you will be running. An example is provided, that looks like this:

```
100:
  app_basedir: /home/peter/git/webfiles
  app_gunicorn_spec: 'webfiles:app'
  gunicorn_binary: /home/peter/pyenv/webfiles/bin/gunicorn
```

The minimal configuration requires just these three settings per Gunicorn server.  (Note that by installing gunicorn in your app's virtual env, your gunicorn_binary setting can be used to infer and activate the correct environment). For now, please use three-digit instance numbers.

You may also specify these items, but if not, reasonable defaults will be used:
+ ip_address (default: 0.0.0.0, all interfaces)
+ port (default: 4xxx2, where xxx is the instance number; e.g., instance 100 listens on port 41002)
+ workers_count (default: # of CPUs * 2 + 1, per Gunicorn's recommendations)

## Running Stampede

File ```bin/shep``` is the script to run.  Use --help to see its instructions:


```
  usage: shep [-h] [-v | -q] {stop,start,status,restart} instance [instance ...]

  positional arguments:
    {stop,start,status,restart}   operation to perform
    instance                      server numbers

  optional arguments:
    -h, --help            show this help message and exit
    -v, --verbose         show debug logging on console
    -q, --quiet           suppress non-error logging on console
```

You may use the word ```all``` as an instance argument to task every instance at once.

Stampede's log is located in the ```var/log/``` subdirectory.

## Feedback
Please ask any questions, report problems, and provide feedback to:  peterjpierce@gmail.com

Thank you!
