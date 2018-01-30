#!/usr/bin/env python3
import argparse
import json
import logging
import sys
import time
import subprocess

# Load logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(
    # filename='data_quality.log',
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

parser = argparse.ArgumentParser(description='Show transversal xml properties.')
parser.add_argument('--debug', '-d', dest='debug', action='store_true', default=False, help='Debug mode')
parser.add_argument('--config', '-c', dest='config', default='config.json', help='Config file')
parser.add_argument('--idle', '-i', dest='idle', default=None, type=float, help='idle time after which we start the process, 30 if no conf provided')
parser.add_argument('--freq', '-f', dest='freq', default=None, type=float, help='inactivity check frequency (s), 0.5 if no conf provided')
parser.add_argument('--idle-freq', '-if', dest='idle_freq', default=5,
                    help='inactivity check frequency during idle time (provide more reactivity when you come back, by default freq is used)')


def load_config(config):
    with open(config, 'r') as f:
        return json.load(f)


def get_idle():
    return int(subprocess.check_output("xprintidle").decode("utf-8").strip()) / 1000.0


def trigger_delayed(delay_proc):
    if delay_proc:
        running = subprocess.check_output(["ps", "axs"])
        for proc in delay_proc:
            if proc in str(running):
                return True
    return False


if __name__ == "__main__":
    args = parser.parse_args()

    conf = load_config(args.config)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # set idle time (seconds)
    idle = args.idle or conf.get('idle') or 30
    freq = args.freq or conf.get('freq') or 0.5
    idle_freq = args.idle_freq or conf.get('idle-freq') or freq

    # set commands
    trigger_cmd = conf['trigger_cmd'].split(' ')
    kill_cmd = conf['kill_cmd'].split(' ')
    delay_proc = conf.get('delay_processes', [])

    should_run = False
    running = False
    last_idle = 0
    new_idle = 0
    log.debug("Starting Idle check every %s, start after %s" % (freq, idle))
    while True:
        time.sleep(freq) if not running else time.sleep(idle_freq)

        new_idle = get_idle()

        if new_idle >= idle and last_idle < idle:
            log.info("Inactivity detected, we should start the process.")
            should_run = True

        elif new_idle <= idle and last_idle > idle:
            log.info("Input detected we should stop the process.")
            should_run = False

        if should_run and not running:
            if not trigger_delayed(delay_proc):
                log.info("Inactivity detected, starting process.")
                subprocess.Popen(trigger_cmd)
                running = True
            else:
                log.debug("Processus found, delaying process")

        if not should_run and running:
            log.info("Activity detected, killing process.")
            subprocess.Popen(kill_cmd)
            running = False

        last_idle = new_idle
