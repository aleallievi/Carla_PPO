import os
import psutil
import signal
import argparse

def kill_carla(SERVERNAME='Carla', CLIENTNAME='leaderboard_evaluator', kill_client=False):
    """
    Kill all CARLA processes
    """
    print('Killing existing CARLA servers...')
    for proc in psutil.process_iter():
        if SERVERNAME in proc.name():
            pid = proc.pid
            os.killpg(os.getpgid(pid), signal.SIGTERM)
    if kill_client:
        os.system(f'pkill -f {CLIENTNAME}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Kill Carla')
    parser.add_argument('--server-name-kw', type=str, default='Carla', required=False, help='Keyword in server name')
    parser.add_argument('--client-name-kw', type=str, default='auto_pilot_agent', required=False, help='Keyword in client name')
    parsed = parser.parse_args()
    print(parsed.server_name_kw)
    kill_carla(parsed.server_name_kw, parsed.client_name_kw)
