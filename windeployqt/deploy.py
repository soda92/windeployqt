import subprocess
from pathlib import Path
import shutil
import glob


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


def deploy_if_qml(file, destdir):
    qml_dirs = list(
        glob.glob("**/qmldir", recursive=True, root_dir=str(Path(file).parent))
    )
    if len(qml_dirs) > 0:
        shutil.copytree(
            get_real_dep("/ucrt64/share/qt6/qml/QtQuick"),
            destdir.joinpath("QtQuick"),
            dirs_exist_ok=True,
        )
        dep2 = str(destdir.joinpath("QtQuick/qtquick2plugin.dll")).replace("\\", "/")
        copy_deps(dep2, destdir)

        for qml_dir in qml_dirs:
            qml_dir = Path(file).parent.joinpath(qml_dir).resolve().parent
            shutil.copytree(qml_dir, destdir.joinpath(qml_dir.name), dirs_exist_ok=True)


def copy_deps(file, destdir):
    cygpath = msys2_run(f"cygpath -u {file}")
    s = msys2_run(f"ldd {cygpath}")

    for line in s.split("\n"):
        dep = line.split("=>")[1].split()[0]
        dep = dep.lower()

        if not dep.startswith("/c/windows"):
            # print(dep)
            real_dep = get_real_dep(dep)
            print(real_dep)
            shutil.copy(real_dep, destdir)


def deploy(file, d):
    destdir = Path(d).resolve().joinpath("dist")
    destdir.mkdir(exist_ok=True)
    print("deploying " + file)

    copy_deps(file, destdir)

    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/plugins"), destdir, dirs_exist_ok=True
    )

    shutil.copy(file, destdir)
    deploy_if_qml(file, destdir)
