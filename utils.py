import os


def get_data_folder(group_to):
    dir_path = os.environ['QIF_PGBACKED'] + '/data/' + group_to;
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_data_path(group_to, plus_name):
    return get_data_folder(group_to) + "/" + plus_name

