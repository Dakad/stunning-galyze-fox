import os
import sys
import time
from datetime import timedelta

from PIL import Image


ACCEPTED_EXTS = ['.jpg', '.jpeg', '.png'] + ['.!bt']

verbose = False

nb_dirs_corrupt = 0
nb_files_corrupted = 0
nb_dirs_valid = 0
nb_dirs_total = 0
start_time = time.monotonic()

args = {}


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs, flush=True)


def run(**argv):

    if argv['corrupt_dir'] != None and not os.path.isdir(argv['corrupt_dir']):
        print("Creating corrupt dir : ", argv['corrupt_dir'], flush=True)
        os.makedirs(argv['corrupt_dir'], exist_ok=True)

    if argv['valid_dir'] != None and not os.path.isdir(argv['valid_dir']):
        print("Creating saving dir : ", argv['valid_dir'], flush=True)
        os.makedirs(argv['valid_dir'], exist_ok=True)

    scan_dir(argv['input_dir'], opts=argv)

    print_summary(argv)


def scan_dir(full_dir_name, dir_name='', opts=None):
    global nb_dirs_corrupt
    global nb_files_corrupted
    global nb_dirs_valid
    global nb_dirs_total

    if opts is None:
        opts = {}

    try:
        is_dir_corrupted = False
        corrupted_files = []
        with os.scandir(full_dir_name) as it:
            for entry in sorted(it, key=lambda e: e.name):
                entry_full_path = os.path.join(full_dir_name, entry.name)
                if entry.is_dir():
                    nb_dirs_total += 1

                    parent_dir_name = os.path.join(dir_name, entry.name)

                    scan_dir(entry_full_path, parent_dir_name, opts)
                else:
                    if entry.is_file():
                        _, file_extension = os.path.splitext(entry.name)
                        if file_extension.lower() in ACCEPTED_EXTS:
                            file_size = entry.stat().st_size
                            if file_size <= 1024:  # 1 Kb
                                corrupted_files.append(entry.name)
                            else:
                                # print("Checking .. ", dir_name, entry.name)
                                if check_corrupt_image(entry_full_path, entry.name):
                                    if not is_dir_corrupted:
                                        is_dir_corrupted = True
                                        nb_dirs_corrupt += 1
                                    corrupted_files.append(entry.name)

        if len(corrupted_files):
            nb_files_corrupted += len(corrupted_files)

            if opts.get('verbose'):
                print_err('Bad directory: ', dir_name)
                print_err(*corrupted_files, sep='\t')
                print_err("")

            if opts.get('corrupt_dir'):
                for file_name in corrupted_files:
                    old_path = os.path.join(full_dir_name, file_name)
                    new_path = os.path.join(
                        opts.get('corrupt_dir'), dir_name, file_name)
                    os.renames(old_path, new_path)
        else:
            if dir_name != (None or ''):
                nb_dirs_valid += 1
                if opts.get('verbose'):
                    print('Valid dir : ', dir_name)

                if opts.get('valid_dir'):
                    new_dir = os.path.join(opts.get('valid_dir'), dir_name)
                    os.renames(full_dir_name, new_dir)

    except IOError as _:
        print_err('Bad director: ', full_dir_name)


def check_corrupt_image(full_file_name, filename):
    is_corrupt = False
    try:
        with Image.open(full_file_name) as img:
            img.verify()

        with Image.open(full_file_name) as img:
            img.transpose(Image.FLIP_LEFT_RIGHT)

        return False
    except (IOError, Exception) as e:
        # if verbose:
        #     print_err(filename, e)
        return True


def print_summary(opts):
    end_time = time.monotonic()
    elapsed = timedelta(seconds=end_time - start_time)

    summary = """
    ----------------------------------------------------------------------------
    DONE in {} (Elapsed time in seconds : {} sec.)
    ----------------------------------------------------------------------------
    On {} dirs scanned in {}
    -----------------
    {} dir valid
    {} dir corrrupt
    {} files corrupted
    ----------------------------------------------------------------------------
    """.format(elapsed, elapsed.total_seconds(), nb_dirs_total, opts['input_dir'], nb_dirs_valid, nb_dirs_corrupt, nb_files_corrupted)

    print(summary)
    print_err(summary)


def parse_command_line():
    import argparse
    global args

    parser = argparse.ArgumentParser(
        description='Simple script to find corrupt dir containing corrupted images')
    parser.add_argument('input_dir', type=str, help='Input dir for scan')

    parser.add_argument('-v', '--valid-dir', action='store', dest='valid_dir',
                        help='Where to move the valid dirs')

    parser.add_argument('-c', '--corrupt-dir', action='store', dest='corrupt_dir',
                        help='Where to move the corrupt dir')

    parser.add_argument('--verbose', action='store_true',
                        dest='verbose',
                        help='Print each dir and their corrupted images')

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print_err("Usage error : The input dir is required")
        sys.exit(1)

    argv = vars(parse_command_line())
    # print(argv)
    run(**argv)
