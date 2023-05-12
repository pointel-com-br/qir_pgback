import os


def get_data_folder(group_to):
    dir_path = os.path.join(os.environ['QIR_PGBACK_DATA'], 'data', group_to)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_data_path(group_to, plus_name):
    return os.path.join(get_data_folder(group_to), plus_name)
