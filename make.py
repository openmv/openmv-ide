#!/usr/bin/env python3

# by: Kwabena W. Agyeman - kwagyeman@openmv.io

import argparse, os, re, shutil, stat, sys

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

def find_tool_in_platform(base_paths, search_sequence, env_var_name, path_separator, bin_subpath="bin"):
    """
    Platform-specific tool finding integrated functions

    Args:
    base_paths: Default paths to search ['/path1', '/path2',...]
    search_sequence: [('Qt', 'match'), ('5.15.2', 'match'), ('mingw', 'search')]
    env_var_name: Name of the environment variable, for example 'QTDIR'
    path_separator: path separator (';' or ':')
    bin_subpath: bin subpath (default: 'bin', Ninja: '')
    """
    for base_path in base_paths:
        current_path = base_path
        
        # Follow the search sequence to navigate the path
        for pattern, search_type in search_sequence:
            if search_type == 'match':
                current_path = match(current_path, pattern)
            elif search_type == 'search':
                current_path = search(current_path, pattern)
            else:  # 'exists' - simple path check
                potential_path = os.path.join(current_path, pattern)
                current_path = potential_path if os.path.exists(potential_path) else None
            
            if current_path is None:
                break
        
        if current_path and os.path.exists(current_path):
            # Setting Environmental Variables
            os.environ[env_var_name] = current_path
            
            # PATH update
            if bin_subpath:
                bin_path = os.path.join(current_path, bin_subpath)
            else:
                bin_path = current_path
            
            if os.path.exists(bin_path):
                current_env_path = os.environ.get("PATH", "")
                if path_separator == ';':  # Windows
                    os.environ["PATH"] = current_env_path + path_separator + bin_path
                else:  # Unix-like
                    os.environ["PATH"] = bin_path + path_separator + current_env_path
            
            return current_path
    
    return None

def find_qtdir(rpi):
    if rpi:
        os.environ["QTDIR"] = rpi
        path = os.path.join(rpi, "bin") + ':'
        os.environ["PATH"] = path + os.environ["PATH"]
        return rpi
    elif sys.platform.startswith('win'):
        base_paths = [os.sep, os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            (r'\d+\.\d+(\.\d+)?', 'match'),
            ('mingw', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'QTDIR', ';')
    elif sys.platform.startswith('darwin'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            (r'\d+\.\d+(\.\d+)?', 'match'),
            ('macos', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'QTDIR', ':')
    elif sys.platform.startswith('linux'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            (r'\d+\.\d+(\.\d+)?', 'match'),
            ('gcc', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'QTDIR', ':')
    return None

def find_mingwdir():
    if sys.platform.startswith('win'):
        base_paths = [os.sep, os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('mingw', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'MINGWDIR', ';')
    return None

def find_cmakedir():
    if sys.platform.startswith('win'):
        base_paths = [os.sep, os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('CMake', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'CMAKEDIR', ';')
    elif sys.platform.startswith('darwin'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('CMake', 'match'),
            ('CMake.app', 'match'),
            ('Contents', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'CMAKEDIR', ':')
    elif sys.platform.startswith('linux'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('CMake', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'CMAKEDIR', ':')
    return None

def find_ninjadir():
    if sys.platform.startswith('win'):
        base_paths = [os.sep, os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('Ninja', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'NINJADIR', ';', bin_subpath='')
    elif sys.platform.startswith('darwin'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('Ninja', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'NINJADIR', ':', bin_subpath='')
    elif sys.platform.startswith('linux'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('Ninja', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'NINJADIR', ':', bin_subpath='')
    return None

def find_ifdir():
    if sys.platform.startswith('win'):
        base_paths = [os.sep, os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('QtInstallerFramework', 'match'),
            (r'\d+\.\d+(\.\d+)?', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'IFDIR', ';')
    elif sys.platform.startswith('darwin'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('QtIFW', 'search')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'IFDIR', ':')
    elif sys.platform.startswith('linux'):
        base_paths = [os.path.expanduser('~')]
        search_sequence = [
            ('Qt', 'match'),
            ('Tools', 'exists'),
            ('QtInstallerFramework', 'match'),
            (r'\d+\.\d+(\.\d+)?', 'match')
        ]
        return find_tool_in_platform(base_paths, search_sequence, 'IFDIR', ':')
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

    parser.add_argument("--no-build-application", action='store_true', default=False,
    help = "Don't build the application")

    parser.add_argument("--no-sign-application", action='store_true', default=False,
    help = "Don't sign the application on windows and mac")

    parser.add_argument("--no-build-installer", action='store_true', default=False,
    help = "Don't build the installer")

    parser.add_argument("--no-sign-installer", action='store_true', default=False,
    help = "Don't sign the installer on windows and mac")

    parser.add_argument("--factory", action='store_true', default=False,
    help = "Build OpenMV IDE for the factory")

    args = parser.parse_args()

    if args.rpi and not sys.platform.startswith('linux'):
        sys.exit("Linux Only")

    ###########################################################################

    qtdir = find_qtdir(args.rpi)
    mingwdir = find_mingwdir()
    find_cmakedir()
    find_ninjadir()
    ifdir = find_ifdir()
    find_windowssdkdir()

    ideversion = get_ideversion(__folder__)

    builddir = os.path.join(__folder__, "build")
    installdir = os.path.join(builddir, "install")
    if args.rpi: installdir = os.path.join(builddir, "openmv-ide")

    if not os.path.exists(builddir):
        os.mkdir(builddir)

    if not os.path.exists(installdir):
        os.mkdir(installdir)

    cxx_flags_init = ""

    if args.factory:
        cxx_flags_init += "-DFORCE_FORM_KEY_DIALOG "
        cxx_flags_init += "-DFORCE_AUTO_CONNECT "
        cxx_flags_init += "-DFORCE_AUTO_UPDATE=release "
        cxx_flags_init += "-DFORCE_AUTO_RUN "
        cxx_flags_init += "-DFORCE_OVERRIDE_READ_TIMEOUT=3000 "

    if args.rpi:
        installer_name = "openmv-ide-linux-arm64-" + ideversion + ".tar.gz"
        if args.factory: installer_name = installer_name.replace("openmv", "openmv-factory")
        if not args.no_build_application:
            os.makedirs(os.path.join(installdir, "lib/Qt/lib"), exist_ok=True)
            if os.system("cd " + builddir +
            " && wget http://ftp.us.debian.org/debian/pool/main/i/icu/libicu67_67.1-7_arm64.deb"
            " && dpkg-deb -x libicu67_67.1-7_arm64.deb icu67"
            " && cp -rv icu67/usr/lib/aarch64-linux-gnu/* openmv-ide/lib/Qt/lib/"
            " && cmake ../qt-creator -Wno-dev" +
                " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
                " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
                " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
                " \"-DCMAKE_C_COMPILER:FILEPATH=/usr/bin/aarch64-linux-gnu-gcc-9\"" +
                " \"-DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/aarch64-linux-gnu-g++-9\"" +
                " \"-DCMAKE_CXX_FLAGS_INIT:STRING=" + cxx_flags_init + "\"" +
                " \"-DCMAKE_TOOLCHAIN_FILE:UNINITIALIZED=" + os.path.join(qtdir, "lib/cmake/Qt6/qt.toolchain.cmake") + "\"" +
            " && cmake --build . --target all" +
            " && cmake --install . --prefix openmv-ide" +
            " && cmake --install . --prefix openmv-ide --component Dependencies" +
            " && mv share/qtcreator/arm install/share/qtcreator/arm" +
            " && mv share/qtcreator/stedgeai install/share/qtcreator/stedgeai" +
            " && rm -rf bin" + # Save disk space
            " && rm -rf lib" + # Save disk space
            " && rm -rf share" + # Save disk space
            " && rm -rf src"): # Save disk space
                sys.exit("Make Failed...")
        if not args.no_build_installer:
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
                f.write("sudo apt-get install -y libboost-all-dev libudev-dev libinput-dev libts-dev libmtdev-dev libjpeg-dev libfontconfig1-dev libssl-dev libdbus-1-dev libglib2.0-dev libxkbcommon-dev libegl1-mesa-dev libgbm-dev libgles2-mesa-dev mesa-common-dev libasound2-dev libpulse-dev gstreamer1.0-omx libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev  gstreamer1.0-alsa libvpx-dev libsrtp2-dev libsnappy-dev libnss3-dev \"^libxcb.*\" flex bison libxslt-dev ruby gperf libbz2-dev libcups2-dev libatkmm-1.6-dev libxi6 libxcomposite1 libfreetype6-dev libicu-dev libsqlite3-dev libxslt1-dev libavcodec-dev libavformat-dev libswscale-dev libx11-dev freetds-dev libsqlite3-dev libpq-dev libiodbc2-dev firebird-dev libgst-dev libxext-dev libxcb1 libxcb1-dev libx11-xcb1 libx11-xcb-dev libxcb-keysyms1 libxcb-keysyms1-dev libxcb-image0 libxcb-image0-dev libxcb-shm0 libxcb-shm0-dev libxcb-icccm4 libxcb-icccm4-dev libxcb-sync1 libxcb-sync-dev libxcb-render-util0 libxcb-render-util0-dev libxcb-xfixes0-dev libxrender-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-glx0-dev libxi-dev libdrm-dev libxcb-xinerama0 libxcb-xinerama0-dev libatspi2.0-dev libxcursor-dev libxcomposite-dev libxdamage-dev libxss-dev libxtst-dev libpci-dev libcap-dev libxrandr-dev libdirectfb-dev libaudio-dev libxkbcommon-x11-dev libxcb-cursor0 build-essential\n\n")
                f.write("sudo apt-get install -y libpng16-16 libusb-1.0 python3 python3-pip python3-usb\n")
                f.write("sudo cp $DIR/share/qtcreator/pydfu/*.rules /etc/udev/rules.d/\n")
                f.write("sudo udevadm trigger\n")
                f.write("sudo udevadm control --reload-rules\n\n")
                f.write("cp -r \"$DIR/share/icons\" \"/home/$USER/.local/share/icons\"\n")
                f.write("sudo cp -r \"$DIR/share/icons\" /usr/share/\n")
                f.write("rm -rf \"$DIR/share/icons\"\n")
                f.write("sudo gtk-update-icon-cache\n\n")
                f.write("cat > \"/home/$USER/Desktop/openmvide.desktop\" << EOM\n")
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=OpenMV IDE\n")
                f.write("GenericName=OpenMV IDE\n")
                f.write("Comment=The IDE of choice for OpenMV Cam Development.\n")
                f.write("Exec=\"$DIR/bin/openmvide\" %F\n")
                f.write("Icon=OpenMV-openmvide\n")
                f.write("Terminal=false\n")
                f.write("Categories=Development;IDE;Electronics;OpenMV;\n")
                f.write("MimeType=text/x-python;\n")
                f.write("Keywords=embedded electronics;electronics;microcontroller;micropython;computer vision;machine vision;\n")
                f.write("StartupWMClass=openmvide\n")
                f.write("EOM\n")
                f.write("cp \"/home/$USER/Desktop/openmvide.desktop\"  \"/home/$USER/.local/share/applications/\"\n")
                f.write("sudo cp \"/home/$USER/Desktop/openmvide.desktop\" /usr/share/applications/\n")
            os.chmod(os.path.join(installdir, "setup.sh"),
                os.stat(os.path.join(installdir, "setup.sh")).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            if os.system("cd " + builddir +
            " && tar -czvf " + installer_name + " openmv-ide"):
                sys.exit("Make Failed...")

    elif sys.platform.startswith('win'):
        installer_name = "openmv-ide-windows-" + ideversion
        if args.factory: installer_name = installer_name.replace("openmv", "openmv-factory")
        installer_archive_name = installer_name + "-installer-archive.7z"
        if not args.no_build_application:
            if os.system("cd " + builddir +
            " && cmake ../qt-creator" +
                " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
                " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
                " \"-DQT_QMAKE_EXECUTABLE:FILEPATH=" + os.path.join(qtdir, "bin/qmake.exe") + "\"" +
                " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
                " \"-DCMAKE_C_COMPILER:FILEPATH=" + os.path.join(mingwdir, "bin/gcc.exe") + "\"" +
                " \"-DCMAKE_CXX_COMPILER:FILEPATH=" + os.path.join(mingwdir, "bin/g++.exe") + "\"" +
                " \"-DCMAKE_CXX_FLAGS_INIT:STRING=" + cxx_flags_init + "\"" +
            " && cmake --build . --target all" +
            " && cmake --install . --prefix install" +
            " && cmake --install . --prefix install --component Dependencies" +
            " && mv share/qtcreator/arm install/share/qtcreator/arm" +
            " && mv share/qtcreator/stedgeai install/share/qtcreator/stedgeai" +
            " && rm -rf bin" + # Save disk space
            " && rm -rf lib" + # Save disk space
            " && rm -rf share" + # Save disk space
            " && rm -rf src"): # Save disk space
                sys.exit("Make Failed...")
        if not args.no_sign_application:
            if os.system("cd " + builddir +
            " && python -u ../qt-creator/scripts/sign.py install/bin/openmvide.exe"):
                sys.exit("Make Failed...")
        if not args.no_build_installer:
            if os.system("cd " + builddir +
            " && cd install" +
            " && archivegen ../" + installer_archive_name + " bin lib share" +
            " && cd .."
            " && python -u ../qt-creator/scripts/packageIfw.py -i " + ifdir +
            " -v " + ideversion +
            " -a " + installer_archive_name + " " + installer_name):
                sys.exit("Make Failed...")
            if not args.no_sign_installer:
                if os.system("cd " + builddir +
                " && python -u ../qt-creator/scripts/sign.py " + installer_name + ".exe"):
                    sys.exit("Make Failed...")
        else:
            with open(os.path.join(installdir, "README.txt"), 'w') as f:
                f.write("Please run setup.cmd to install OpenMV IDE's drivers:\r\n\r\n")
                f.write("    Double click on setup.cmd\r\n\r\n")
                f.write("And then to run OpenMV IDE:\r\n\r\n")
                f.write("    Double click on bin\\openmvide.exe\r\n")
            with open(os.path.join(installdir, "setup.cmd"), 'w') as f:
                f.write("@echo off\r\n")
                f.write("NET FILE 1>NUL 2>NUL & IF ERRORLEVEL 1 (ECHO You must right-click this file and select \"Run as administrator\" to run the setup script. & ECHO. & PAUSE & EXIT /D)\r\n")
                f.write("cmd /c \"%~dp0\\share\\qtcreator\\drivers\\ftdi\\ftdi.cmd\"\r\n")
                f.write("cmd /c \"%~dp0\\share\\qtcreator\\drivers\\openmv\\openmv.cmd\"\r\n")
                f.write("cmd /c \"%~dp0\\share\\qtcreator\\drivers\\arduino\\arduino.cmd\"\r\n")
                f.write("cmd /c \"%~dp0\\share\\qtcreator\\drivers\\dfuse.cmd\"\r\n")
                f.write("cmd /c \"%~dp0\\share\\qtcreator\\drivers\\vcr.cmd\"\r\n")
                f.write("ECHO All drivers have been successfully installed! & ECHO. & PAUSE & EXIT /D\r\n")
            output_dir = os.path.join(builddir, "openmv-ide")
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            shutil.copytree(os.path.join(builddir, "install"), output_dir)
            if os.system("cd " + output_dir +
            " && archivegen -f zip -c 9 ../" + installer_name + " bin lib share README.txt setup.cmd"):
                sys.exit("Make Failed...")

    elif sys.platform.startswith('darwin'):
        installer_name = "openmv-ide-mac-" + ideversion + ".dmg"
        if args.factory: installer_name = installer_name.replace("openmv", "openmv-factory")
        if not args.no_build_application:
            if os.system("cd " + builddir +
            " && cmake ../qt-creator" +
                " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
                " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
                " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
                " \"-DCMAKE_CXX_FLAGS_INIT:STRING=" + cxx_flags_init + "\"" +
            " && cmake --build . --target all" +
            " && cmake --install . --prefix . --component Dependencies" +
            " && rm -rf share" # Save disk space
            " && rm -rf src"): # Save disk space
                sys.exit("Make Failed...")
        if not args.no_sign_application:
            if os.system("cd " + builddir +
            " && python3 -u ../qt-creator/scripts/sign.py \"OpenMV IDE.app\" || true" +
            " && codesign --deep -s Application --force --options=runtime --timestamp \"OpenMV IDE.app\" || true" +
            " && ditto -c -k -rsrc --sequesterRsrc --keepParent OpenMV\\ IDE.app OpenMV\\ IDE.zip" +
            " && xcrun notarytool submit OpenMV\\ IDE.zip --keychain-profile \"AC_PASSWORD\" --wait || true" +
            " && xcrun stapler staple OpenMV\\ IDE.app || true" +
            " && rm \"OpenMV IDE.zip\" || true"):
                sys.exit("Make Failed...")
        if not args.no_build_installer:
            if os.system("cd " + builddir +
            " && ../qt-creator/scripts/makedmg.sh OpenMV\\ IDE.app " + installer_name):
                sys.exit("Make Failed...")
        if not args.no_sign_installer:
            if os.system("cd " + builddir +
            " && xcrun notarytool submit " + installer_name + " --keychain-profile \"AC_PASSWORD\" --wait || true" +
            " && xcrun stapler staple " + installer_name + " || true"):
                sys.exit("Make Failed...")

    elif sys.platform.startswith('linux'):
        installer_name = "openmv-ide-linux-x86_64-" + ideversion
        if args.factory: installer_name = installer_name.replace("openmv", "openmv-factory")
        installer_archive_name = installer_name + "-installer-archive.7z"
        if not args.no_build_application:
            if os.system("cd " + builddir +
            " && cmake ../qt-creator" +
                " -Wno-dev" +
                " \"-DCMAKE_GENERATOR:STRING=Ninja\"" +
                " \"-DCMAKE_BUILD_TYPE:STRING=Release\"" +
                " \"-DCMAKE_PREFIX_PATH:PATH=" + qtdir + "\"" +
                " \"-DCMAKE_CXX_FLAGS_INIT:STRING=" + cxx_flags_init + "\"" +
            " && cmake --build . --target all" +
            " && cmake --install . --prefix install" +
            " && cmake --install . --prefix install --component Dependencies" +
            " && mv share/qtcreator/arm install/share/qtcreator/arm" +
            " && mv share/qtcreator/stedgeai install/share/qtcreator/stedgeai" +
            " && rm -rf bin" + # Save disk space
            " && rm -rf lib" + # Save disk space
            " && rm -rf share" + # Save disk space
            " && rm -rf src"): # Save disk space
                sys.exit("Make Failed...")
        if not args.no_build_installer:
            if os.system("cd " + builddir +
            " && cd install"
            " && archivegen ../" + installer_archive_name + " bin lib share" +
            " && cd .."
            " && python3 -u ../qt-creator/scripts/packageIfw.py -i " + ifdir +
            " -v " + ideversion + " -a " + installer_archive_name +
            " " + installer_name):
                sys.exit("Make Failed...")
        else:
            with open(os.path.join(installdir, "README.txt"), 'w') as f:
                f.write("Please run setup.sh to install OpenMV IDE dependencies:\n\n")
                f.write("    ./setup.sh\n\n")
                f.write("And then run OpenMV IDE:\n\n")
                f.write("    ./bin/openmvide\n")
            with open(os.path.join(installdir, "setup.sh"), 'w') as f:
                f.write("#! /bin/sh\n\n")
                f.write("DIR=\"$(dirname \"$(readlink -f \"$0\")\")\"\n\n")
                f.write("sudo apt-get install -y libfontconfig1 libfreetype6 libxcb1 libxcb-glx0 libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 libxcb-xfixes0 libxcb-shape0 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 build-essential\n")
                f.write("sudo apt-get install -y libpng16-16 libusb-1.0 python3 python3-pip python3-usb\n")
                f.write("sudo cp $DIR/share/qtcreator/pydfu/*.rules /etc/udev/rules.d/\n")
                f.write("sudo udevadm trigger\n")
                f.write("sudo udevadm control --reload-rules\n\n")
                f.write("cp -r \"$DIR/share/icons\" \"/home/$USER/.local/share/icons\"\n")
                f.write("sudo cp -r \"$DIR/share/icons\" /usr/share/\n")
                f.write("rm -rf \"$DIR/share/icons\"\n")
                f.write("sudo gtk-update-icon-cache\n\n")
                f.write("cat > \"/home/$USER/Desktop/openmvide.desktop\" << EOM\n")
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=OpenMV IDE\n")
                f.write("GenericName=OpenMV IDE\n")
                f.write("Comment=The IDE of choice for OpenMV Cam Development.\n")
                f.write("Exec=\"$DIR/bin/openmvide\" %F\n")
                f.write("Icon=OpenMV-openmvide\n")
                f.write("Terminal=false\n")
                f.write("Categories=Development;IDE;Electronics;OpenMV;\n")
                f.write("MimeType=text/x-python;\n")
                f.write("Keywords=embedded electronics;electronics;microcontroller;micropython;computer vision;machine vision;\n")
                f.write("StartupWMClass=openmvide\n")
                f.write("EOM\n")
                f.write("cp \"/home/$USER/Desktop/openmvide.desktop\"  \"/home/$USER/.local/share/applications/\"\n")
                f.write("sudo cp \"/home/$USER/Desktop/openmvide.desktop\" /usr/share/applications/\n")
            os.chmod(os.path.join(installdir, "setup.sh"),
                os.stat(os.path.join(installdir, "setup.sh")).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            if os.system("cd " + builddir +
            " && rm -rf openmv-ide"
            " && mv install openmv-ide"
            " && tar -czvf " + installer_name + ".tar.gz openmv-ide"):
                sys.exit("Make Failed...")

    else:
        sys.exit("Unknown Platform")

if __name__ == "__main__":
    make()
