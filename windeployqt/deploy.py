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
        s = msys2_run("cygpath -m /ucrt64/bin/bash")
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
            dst = destdir.joinpath(qml_dir.name)
            if qml_dir != dst:
                shutil.copytree(qml_dir, dst, dirs_exist_ok=True)


def copy_deps(file: Path, destdir):
    file_str = str(file).replace("\\", "/")
    cygpath = msys2_run(f"cygpath -u {file_str}")
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


def deploy(file, d, destdir):
    destdir.mkdir(exist_ok=True)
    print("deploying " + str(file))

    copy_deps(file, destdir)

    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/plugins"), destdir, dirs_exist_ok=True
    )

    if not Path(file).parent == Path(destdir):
        shutil.copy(file, destdir)
    deploy_if_qml(file, destdir)
