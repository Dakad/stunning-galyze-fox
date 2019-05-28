import os
import sys


def run(comic_dir_path, saving_dir_path):

    if not os.path.isdir(comic_dir_path):
        print("The provided comic dir '%s' do not exist" %
              comic_dir_path, flush=True)
        sys.exit(1)

    if not os.path.isdir(saving_dir_path):
        print("Creating saving dir : ", saving_dir_path, flush=True)
        os.makedirs(saving_dir_path, exist_ok=True)

    def join_with_comic_dir_func(dir_name):
        return os.path.isdir(os.path.join(comic_dir_path, dir_name))

    dirs = sorted(filter(join_with_comic_dir_func, os.listdir(comic_dir_path)))

    for comic_dir in dirs:
        print(comic_dir)
        # new_comics_names = scan_comic_dir(comic_dir_path)

    # TODO Rename the new list


def scan_comic_dir(comic_dir_path, num_serie=None):
    with os.scandir(comic_dir_path) as comic_dir:
        for entry in sorted(comic_dir, key=lambda e: e.name):
            if entry.is_dir():
                # TODO PArse the dir name to retrieve the num
                scan_comic_dir(comic_dir)


if __name__ == "__main__":
    message = """
This script will rename the comic folders with  the correct format.
Renamed on a range of number starting by 001, 002, ....
(depending of the folder name).

If the folder is part of a serie, the serie number is added to the new filename
    """

    syntax = """
Syntax : python {0} <comic_directory> <saving_directory>
            <comic_directory> is the comic directory
            <saving_directory> where to save the renamed files. Will be created if not exist.
Example : python {0} ../Comics/  ~/Comics/Organized/
    """.format(sys.argv[0])

    if len(sys.argv) != 3:
        print("Bad usage of ", sys.argv[0])
        print(syntax)
    else:
        run(*sys.argv[1:])
