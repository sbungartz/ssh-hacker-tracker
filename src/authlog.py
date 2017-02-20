import pandas as pd
import numpy as np
from dateutil.tz import tzlocal
import os
import gzip
import locale
import glob


def log_headers_to_df(log_lines, log_year, log_timezone):
    # load given log_lines into single columned data frame
    lines_df = pd.DataFrame({'logline': list(log_lines)})
    if len(lines_df) == 0:
        return pd.DataFrame()

    # match the log headers like
    # Jan  8 09:50:53 MY_MACHINE sshd[5908]: Disconnecting: Too many authentication failures for root [preauth]
    # into groups:
    # - Date:         'Jan  8 09:50:53'
    # - Machine name: 'MY_MACHINE'
    # - Program name: 'sshd'
    # - 'Action ID':  '5908'
    # - Message:      'Disconnecting: Too many authentication failures for root [preauth]'
    df = lines_df.logline.str.extract(
        r'^(?P<datestring>[A-z]+\s+\d+ [\d\W\:]+) (?P<machine>\S+) '
        r'(?P<program>[\w-]+)(?:\[(?P<action>\d+)\])?: (?P<message>.*)$',
        expand=True)

    # parse types where necessary:

    # replace datestring column with date column
    # TODO Need to deal with locales better than this: right now we suddenly change the locale for the entire process
    locale.setlocale(locale.LC_TIME, 'C')
    df['date'] = pd.to_datetime(df.datestring, format='%b %d %H:%M:%S')
    df = df.drop('datestring', axis=1)
    # since the log does not contain a year, we set it to the current year or the given log_year (from file timestamp)
    df.date = df.date.apply(lambda x: x.replace(year=log_year))
    df.date = df.date.dt.tz_localize(log_timezone)
    # now if the log file wraps over to a new year, we do best-effort detection to set the old logs to the previous year
    if df.date[0] > df.date[-1]:
        first_month = df.date[0].month
        df.date = df.date.apply(lambda x: x.replace(year=log_year - 1 if x.month >= first_month else log_year))

    # the action ID is numeric
    df.action = df.action.apply(pd.to_numeric)

    return df


def load_current_log():
    return load_local_log('/var/log/auth.log')


def load_all_logs(dir='/var/log'):
    files = glob.glob(os.path.join(dir, 'auth.log*'))
    files.sort(reverse=True) # Sort reversed, so we read the oldest log (with highest number) first
    return pd.concat([load_local_log(f) for f in files])


def load_local_log(filename):
    timezone = 'Europe/Berlin'
    log_year = pd.to_datetime(os.path.getmtime(filename), unit='s').tz_localize('UTC').tz_convert(timezone).year
    with open_maybe_gzip(filename) as f:
        return log_headers_to_df(f, log_year=log_year, log_timezone=timezone)


def open_maybe_gzip(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename)
    else:
        return open(filename)


def extract_probed_users(df):
    return df.message.str.extract('input_userauth_request: invalid user (\w+)', expand=False)


def extract_failed_password_users(df):
    return df.message.str.extract('Failed password for (\w+)', expand=False)


def extract_disconnect_ip(df):
    return df.message.str.extract('Received disconnect from ((?:[0-9]{1,3}\.){3}[0-9]{1,3})', expand=False)


