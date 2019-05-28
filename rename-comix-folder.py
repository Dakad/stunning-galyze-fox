import os
import sys

import re


regex_flags = re.MULTILINE | re.IGNORECASE
regex = r"(?P<title>.+)(?:\s|#)(?P<num_serie>[0-9]{1,2}$)"

pattern = re.compile(regex, regex_flags)


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
    comics = {}
    for comic_dir in dirs:
        comic_name, num_serie = parse_comic_name(comic_dir)

        # Little eception for an custom folder victim of I/O Error
        if(num_serie != None and num_serie == 99):
            continue

        # Retrieve the comic
        file_names = comics.get(comic_name, [])

        # Rename this comic files
        dir_path = os.path.join(comic_dir_path, comic_dir)

        new_comics_names = process_comic_dir(dir_path, num_serie)
        # print(comics, file_names, new_comics_names)

        print("Parsed comic : title=%s num_serie=%d  #filenames=%d" %
              (comic_name, num_serie, len(new_comics_names)))
        # Add the renamed comic filenames
        comics[comic_name] = file_names + new_comics_names

    # Now, begin the renaming of the comic old filename
    for comic in comics.items():
        comic_new_dir_name, comic_new_names = comic
        for (comic_old_path, new_name) in comic_new_names:
            # Create the path for the new comic files
            comic_new_path = os.path.join(
                saving_dir_path, comic_new_dir_name, new_name)
            # print(comic_old_path, ' ~-_-~> ', comic_new_path)
            os.renames(comic_old_path, comic_new_path)


def parse_comic_name(comic_name):
    """Retrieve the comic nam and the serie number

    Arguments:
        comic_name {String} -- The comic name

    Returns:

        [String] -- Comic title with the author

        [Number] -- Comic serie number
    """

    match = pattern.match(comic_name)
    if match:
        group = match.groupdict()
        return (group['title'], int(group['num_serie']))
    else:
        return (comic_name, None)


def process_comic_dir(comic_dir_path, num_serie=None):
    """Scan and rename the comic file

    Arguments:
        comic_dir_path {[type]} -- [description]

    Keyword Arguments:
        num_serie {[type]} -- [description] (default: {None})
    """
    new_comic_names = []
    with os.scandir(comic_dir_path) as comic_dir:
        for i, entry in enumerate(sorted(comic_dir, key=lambda e: e.name)):
            if not entry.is_file():
                return

            ext = os.path.splitext(entry.name)[1]
            new_name = '{:0>3}'.format(i+1) + ext
            if num_serie != None:
                new_name = '{}_'.format(num_serie) + new_name
            names = (entry.path, new_name)
            new_comic_names.append(names)

    return new_comic_names


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
