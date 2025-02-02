import subprocess
from pathlib import Path
import shutil
import glob
import os


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


def copy_build_file(src, dst, use_symlink=False):
    if use_symlink:
        skip_create = False
        import subprocess

        if src.is_file():
            dst = dst.joinpath(Path(src).name)
            if dst.exists():
                if dst.is_symlink():
                    if os.readlink(dst).endswith(str(src)):
                        skip_create = True
                    else:
                        dst.unlink()
                elif dst.is_dir():
                    shutil.rmtree(dst)
                elif dst.is_file():
                    dst.unlink()
        elif src.is_dir():
            if dst.exists():
                if dst.is_symlink():
                    if os.readlink(dst).endswith(str(src)):
                        skip_create = True
                    else:
                        dst.unlink()
                elif dst.is_dir():
                    shutil.rmtree(dst)

                else:
                    dst.unlink()

        cmd = f"New-Item -ItemType SymbolicLink -Path {dst} -Target {src}"
        print(cmd)
        if not skip_create:
            subprocess.run(["pwsh", "-c", cmd], check=True)
    else:
        shutil.copytree(src, dst, dirs_exist_ok=True)


def deploy_if_qml(file, destdir, use_symlink):
    qml_dirs = list(
        glob.glob("**/qmldir", recursive=True, root_dir=str(Path(file).parent))
    )

    if len(qml_dirs) > 0:
        destdir.joinpath("QtQuick").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            get_real_dep("/ucrt64/share/qt6/qml/QtQuick"),
            destdir.joinpath("QtQuick"),
            dirs_exist_ok=True,
        )
        dep2 = str(destdir.joinpath("QtQuick/qtquick2plugin.dll")).replace("\\", "/")
        copy_deps(dep2, destdir)

        for qml_dir in qml_dirs:
            qml_dir = Path(file).parent.joinpath(qml_dir).resolve().parent
            target = destdir.joinpath(qml_dir.name)
            target.mkdir(exist_ok=True, parents=True)
            copy_build_file(qml_dir, target, use_symlink)


def copy_deps(file: Path, destdir):
    file_str = str(file).replace("\\", "/")
    cygpath = msys2_run(f"cygpath -u {file_str}")
    s = msys2_run(f"ldd {cygpath}")

    for line in s.split("\n"):
        dep = ""
        try:
            dep = line.split("=>")[1].split()[0]
        except IndexError:
            print("error: ", s)
            breakpoint()
            return
        dep = dep.lower()

        if not dep.startswith("/c/windows"):
            # print(dep)
            real_dep = get_real_dep(dep)
            print(real_dep)
            shutil.copy(real_dep, destdir)


def deploy(file, d, use_symlink):
    destdir = Path(d).resolve().joinpath("dist")
    if destdir.exists():
        if not destdir.is_dir():
            destdir.unlink()
            import os

            os.mkdir(destdir)
    if not destdir.exists():
        import os

        os.mkdir(destdir)
    destdir.mkdir(exist_ok=True)
    print("deploying " + str(file))

    copy_deps(file, destdir)

    shutil.copytree(
        get_real_dep("/ucrt64/share/qt6/plugins"), destdir, dirs_exist_ok=True
    )

    copy_build_file(file, destdir, use_symlink)
    deploy_if_qml(file, destdir, use_symlink)
