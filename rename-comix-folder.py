import os
import sys


def run(comic_dir_path, saving_dir_path):
    # TODO Check if the comic and saving dir exists

    # TODO Create the saving dir if not exists

    # TODO Scan the comic dir
    pass


if __name__ == "__main__":
    message = """
        This script will rename the comic folders with  the correct format.
        Renamed on a range of number starting by 001, 002, ....
        (depending of the folder name).
        If the folder is part of a serie, the serie number is added to the new filename
        Syntax : python {0} <comic_directory> <saving_directory>
            where <comic_directory> is the comic directory
                  <saving_directory> where to save the renamed files
                    Will be created if not exist.
        Examples : 
            python {0} ../Comics/  ~/Comics/Organized/
    """.format(sys.argv[0])

    if len(sys.argv) != 3:
        print(message)
    else:
        run(*sys.argv[1:])
