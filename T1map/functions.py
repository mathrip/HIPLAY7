import os


def is_directory(directory_path):
    if os.path.exists(directory_path):
        exist = 1
        print('INFO : Directory {} already exists'.format(directory_path))
    else:
        exist = 0
        os.makedirs(directory_path)
    return exist


def is_file(file_path):
    if os.path.exists(file_path):
        exist = 1
        print('INFO : File {} already exist. Use existing file for the ratio'.format(file_path))
    else:
        exist = 0
        print('WARNINGFile {} does not exist'.format(file_path))
    return exist


