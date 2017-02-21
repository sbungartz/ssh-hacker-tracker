# default config values:
dataDirLogs = '/var/log'

# if local_config.py exists, import from there, to override
# TODO

# if set from env, overwrite from there
import os
dataDirLogs = os.getenv('DATA_DIR_LOGS', dataDirLogs)

print 'dataDirLogs = {}'.format(dataDirLogs)