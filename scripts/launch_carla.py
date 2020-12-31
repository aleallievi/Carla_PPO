import os
import time
import subprocess
import argparse


def launch_carla_server(world_port=8000, gpu=0, boot_time=10):
    """Carla server instantiation"""
    os.environ["DISPLAY"] = ':0'
    # launches CarlaUE4.sh as subprocess
    cmd = f'/home/boschaustin/projects/CL_AD/Carla_PPO/CARLA_9_10_1/CarlaUE4.sh ' \
          f'--host=\'localhost\' ' \
          f'--carla-rpc-port={world_port} ' \
          f'--quality-level{{epic}} ' \
          f'--resx={800} ' \
          f'--resy={600} ' \
          f'--gpu={gpu}' \
          f'--opengl'

    carla_process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, preexec_fn=os.setsid)
    # give a few seconds to boot
    time.sleep(boot_time)
    return carla_process


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Launch Carla Server')
    parser.add_argument('--world-port', type=int, default=8000, required=False)
    parser.add_argument('--gpu', type=int, default=0, required=False)
    parsed = parser.parse_args()
    launch_carla_server(**vars(parsed))
