import datetime as dt
import os
import sys

import utils


class Restore:
    origin_data_group = "periodically"
    origin_backup_week = "(now::week)"
    target_restore_host = "localhost"

    def __init__(self,
                 origin_data_group: str = "",
                 origin_backup_week: str = "",
                 target_restore_host: str = ""):
        if origin_data_group:
            self.origin_data_group = origin_data_group
        if origin_backup_week:
            self.origin_backup_week = origin_backup_week
        if target_restore_host:
            self.target_restore_host = target_restore_host

    def get_target_week(self) -> str:
        if self.origin_backup_week == "(now::week)":
            return str(dt.datetime.today().weekday())
        else:
            return self.origin_backup_week


def restore_globals(restore: Restore):
    globals_name = utils.get_data_path(
        restore.origin_data_group,
        "globals-" + restore.get_target_week() + ".bkp")
    if os.system("psql -h " + restore.target_restore_host +
                 " -U postgres -f " + globals_name) == 0:
        print("Successfully restore globals.")
    else:
        print("Fail on restore globals.")
        sys.exit(-1)


def restore_database(restore: Restore, path_name):
    print("Restoring path: " + path_name + "...")
    file_name = os.path.basename(path_name)
    db_name = file_name[3:len(file_name)-6]
    print("Restoring database: " + db_name)
    os.system('psql -h ' + restore.target_restore_host +
              ' -U postgres -c "DROP DATABASE ' + db_name + '"')
    if os.system('psql -h ' + restore.target_restore_host +
                 ' -U postgres -c "CREATE DATABASE ' + db_name + '"') != 0:
        print("Fail on create database " + db_name)
        sys.exit(-1)
    if os.system("pg_restore -h " + restore.target_restore_host +
                 " -U postgres -d " + db_name + " --format tar -v " + path_name) != 0:
        print("Fail on restore database " + db_name)
        sys.exit(-1)


def restore_globals_and_databases(restore: Restore):
    restore_globals(restore)
    origin_path = utils.get_data_folder(restore.origin_data_group)
    for inside_path in os.listdir(origin_path):
        if inside_path.startswith("db-") and inside_path.endswith(
                "-" + restore.get_target_week() + ".bkp"):
            restore_database(restore, os.path.join(origin_path, inside_path))
    print("Successfully finish to restore the globals and all databases.")


if __name__ == "__main__":
    print("Restore Globals and Databases")
    host = input("Host [localhost] : ")
    week = input("Week [now::week] (Monday == 0 ... Sunday == 6) : ")
    group = input("Group [periodically] (periodically | emergency) : ")
    restore = Restore(group, week, host)
    confirm = input(
        "Do you wanna restore the globals and all databases?\n" +
        "  From group: '" + restore.origin_data_group + "'\n" +
        "  And of week: '" + restore.get_target_week() + "'\n" +
        "  And to host: '" + restore.target_restore_host + "' ? (y/N) : ")
    if confirm != "y":
        sys.exit(0)
    restore_globals_and_databases(restore)
