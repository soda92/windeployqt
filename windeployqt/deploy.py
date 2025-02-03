import subprocess
from pathlib import Path
import shutil
import glob
import functools


def str_path(p: Path):
    return str(p).replace("\\", "/")


def msys2_run(cmd):
    s = subprocess.getoutput(f"msys2 -defterm -here -no-start -ucrt64 -c '{cmd}")
    return s


@functools.cache
def get_cyg_prefix() -> Path:
    s = msys2_run("cygpath -m /ucrt64/bin/bash")
    cyg_prefix = s.split("/ucrt64/bin")[0]
    return Path(cyg_prefix)


def get_real_dep(dep: str) -> str:
    cyg_prefix = get_cyg_prefix()
    return str_path(cyg_prefix.joinpath(dep))


def deploy_if_qml(file, destdir):
    qml_dirs = list(glob.glob("*/qmldir", root_dir=str(Path(file).parent)))
    if len(qml_dirs) > 0:
        shutil.copytree(
            get_real_dep("/ucrt64/share/qt6/qml/QtQuick"),
            destdir.joinpath("QtQuick"),
            dirs_exist_ok=True,
        )
        dep2 = str_path(destdir.joinpath("QtQuick/qtquick2plugin.dll"))
        copy_deps(dep2, destdir)

        for qml_dir in qml_dirs:
            qml_dir = Path(file).parent.joinpath(qml_dir).resolve().parent
            dst = destdir.joinpath(qml_dir.name)
            if qml_dir != dst: # inplace
                shutil.copytree(qml_dir, dst, dirs_exist_ok=True)


def copy_deps(file: Path, destdir: Path):
    cygpath = msys2_run(f"cygpath -u {str_path(file)}")
    s = msys2_run(f"ldd {cygpath}")

    for line in s.split("\n"):
        dep = ""
        try:
            dep = line.split("=>")[1].split()[0]
        except IndexError as e:
            print(e)
            print(s)
            return
        dep = dep.lower()

        if not dep.startswith("/c/"):
            # print(dep)
            real_dep = get_real_dep(dep)
            print(real_dep)
            shutil.copy(real_dep, destdir)


def deploy(file: Path, project_dir: Path, destdir: Path):
    print("deploying " + str(file))

    copy_deps(file, destdir)

    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/plugins"), destdir, dirs_exist_ok=True
    )

    if not file.parent == destdir:  # no need to copy (error: same file)
        shutil.copy(file, destdir)
    deploy_if_qml(file, destdir)
