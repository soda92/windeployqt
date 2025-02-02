import os
import glob
from windeployqt.deploy import deploy
import argparse
from pathlib import Path
import subprocess


def get_all_exe(d):
    files = glob.glob("**/*.exe", recursive=True, root_dir=str(d))
    files = list(map(lambda x: str(d.joinpath(x)).replace("\\", "/"), files))
    return files


def choose(files):
    print("please select:")
    for i, file in enumerate(files):
        print(f"[{i}] {file}")
    ranges = ", ".join([str(i) for i in range(len(files))])
    prompt = f"[{ranges}]: "
    selected = input(prompt)

    def is_valid(x):
        y = 0
        try:
            y = int(x)
        except Exception as _:
            return False
        if 0 <= y < len(files):
            return True
        return False

    while not is_valid(selected):
        selected = input(prompt)
    selected = int(selected)

    return files[selected]


def get_valid_files(files, d):
    import re

    ret = []
    for f in files:
        if re.match(r".*/CMakeFiles/[0-9\.]+/.*", f, re.IGNORECASE):
            continue
        if f.startswith(str(d.joinpath("dist")).replace("\\", "/")):
            continue
        ret.append(f)
    return ret


def main2():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", "-d", type=str, default=os.getcwd(), help="project directory"
    )
    parser.add_argument(
        "--inplace",
        "-I",
        action="store_true",
        default=False,
        help="deploy inplace (suit for debug-and-build)",
    )

    parser.add_argument(
        "--symlink",
        "-s",
        action="store_true",
        default=False,
        help="create desktop shortcut",
    )

    parser.add_argument(
        "--open", "-o", action="store_true", default=False, help="open build dir"
    )

    args = parser.parse_args()
    d = Path(args.dir).resolve()
    inplace = args.inplace

    files = get_all_exe(d)
    files = get_valid_files(files, d)
    file = ""
    if len(files) == 0:
        print("no exe found")
        return
    elif len(files) == 1:
        file = files[0]
    else:
        file = choose(files)

    file = Path(file)
    destdir = None
    if inplace:
        destdir = Path(file).resolve().parent
    else:
        destdir = Path(d).joinpath("dist")
    deploy(file, d, destdir)

    if args.open:
        subprocess.Popen(f"explorer {destdir}")

    if args.symlink:
        from windeployqt.desktop import create_shortcut

        create_shortcut(file, file.name)


if __name__ == "__main__":
    main2()
