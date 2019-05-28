import os
import sys

from PIL import Image


ACCEPTED_EXTS = ['.jpg', '.jpeg', '.png'] + ['.!bt']

verbose = False


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs, flush=True)


def run(argv):
    input_dir = argv[1]

    scan_dir(input_dir)

    print('Done')


def scan_dir(full_dir_name, dir_name=''):
    try:
        is_dir_corrupted = False
        corrupted_files = []
        with os.scandir(full_dir_name) as it:
            for entry in sorted(it, key=lambda e: e.name):
                entry_full_path = os.path.join(full_dir_name, entry.name)
                if entry.is_dir():

                    scan_dir(entry_full_path, entry.name+'/'+dir_name)
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
                                    corrupted_files.append(entry.name)

        if len(corrupted_files):
            print_err('Bad directory: ', dir_name)
            print_err(*corrupted_files, sep='\t')
            print_err("")
        else:
            if dir_name != (None or ''):
                print('Valid dir : ', dir_name)

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
        if verbose:
            print_err(filename, e)
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_err("Usage error : The input dir is required")
        sys.exit(1)

    run(sys.argv)
    verbose = len(sys.argv) == 3
