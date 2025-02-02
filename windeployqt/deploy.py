import subprocess
from pathlib import Path
import shutil


def msys2_run(cmd):
    s = subprocess.getoutput(f"msys2 -defterm -here -no-start -ucrt64 -c '{cmd}")
    return s


cyg_prefix = ""


def get_real_dep(dep):
    global cyg_prefix
    if cyg_prefix == "":
        s = msys2_run(f"cygpath -m {dep}")
        cyg_prefix = s.split("/ucrt64/bin")[0]
    return cyg_prefix + dep


def copy_plugins(dest: Path):
    f = "/ucrt64/share/qt6/plugins/platforms/qwindows.dll"
    target = dest.joinpath("platforms").joinpath(Path(f).name)
    target.parent.mkdir(exist_ok=True, parents=True)
    f = get_real_dep(f)
    print(f)
    shutil.copy(f, target)


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
            # print(dep)
            real_dep = get_real_dep(dep)
            print(real_dep)
            shutil.copy(real_dep, destdir)

    shutil.copy(file, destdir)

    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/qml/QtQuick"),
        destdir.joinpath("QtQuick"),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/plugins"), destdir, dirs_exist_ok=True
    )
    # copy_plugins(destdir)
