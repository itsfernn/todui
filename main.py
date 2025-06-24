import os
import argparse
import configparser
from icalendar import Todo

from dav import DavSession

from tui import run_tui

import caldav
import dotenv
import json

dotenv.load_dotenv()

SERVER = os.getenv("CALDAV_SERVER") or ""
USER = os.getenv("CALDAV_USER") or ""
PASSWORD = os.getenv("CALDAV_PASSWORD") or ""

def load_config():
    home_dir = os.getenv("HOME")

    if home_dir is None:
        raise RuntimeError("HOME environment variable is not set. Cannot determine config file path.")

    config_path = os.path.join(home_dir, ".config", "todui", "todui.conf")
    config = configparser.ConfigParser(allow_unnamed_section=True)
    config.read(config_path)

    global SERVER, USER, PASSWORD
    SERVER = config.get(configparser.UNNAMED_SECTION, 'server', fallback=SERVER)
    USER = config.get(configparser.UNNAMED_SECTION, 'user', fallback=USER)
    PASSWORD = config.get(configparser.UNNAMED_SECTION, 'password', fallback=PASSWORD)

def load_args(args):
    global SERVER, USER, PASSWORD
    SERVER = args.server or SERVER
    USER = args.user or USER
    PASSWORD = args.password or PASSWORD

def get_client():
    global SERVER, USER, PASSWORD
    client = caldav.DAVClient(
        url=SERVER,
        username=USER,
        password=PASSWORD
    )
    return client

def encode_tasks(tasks):
    encoded_tasks = []
    for task in tasks:
        if isinstance(task['ical'], Todo):
            task['ical'] = task['ical'].to_ical().decode('utf-8')
        encoded_tasks.append(task)
    return encoded_tasks

def get_tasks(dav_session: DavSession):
    if not os.path.exists('tasks.json'):
        tasks = dav_session.sync()
        enc_tasks = encode_tasks(tasks)
        with open('tasks.json', 'w') as f:
            json.dump(enc_tasks, f, indent=4)

    else:
        with open('tasks.json', 'r') as f:
            tasks = json.load(f)
            for task in tasks:
                if isinstance(task["ical"], str):
                    task["ical"] = Todo.from_ical(task["ical"].encode('utf-8'))

    return tasks

def main():
    parser = argparse.ArgumentParser(description="Manage tasks with CalDAV.")
    parser.add_argument("--server", help="CalDAV server URL")
    parser.add_argument("--user", help="CalDAV username")
    parser.add_argument("--password", help="CalDAV password")
    args = parser.parse_args()


    try:
        load_config()
    except:
        pass

    load_args(args)

    dav_session = DavSession(SERVER, USER, PASSWORD)

    tasks = get_tasks(dav_session)
    run_tui(tasks, dav_session=dav_session)

if __name__ == "__main__":
    main()
