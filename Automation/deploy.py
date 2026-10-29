import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT.parent / "Configurations"
BACKUP_DIR = ROOT / "backups"
SECRET_LINE = re.compile(r"^(pre-shared-key)\b.*$")


def normalize(line):
    return SECRET_LINE.sub(r"\1", line.strip())


def parse_entries(text):
    entries = []
    stack = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("!"):
            continue
        level = len(raw) - len(raw.lstrip(" "))
        while stack and stack[-1][0] >= level:
            stack.pop()
        path = tuple(item[1] for item in stack) + (normalize(stripped),)
        entries.append(path)
        stack.append((level, normalize(stripped)))
    return entries


def is_present(path, running):
    if path[-1] == "no shutdown":
        parent = path[:-1]
        return parent in running and parent + ("shutdown",) not in running
    return path in running


def find_missing(wanted, running_text):
    running = set(parse_entries(running_text))
    return [path for path in wanted if not is_present(path, running)]


def build_commands(missing):
    commands = []
    last_parents = ()
    for path in missing:
        parents = path[:-1]
        if parents != last_parents:
            commands.extend(parents)
            last_parents = parents
        commands.append(path[-1])
    return commands


def load_inventory(path):
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    defaults = data.get("defaults", {})
    devices = []
    for name, spec in data["devices"].items():
        device = {**defaults, **spec}
        device["name"] = name
        devices.append(device)
    return devices


def select_devices(devices, names, sites):
    chosen = devices
    if names:
        chosen = [device for device in chosen if device["name"] in names]
    if sites:
        chosen = [device for device in chosen if device.get("site") in sites]
    return chosen


def load_wanted(name, parts):
    folder = CONFIG_DIR / name
    files = sorted(folder.glob("*.cfg")) if folder.is_dir() else []
    if parts:
        files = [path for path in files if any(path.name.startswith(part) for part in parts)]
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    return files, parse_entries(text)


def credentials():
    try:
        username = os.environ["TVI_USER"]
        password = os.environ["TVI_PASS"]
    except KeyError as missing:
        sys.exit(f"environment variable {missing.args[0]} is not set")
    return {"username": username, "password": password, "secret": os.environ.get("TVI_ENABLE", password)}


def connect(device, creds):
    from netmiko import ConnectHandler

    params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "port": device["port"],
        "timeout": device["timeout"],
        **creds,
    }
    connection = ConnectHandler(**params)
    connection.enable()
    return connection


def run_device(device, creds, action, parts, save):
    name = device["name"]
    result = {"name": name, "status": "ok", "pending": 0, "remaining": 0, "detail": ""}
    try:
        files, wanted = load_wanted(name, parts)
        if action != "backup" and not files:
            result.update(status="skipped", detail="no config files")
            return result
        connection = connect(device, creds)
        try:
            running = connection.send_command("show running-config")
            if action == "backup":
                BACKUP_DIR.mkdir(exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                target = BACKUP_DIR / f"{name}-{stamp}.cfg"
                target.write_text(running, encoding="utf-8")
                result["detail"] = str(target.name)
                return result
            missing = find_missing(wanted, running)
            result["pending"] = len(missing)
            commands = build_commands(missing)
            result["commands"] = commands
            if action == "apply" and commands:
                connection.send_config_set(commands)
                after = connection.send_command("show running-config")
                remaining = find_missing(wanted, after)
                result["remaining"] = len(remaining)
                if remaining:
                    result["status"] = "incomplete"
                    result["detail"] = "; ".join(" > ".join(path) for path in remaining[:5])
                elif save:
                    connection.save_config()
                    result["detail"] = "saved"
        finally:
            connection.disconnect()
    except Exception as error:
        result.update(status="failed", detail=f"{type(error).__name__}: {error}")
    return result


def print_report(results, action):
    for result in results:
        if action == "plan" and result.get("commands"):
            print(f"--- {result['name']}")
            print("\n".join(result["commands"]))
    width = max(len(result["name"]) for result in results)
    print()
    for result in results:
        print(f"{result['name']:<{width}}  {result['status']:<10} pending={result['pending']:<4} remaining={result['remaining']:<4} {result['detail']}")


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="deploy.py")
    parser.add_argument("action", choices=["backup", "plan", "apply"])
    parser.add_argument("--inventory", default=str(ROOT / "inventory.yml"))
    parser.add_argument("--device", action="append", default=[])
    parser.add_argument("--site", action="append", default=[])
    parser.add_argument("--part", action="append", default=[])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--save", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    devices = select_devices(load_inventory(args.inventory), args.device, args.site)
    if not devices:
        sys.exit("no device matches the filters")
    creds = credentials()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_device, device, creds, args.action, args.part, args.save) for device in devices]
        results = [future.result() for future in futures]
    print_report(results, args.action)
    return 0 if all(result["status"] in ("ok", "skipped") for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
