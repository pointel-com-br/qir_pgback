import datetime as dt
import os
import sys

import utils


class Restore:
    origin_backup_week = "(now::week)"
    target_restore_host = "localhost"
    data_group_to = "periodically"

    def __init__(self,
                 target_restore_host: str = "",
                 origin_backup_week: str = "",
                 data_group_to: str = ""):
        if target_restore_host:
            self.target_restore_host = target_restore_host
        if origin_backup_week:
            self.origin_backup_week = origin_backup_week
        if data_group_to:
            self.data_group_to = data_group_to

    def get_target_week(self) -> str:
        if self.origin_backup_week == "(now::week)":
            return str(dt.datetime.today().weekday())
        else:
            return self.origin_backup_week


def restore_globals(restore: Restore):
    globals_name = utils.get_data_path(
        restore.data_group_to,
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
    origin_path = utils.get_data_folder(restore.data_group_to)
    for inside_path in os.listdir(origin_path):
        if inside_path.startswith("db-") and inside_path.endswith(
                "-" + restore.get_target_week() + ".bkp"):
            restore_database(restore, os.path.join(origin_path, inside_path))
    print("Successfully finish to restore the globals and all databases.")


if __name__ == "__main__":
    print("Restore Globals and Databases")
    host = os.getenv("QIR_PGBACK_HOST", "")
    if not host :
        host = input("Host: ")
    week = os.getenv("QIR_PGBACK_WEEK", "")
    if not week:
        week = input("Week: ")
    group = os.getenv("QIR_PGBACK_GROUP", "")
    if not group:
        group = input("Group: ")
    restore = Restore(host, week, group)
    confirm = input(
        "Do you wanna restore the globals and all databases?\n" +
        "  From data: '" + restore.data_group_to + "'\n" +
        "  And of week: '" + restore.get_target_week() + "'\n" +
        "  And to host: '" + restore.target_restore_host + "' ? (y/N) : ")
    if confirm != "y":
        sys.exit(0)
    restore_globals_and_databases(restore)
