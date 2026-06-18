#!/usr/bin/env python3

# by: Kwabena W. Agyeman - kwagyeman@openmv.io

# Quickly builds an OpenMV IDE installer with a tiny fake payload (one file)
# so archivegen + binarycreator finish in seconds. The installer is assembled
# from the real dist/installer/ifw config + package meta, so every wizard page
# (intro, install folder, ready, finished, custom widgets) renders exactly as
# it does in a shipping build -- ideal for eyeballing layout/style/spacing
# without doing a full IDE compile.
#
# Usage:  python test_installer.py
# Output: build/openmv-ide-uitest-<version>(.exe) -- run it to inspect the UI.

import os, sys, shutil, subprocess

import make  # reuse find_ifdir() / get_ideversion() so paths match a real build

def run(cmd, cwd):
    print("> " + cmd)
    if subprocess.call(cmd, cwd=cwd, shell=True):
        sys.exit("Failed: " + cmd)

def main():
    folder = os.path.dirname(os.path.abspath(__file__))

    ifdir = make.find_ifdir()
    if not ifdir:
        sys.exit("QtInstallerFramework not found (looked where make.py looks).")

    version = make.get_ideversion(folder) or "0.0.0"
    exe = ".exe" if sys.platform.startswith("win") else ""

    builddir = os.path.join(folder, "build")
    os.makedirs(builddir, exist_ok=True)

    # Minimal fake install tree -- one placeholder plus the license so the
    # payload archive is tiny and the build is near-instant.
    testinstall = os.path.join(builddir, "test_install")
    if os.path.exists(testinstall):
        shutil.rmtree(testinstall)
    os.makedirs(testinstall)
    with open(os.path.join(testinstall, "PLACEHOLDER.txt"), "w") as f:
        f.write("OpenMV IDE installer UI test build -- not a real install.\n")
    shutil.copy(os.path.join(folder, "qt-creator", "LICENSE.GPL3-EXCEPT"),
                os.path.join(testinstall, "LICENSE.GPL3-EXCEPT.txt"))

    name = "openmv-ide-uitest-" + version
    archive = name + "-installer-archive.zip"

    archivegen = os.path.join(ifdir, "bin", "archivegen" + exe)
    packageifw = os.path.join(folder, "qt-creator", "scripts", "packageIfw.py")

    # Pack the fake tree, then assemble the installer the same way make.py does.
    run('"%s" -f zip "../%s" PLACEHOLDER.txt LICENSE.GPL3-EXCEPT.txt'
        % (archivegen, archive), cwd=testinstall)
    run('"%s" -u "%s" -i "%s" -v %s -a %s %s'
        % (sys.executable, packageifw, ifdir, version, archive, name), cwd=builddir)

    out = os.path.join(builddir, name + exe)
    print("\nDone. Run the installer to inspect the wizard pages:\n  " + out)

if __name__ == "__main__":
    main()
