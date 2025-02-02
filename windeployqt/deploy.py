import subprocess
from pathlib import Path
import shutil


def msys2_run(cmd):
    s = subprocess.getoutput(f"msys2 -defterm -here -no-start -ucrt64 -c '{cmd}")
    return s


def deploy(file, d):
    print("deploying " + file)
    cygpath = msys2_run(f"cygpath -u {file}")
    s = msys2_run(f"ldd {cygpath}")

    destdir = Path(d).resolve().joinpath("dist")
    destdir.mkdir(exist_ok=True)

    for line in s.split("\n"):
        dep = line.split("=>")[1].split()[0]
        dep = dep.lower()

        if not dep.startswith("/c/windows"):
            print(dep)
            real_dep = msys2_run(f"cygpath -m {dep}")
            shutil.copy(real_dep, destdir)

    shutil.copy(file, destdir)
