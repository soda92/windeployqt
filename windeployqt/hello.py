import os
import glob
from windeployqt.deploy import deploy
import argparse


def main(d):
    cwd = os.getcwd()
    files = glob.glob("**/*.exe", recursive=True, root=cwd)
    files = list(files)

    print("please select:")
    for i, file in enumerate(files):
        print(f"[{i}] {file}")
    ranges = ", ".join([i for i in range(len(files))])
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

    deploy(files[selected])


if __name__ == "__main__":
    main()
