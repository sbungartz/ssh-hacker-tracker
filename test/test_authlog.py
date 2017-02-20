import pytest
import authlog
import pandas as pd


log_normal = """Jan 14 21:17:01 SIMONLX CRON[6671]: pam_unix(cron:session): session opened for user root by (uid=0)
Jan 14 21:17:01 SIMONLX CRON[6671]: pam_unix(cron:session): session closed for user root
Jan 14 22:00:01 SIMONLX CRON[7307]: pam_unix(cron:session): session opened for user root by (uid=0)
Jan 14 22:00:02 SIMONLX CRON[7307]: pam_unix(cron:session): session closed for user root
Jan 14 22:16:49 SIMONLX sshd[7584]: reverse mapping checking getaddrinfo for 152.25.178.186.static.pichincha.andinanet.net [186.178.25.152] failed - POSSIBLE BREAK-IN ATTEMPT!
Jan 14 22:16:49 SIMONLX sshd[7584]: Invalid user kevin from 186.178.25.152
Jan 14 22:16:49 SIMONLX sshd[7584]: input_userauth_request: invalid user kevin [preauth]
Jan 14 22:16:51 SIMONLX sshd[7584]: error: maximum authentication attempts exceeded for invalid user kevin from 186.178.25.152 port 56150 ssh2 [preauth]
Jan 14 22:16:51 SIMONLX sshd[7584]: Disconnecting: Too many authentication failures for kevin [preauth]
Jan 14 22:17:01 SIMONLX CRON[7586]: pam_unix(cron:session): session opened for user root by (uid=0)
Jan 14 22:17:01 SIMONLX CRON[7586]: pam_unix(cron:session): session closed for user root
Jan 14 22:19:53 SIMONLX sshd[7612]: Invalid user ubnt from 49.231.153.151
Jan 14 22:19:53 SIMONLX sshd[7612]: input_userauth_request: invalid user ubnt [preauth]
Jan 14 22:19:54 SIMONLX sshd[7612]: error: maximum authentication attempts exceeded for invalid user ubnt from 49.231.153.151 port 54102 ssh2 [preauth]
Jan 14 22:19:54 SIMONLX sshd[7612]: Disconnecting: Too many authentication failures for ubnt [preauth]""".split('\n')


log_year_wrap = """Oct 16 09:57:29 SIMONLX sshd[7072]: Connection closed by 221.194.47.249 [preauth]
Oct 16 10:00:01 SIMONLX CRON[7162]: pam_unix(cron:session): session opened for user root by (uid=0)
Oct 16 10:00:01 SIMONLX CRON[7162]: pam_unix(cron:session): session closed for user root
Oct 16 10:03:47 SIMONLX polkitd(authority=local): Unregistered Authentication Agent for unix-session:c2 (system bus name :1.88, object path /org/gnome/PolicyKit1/AuthenticationAgent, locale de_DE.UTF-8) (disconnected from bus)
Oct 16 10:03:47 SIMONLX systemd-logind[1004]: System is powering down.
Jan  4 00:12:46 SIMONLX systemd-logind[1087]: New seat seat0.
Jan  4 00:12:46 SIMONLX systemd-logind[1087]: cgmanager: cgm_list_children for controller=systemd, cgroup_path=user failed: invalid request
Jan  4 00:12:46 SIMONLX systemd-logind[1087]: Watching system buttons on /dev/input/event1 (Power Button)
Jan  4 00:12:46 SIMONLX systemd-logind[1087]: Watching system buttons on /dev/input/event0 (Power Button)
Jan  4 00:12:47 SIMONLX sshd[1279]: Server listening on 0.0.0.0 port 22.
Jan  4 00:12:47 SIMONLX sshd[1279]: Server listening on :: port 22.""".split('\n')


def test_parse_empty_file():
    df = authlog.log_headers_to_df('', log_year=2017, log_timezone='UTC')
    assert len(df) == 0


def test_concat_actual_and_empty_file():
    df_empty = authlog.log_headers_to_df('', log_year=2017, log_timezone='Europe/Berlin')
    df_normal = authlog.log_headers_to_df(log_normal, log_year=2017, log_timezone='Europe/Berlin')
    df = pd.concat([df_empty, df_normal])
    assert len(df) == len(log_normal)


def test_parse_year_wrap():
    df = authlog.log_headers_to_df(log_year_wrap, log_year=2017, log_timezone='Europe/Berlin')
    assert df.date.equals(pd.to_datetime(pd.Series([
        '2016-10-16 09:57:29',
        '2016-10-16 10:00:01',
        '2016-10-16 10:00:01',
        None,
        '2016-10-16 10:03:47',
        '2017-01-04 00:12:46',
        '2017-01-04 00:12:46',
        '2017-01-04 00:12:46',
        '2017-01-04 00:12:46',
        '2017-01-04 00:12:47',
        '2017-01-04 00:12:47',
    ])).dt.tz_localize('Europe/Berlin'))

