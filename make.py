#!/usr/bin/env python3

# by: Kwabena W. Agyeman - kwagyeman@openmv.io

import argparse, glob, multiprocessing, os, re, shutil, stat, sys

def match(d0, d1):
    x = [x for x in os.listdir(d0) if re.match(d1, x)]
    return os.path.join(d0, x[0]) if x else None

def match_all(d0, d1):
    return [os.path.join(d0, x) for x in os.listdir(d0) if re.match(d1, x)]

def search(d0, d1):
    x = [x for x in os.listdir(d0) if re.search(d1, x)]
    return os.path.join(d0, x[0]) if x else None

def search_all(d0, d1):
    return [os.path.join(d0, x) for x in os.listdir(d0) if re.search(d1, x)]

def find_qtdir(rpi):
    if rpi:
        os.environ["QTDIR"] = rpi
        path = os.path.join(rpi, "bin") + ':'
        os.environ["PATH"] = path + os.environ["PATH"]
        return rpi
    elif sys.platform.startswith('win'):
        qtdir = match(os.sep, r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d+\.\d+(\.\d+)?")
            if qtdir:
                qtdir = search(qtdir, r"mingw")
                if qtdir:
                    os.environ["QTDIR"] = qtdir
                    path = ';' + os.path.join(qtdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtdir
        qtdir = match(os.path.expanduser('~'), r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d+\.\d+(\.\d+)?")
            if qtdir:
                qtdir = search(qtdir, r"mingw")
                if qtdir:
                    os.environ["QTDIR"] = qtdir
                    path = ';' + os.path.join(qtdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtdir
    elif sys.platform.startswith('darwin'):
        qtdir = match(os.path.expanduser('~'), r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d+\.\d+(\.\d+)?")
            if qtdir:
                qtdir = match(qtdir, r"macos")
                if qtdir:
                    os.environ["QTDIR"] = qtdir
                    path = ':' + os.path.join(qtdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtdir
    elif sys.platform.startswith('linux'):
        qtdir = match(os.path.expanduser('~'), r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d+\.\d+(\.\d+)?")
            if qtdir:
                qtdir = search(qtdir, r"gcc")
                if qtdir:
                    os.environ["QTDIR"] = qtdir
                    path = ':' + os.path.join(qtdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtdir
    return None

def find_mingwdir():
    if sys.platform.startswith('win'):
        mingwdir = match(os.sep, r"Qt")
        if mingwdir:
            mingwdir = match(mingwdir, r"Tools")
            if mingwdir:
                mingwdir = search(mingwdir, r"mingw")
                if mingwdir:
                    os.environ["MINGWDIR"] = mingwdir
                    path = ';' + os.path.join(mingwdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return mingwdir
        mingwdir = match(os.path.expanduser('~'), r"Qt")
        if mingwdir:
            mingwdir = match(mingwdir, r"Tools")
            if mingwdir:
                mingwdir = search(mingwdir, r"mingw")
                if mingwdir:
                    os.environ["MINGWDIR"] = mingwdir
                    path = ';' + os.path.join(mingwdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return mingwdir
    return None

def find_cmakedir():
    if sys.platform.startswith('win'):
        cmakedir = match(os.sep, r"Qt")
        if cmakedir:
            cmakedir = match(cmakedir, r"Tools")
            if cmakedir:
                cmakedir = search(cmakedir, r"CMake")
                if cmakedir:
                    os.environ["CMAKEDIR"] = cmakedir
                    path = ';' + os.path.join(cmakedir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return cmakedir
        cmakedir = match(os.path.expanduser('~'), r"Qt")
        if cmakedir:
            cmakedir = match(cmakedir, r"Tools")
            if cmakedir:
                cmakedir = search(cmakedir, r"CMake")
                if cmakedir:
                    os.environ["CMAKEDIR"] = cmakedir
                    path = ';' + os.path.join(cmakedir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return cmakedir
    elif sys.platform.startswith('darwin'):
        cmakedir = match(os.path.expanduser('~'), r"Qt")
        if cmakedir:
            cmakedir = match(cmakedir, r"Tools")
            if cmakedir:
                cmakedir = match(cmakedir, r"CMake")
                if cmakedir:
                    cmakedir = match(cmakedir, r"CMake.app")
                    if cmakedir:
                        cmakedir = match(cmakedir, r"Contents")
                        if cmakedir:
                            os.environ["CMAKEDIR"] = cmakedir
                            path = ':' + os.path.join(cmakedir, "bin")
                            os.environ["PATH"] = os.environ["PATH"] + path
                            return cmakedir
    elif sys.platform.startswith('linux'):
        cmakedir = match(os.path.expanduser('~'), r"Qt")
        if cmakedir:
            cmakedir = match(cmakedir, r"Tools")
            if cmakedir:
                cmakedir = search(cmakedir, r"CMake")
                if cmakedir:
                    os.environ["CMAKEDIR"] = cmakedir
                    path = ':' + os.path.join(cmakedir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return cmakedir
    return None

def find_ninjadir():
    if sys.platform.startswith('win'):
        ninjadir = match(os.sep, r"Qt")
        if ninjadir:
            ninjadir = match(ninjadir, r"Tools")
            if ninjadir:
                ninjadir = match(ninjadir, r"Ninja")
                if ninjadir:
                    os.environ["NINJADIR"] = ninjadir
                    path = ';' + ninjadir
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return ninjadir
        ninjadir = match(os.path.expanduser('~'), r"Qt")
        if ninjadir:
            ninjadir = match(ninjadir, r"Tools")
            if ninjadir:
                ninjadir = match(ninjadir, r"Ninja")
                if ninjadir:
                    os.environ["NINJADIR"] = ninjadir
                    path = ';' + ninjadir
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return ninjadir
    elif sys.platform.startswith('darwin'):
        ninjadir = match(os.path.expanduser('~'), r"Qt")
        if ninjadir:
            ninjadir = match(ninjadir, r"Tools")
            if ninjadir:
                ninjadir = match(ninjadir, r"Ninja")
                if ninjadir:
                    os.environ["NINJADIR"] = ninjadir
                    path = ':' + ninjadir
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return ninjadir
    elif sys.platform.startswith('linux'):
        ninjadir = match(os.path.expanduser('~'), r"Qt")
        if ninjadir:
            ninjadir = match(ninjadir, r"Tools")
            if ninjadir:
                ninjadir = match(ninjadir, r"Ninja")
                if ninjadir:
                    os.environ["NINJADIR"] = ninjadir
                    path = ':' + ninjadir
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return ninjadir
    return None

def find_ifdir():
    if sys.platform.startswith('win'):
        ifdir = match(os.sep, r"Qt")
        if ifdir:
            ifdir = match(ifdir, r"Tools")
            if ifdir:
                ifdir = match(ifdir, r"QtInstallerFramework")
                if ifdir:
                    ifdir = match(ifdir, r"\d+\.\d+(\.\d+)?")
                    if ifdir:
                        os.environ["IFDIR"] = ifdir
                        path = ';' + os.path.join(ifdir, "bin")
                        os.environ["PATH"] = os.environ["PATH"] + path
                        return ifdir
        ifdir = match(os.path.expanduser('~'), r"Qt")
        if ifdir:
            ifdir = match(ifdir, r"Tools")
            if ifdir:
                ifdir = match(ifdir, r"QtInstallerFramework")
                if ifdir:
                    ifdir = match(ifdir, r"\d+\.\d+(\.\d+)?")
                    if ifdir:
                        os.environ["IFDIR"] = ifdir
                        path = ';' + os.path.join(ifdir, "bin")
                        os.environ["PATH"] = os.environ["PATH"] + path
                        return ifdir
    elif sys.platform.startswith('darwin'):
        ifdir = match(os.path.expanduser('~'), r"Qt")
        if ifdir:
            ifdir = search(ifdir, r"QtIFW")
            if ifdir:
                os.environ["IFDIR"] = ifdir
                path = ':' + os.path.join(ifdir, "bin")
                os.environ["PATH"] = os.environ["PATH"] + path
                return ifdir
    elif sys.platform.startswith('linux'):
        ifdir = match(os.path.expanduser('~'), r"Qt")
        if ifdir:
            ifdir = match(ifdir, r"Tools")
            if ifdir:
                ifdir = match(ifdir, r"QtInstallerFramework")
                if ifdir:
                    ifdir = match(ifdir, r"\d+\.\d+(\.\d+)?")
                    if ifdir:
                        os.environ["IFDIR"] = ifdir
                        path = ':' + os.path.join(ifdir, "bin")
                        os.environ["PATH"] = os.environ["PATH"] + path
                        return ifdir
    return None

def find_windowssdkdir():
    if sys.platform.startswith('win'):
        windowssdkdir = match(os.sep, r"Program Files \(x86\)")
        if windowssdkdir:
            windowssdkdir = match(windowssdkdir, r"Windows Kits")
            if windowssdkdir:
                windowssdkdir = match(windowssdkdir, r"10")
                if windowssdkdir:
                    windowssdkdir = match(windowssdkdir, r"bin")
                    if windowssdkdir:
                        for d in match_all(windowssdkdir, r"\d+\.\d+\.\d+\.\d+"):
                            dx64 = match(d, r"x64")
                            if dx64:
                                dx64exe = match(dx64, r"signtool.exe")
                                if dx64exe:
                                    os.environ["WINDOWSSDKDIR"] = dx64
                                    path = ';' + os.path.join(dx64)
                                    os.environ["PATH"] = os.environ["PATH"] + path
                                    return dx64
                            dx86 = match(d, r"x86")
                            if dx86:
                                dx86exe = match(dx86, r"signtool.exe")
                                if dx86exe:
                                    os.environ["WINDOWSSDKDIR"] = dx86
                                    path = ';' + os.path.join(dx86)
                                    os.environ["PATH"] = os.environ["PATH"] + path
                                    return dx86
    return None

def get_ideversion(folder):
    for line in reversed(list(open(os.path.join(folder, "qt-creator/cmake/QtCreatorIDEBranding.cmake")))):
        match = re.search(r'set\(IDE_VERSION\s+"([^"]+)"\)', line)
        if match: return match.group(1)

def make():

    __folder__ = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description =
    "Make Script")

    parser.add_argument("--rpi", nargs = '?',
    help = "Qt 6 Cross-Compile QTDIR for the Raspberry Pi")

    args = parser.parse_args()

    if args.rpi and not sys.platform.startswith('linux'):
        sys.exit("Linux Only")

    ###########################################################################

    cpus = multiprocessing.cpu_count()

    qtdir = find_qtdir(args.rpi)
    mingwdir = find_mingwdir()
    cmakedir = find_cmakedir()
    ninjadir = find_ninjadir()
    ifdir = find_ifdir()
    windowssdk = find_windowssdkdir()

    ideversion = get_ideversion(__folder__)

    builddir = os.path.join(__folder__, "build")
    installdir = os.path.join(builddir, "install")

    if not os.path.exists(builddir):
        os.mkdir(builddir)

    if not os.path.exists(installdir):
        os.mkdir(installdir)

    installer = ""

    if args.rpi:
        with open(os.path.join(installdir, "README.txt"), 'w') as f:
            f.write("Please run setup.sh to install OpenMV IDE dependencies:\n\n")
            f.write("    ./setup.sh\n\n")
            f.write("And then run OpenMV IDE:\n\n")
            f.write("    ./bin/openmvide\n")
        with open(os.path.join(installdir, "setup.sh"), 'w') as f:
            f.write("#! /bin/sh\n\n")
            f.write("DIR=\"$(dirname \"$(readlink -f \"$0\")\")\"\n\n")
            f.write("sudo apt-get update -y\n")
            f.write("sudo apt-get full-upgrade -y\n")
            f.write("sudo apt-get install -y libboost-all-dev libudev-dev libinput-dev libts-dev libmtdev-dev libjpeg-dev libfontconfig1-dev libssl-dev libdbus-1-dev libglib2.0-dev libxkbcommon-dev libegl1-mesa-dev libgbm-dev libgles2-mesa-dev mesa-common-dev libasound2-dev libpulse-dev gstreamer1.0-omx libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev  gstreamer1.0-alsa libvpx-dev libsrtp2-dev libsnappy-dev libnss3-dev \"^libxcb.*\" flex bison libxslt-dev ruby gperf libbz2-dev libcups2-dev libatkmm-1.6-dev libxi6 libxcomposite1 libfreetype6-dev libicu-dev libsqlite3-dev libxslt1-dev libavcodec-dev libavformat-dev libswscale-dev libx11-dev freetds-dev libsqlite3-dev libpq-dev libiodbc2-dev firebird-dev libgst-dev libxext-dev libxcb1 libxcb1-dev libx11-xcb1 libx11-xcb-dev libxcb-keysyms1 libxcb-keysyms1-dev libxcb-image0 libxcb-image0-dev libxcb-shm0 libxcb-shm0-dev libxcb-icccm4 libxcb-icccm4-dev libxcb-sync1 libxcb-sync-dev libxcb-render-util0 libxcb-render-util0-dev libxcb-xfixes0-dev libxrender-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-glx0-dev libxi-dev libdrm-dev libxcb-xinerama0 libxcb-xinerama0-dev libatspi2.0-dev libxcursor-dev libxcomposite-dev libxdamage-dev libxss-dev libxtst-dev libpci-dev libcap-dev libxrandr-dev libdirectfb-dev libaudio-dev libxkbcommon-x11-dev\n\n")
            f.write("sudo apt-get install -y libpng16-16 libusb-1.0 python3 python3-pip\n")
            f.write("sudo pip install pyusb\n\n")
            f.write("sudo cp $( dirname \"$0\" )/share/qtcreator/pydfu/*.rules /etc/udev/rules.d/\n")
            f.write("sudo udevadm trigger\n")
            f.write("sudo udevadm control --reload-rules\n\n")
            f.write("while true; do\n")
            f.write("    read -r -p \"\nInstall Desktop Shortcut? [y/n] \" _response\n")
            f.write("    case \"$_response\" in\n")
            f.write("        [Yy][Ee][Ss]|[Yy])\n")
            f.write("            cat > /home/$USER/Desktop/openmvide.desktop << EOM\n")
            f.write("[Desktop Entry]\n")
            f.write("Type=Application\n")
            f.write("Exec=$DIR/bin/openmvide\n")
            f.write("Path=$DIR\n")
            f.write("Name=OpenMV IDE\n")
            f.write("GenericName=The IDE of choice for OpenMV Cam Development.\n")
            f.write("X-KDE-StartupNotify=true\n")
            f.write("Icon=$DIR/share/icons/hicolor/512x512/apps/OpenMV-openmvide.png\n")
            f.write("StartupWMClass=openmvide\n")
            f.write("Terminal=false\n")
            f.write("Categories=Development;IDE;OpenMV;\n")
            f.write("MimeType=text/x-python;\n")
            f.write("EOM\n")
            f.write("            echo \"You must logout and login again for the desktop shortcut to work.\"\n")
            f.write("            exit 0\n")
            f.write("            ;;\n")
            f.write("        [Nn][Oo]|[Nn])\n")
            f.write("            exit 0\n")
            f.write("            ;;\n")
            f.write("        *)\n")
            f.write("            ;;\n")
            f.write("    esac\n")
            f.write("done\n")
        os.chmod(os.path.join(installdir, "setup.sh"),
            os.stat(os.path.join(installdir, "setup.sh")).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        installer_name = "openmv-ide-linux-arm-" + ideversion + ".tar.gz"
        if os.system("cd " + builddir +
        " && cmake ../qt-creator" +
            " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
            " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
            " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
            " \"-DCMAKE_C_COMPILER:FILEPATH=/usr/bin/aarch64-linux-gnu-gcc-9\"" +
            " \"-DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/aarch64-linux-gnu-g++-9\"" +
            " \"-DCMAKE_CXX_FLAGS_INIT:STRING=\"" +
            " \"-DCMAKE_TOOLCHAIN_FILE:UNINITIALIZED=" + os.path.join(qtdir, "lib/cmake/Qt6/qt.toolchain.cmake") + "\"" +
        " && cmake --build . --target all" +
        " && cmake --install . --prefix install" +
        " && cmake --install . --prefix install --component Dependencies" +
        " && cp -r install openmv-ide" +  
        " && tar -czvf " + installer_name + " openmv-ide"):
            sys.exit("Make Failed...")

    elif sys.platform.startswith('win'):
        installer_name = "openmv-ide-windows-" + ideversion
        installer_archive_name = installer_name + "-installer-archive.7z"
        if os.system("cd " + builddir +
        " && cmake ../qt-creator" +
            " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
            " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
            " \"-DQT_QMAKE_EXECUTABLE:FILEPATH=" + os.path.join(qtdir, "bin/qmake.exe") + "\"" +
            " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
            " \"-DCMAKE_C_COMPILER:FILEPATH=" + os.path.join(mingwdir, "bin/gcc.exe") + "\"" +
            " \"-DCMAKE_CXX_COMPILER:FILEPATH=" + os.path.join(mingwdir, "bin/g++.exe") + "\"" +
            " \"-DCMAKE_CXX_FLAGS_INIT:STRING=\""
        " && cmake --build . --target all" +
        " && cmake --install . --prefix install" +
        " && cmake --install . --prefix install --component Dependencies" +
        " && python -u ../qt-creator/scripts/sign.py install" +
        " && cd install"
        " && archivegen ../" + installer_archive_name + " bin lib share" +
        " && cd .."
        " && python3 -u ../qt-creator/scripts/packageIfw.py -i " + ifdir +
            " -v " + ideversion +
            " -a " + installer_archive_name + " " + installer_name +
        " && python3 -u ../qt-creator/scripts/sign.py " + installer_name + ".exe"):
            sys.exit("Make Failed...")

    elif sys.platform.startswith('darwin'):
        installer_name = "openmv-ide-mac-" + ideversion + ".dmg"
        if os.system("cd " + builddir +
        " && cmake ../qt-creator" +
            " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
            " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
            " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
            " \"-DCMAKE_CXX_FLAGS_INIT:STRING=\""
        " && cmake --build . --target all" +
        " && cmake --install . --prefix . --component Dependencies" +
        " && python3 -u ../qt-creator/scripts/sign.py \"OpenMV IDE.app\" || true" +
        " && codesign --deep -s Application --force --options=runtime --timestamp \"OpenMV IDE.app\" || true" +
        " && ditto -c -k -rsrc --sequesterRsrc --keepParent OpenMV\\ IDE.app OpenMV\\ IDE.zip" +
        " && xcrun notarytool submit OpenMV\\ IDE.zip --keychain-profile \"AC_PASSWORD\" --wait || true" +
        " && xcrun stapler staple OpenMV\\ IDE.app || true" +
        " && ../qt-creator/scripts/makedmg.sh OpenMV\\ IDE.app " + installer_name +
        " && xcrun notarytool submit " + installer_name + " --keychain-profile \"AC_PASSWORD\" --wait || true" +
        " && xcrun stapler staple " + installer_name + " || true"):
            sys.exit("Make Failed...")

    elif sys.platform.startswith('linux'):
        installer_name = "openmv-ide-linux-x86_64-" + ideversion
        installer_archive_name = installer_name + "-installer-archive.7z"
        if os.system("cd " + builddir +
        " && cmake ../qt-creator" +
            " -Wno-dev" +
            " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
            " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
            " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
            " \"-DCMAKE_CXX_FLAGS_INIT:STRING=\"" +
        " && cmake --build . --target all" +
        " && cmake --install . --prefix install" +
        " && cmake --install . --prefix install --component Dependencies" +
        " && cd install"
        " && archivegen ../" + installer_archive_name + " bin lib share" +
        " && cd .."
        " && python3 -u ../qt-creator/scripts/packageIfw.py -i " + ifdir +
            " -v " + ideversion + " -a " + installer_archive_name +
            " " + installer_name):
            sys.exit("Make Failed...")

    else:
        sys.exit("Unknown Platform")

if __name__ == "__main__":
    make()
