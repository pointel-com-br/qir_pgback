import http.client as httplib
import threading
import time
from datetime import datetime

import backup

backup_of_host = "pointel.pointto.us"


def has_internet() -> bool:
    link = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        link.request("HEAD", "/")
        link.close()
        return True
    except:
        link.close()
        return False


def backup_periodically():
    backup.backup_globals_and_databases(backup.Backup(
        target_backup_host=backup_of_host,
        data_group_to="periodically"))


def backup_emergency():
    backup.backup_globals_and_databases(backup.Backup(
        target_backup_host=backup_of_host,
        data_group_to="emergency"))


if __name__ == "__main__":
    minutes_passed = 0
    while True:
        now_str = datetime.now().strftime("%Y-%m-%d %H-%M")
        if minutes_passed > 60:
            minutes_passed = 0
            print(now_str +
                  " - Have passed one hour so we must to do the periodically backup.")
            threading.Thread(target=backup_periodically).start()
        if has_internet():
            print(now_str +
                  " - We have internet so we don't need to do the emergency backup.")
        else:
            print(now_str +
                  " - We don't have internet so we need to do the emergency backup.")
            backup_emergency()
            time.sleep(120)
            minutes_passed += 2
        time.sleep(60)
        minutes_passed += 1
