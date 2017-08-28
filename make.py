#!/usr/bin/env python

# by: Kwabena W. Agyeman - kwagyeman@openmv.io

import argparse, glob, multiprocessing, os, re, shutil, stat, sys, subprocess

def match(d0, d1):
    x = [x for x in os.listdir(d0) if re.match(d1, x)]
    return os.path.join(d0, x[0]) if x else None

def search(d0, d1):
    x = [x for x in os.listdir(d0) if re.search(d1, x)]
    return os.path.join(d0, x[0]) if x else None

def find_qtdir(rpi):
    if rpi:
        os.environ["QTDIR"] = rpi
        path = os.path.join(rpi, "bin") + ':'
        os.environ["PATH"] = path + os.environ["PATH"]
        return rpi
    elif sys.platform.startswith('win'):
        qtdir = match(os.sep, r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d\.\d(\.\d)?")
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
            qtdir = match(qtdir, r"\d\.\d(\.\d)?")
            if qtdir:
                qtdir = search(qtdir, r"clang")
                if qtdir:
                    os.environ["QTDIR"] = qtdir
                    path = ':' + os.path.join(qtdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtdir
    elif sys.platform.startswith('linux'):
        qtdir = match(os.path.expanduser('~'), r"Qt")
        if qtdir:
            qtdir = match(qtdir, r"\d\.\d(\.\d)?")
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
    return None

def find_qtcdir():
    if sys.platform.startswith('win'):
        qtcdir = match(os.sep, r"Qt")
        if qtcdir:
            qtcdir = match(qtcdir, r"Tools")
            if qtcdir:
                qtcdir = match(qtcdir, r"QtCreator")
                if qtcdir:
                    os.environ["QTCDIR"] = qtcdir
                    path = ';' + os.path.join(qtcdir, "bin")
                    os.environ["PATH"] = os.environ["PATH"] + path
                    return qtcdir
    return None

def find_ifdir():
    if sys.platform.startswith('win'):
        ifdir = match(os.sep, r"Qt")
        if ifdir:
            ifdir = search(ifdir, r"QtIFW")
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
            ifdir = search(ifdir, r"QtIFW")
            if ifdir:
                os.environ["IFDIR"] = ifdir
                path = ':' + os.path.join(ifdir, "bin")
                os.environ["PATH"] = os.environ["PATH"] + path
                return ifdir
    return None

def make():

    __folder__ = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description =
    "Make Script")

    parser.add_argument("--rpi", nargs = '?',
    help = "Cross Compile QTDIR for the Raspberry Pi")

    parser.add_argument("-u", "--upload", nargs = '?',
    help = "FTP Password")

    args = parser.parse_args()

    if args.rpi and not sys.platform.startswith('linux'):
        sys.exit("Linux Only")

    ###########################################################################

    cpus = multiprocessing.cpu_count()

    qtdir = find_qtdir(args.rpi)
    mingwdir = find_mingwdir()
    qtcdir = find_qtcdir()
    ifdir = find_ifdir()

    builddir = os.path.join(__folder__, "build")
    installdir = os.path.join(builddir, "install")

    if not os.path.exists(builddir):
        os.mkdir(builddir)

    installer = ""

    if args.rpi:
        # Add Fonts...
        if os.path.exists(os.path.join(installdir, "lib/Qt/lib/fonts")):
            shutil.rmtree(os.path.join(installdir, "lib/Qt/lib/fonts"), ignore_errors = True)
        shutil.copytree(os.path.join(__folder__, "dejavu-fonts/fonts/"),
                        os.path.join(installdir, "lib/Qt/lib/fonts"))
        # Add README.txt...
        with open(os.path.join(installdir, "README.txt"), 'w') as f:
            f.write("Please run setup.sh to install OpenMV IDE dependencies... e.g.\n\n")
            f.write("./setup.sh\n\n")
            f.write("source ~/.bashrc\n\n")
            f.write("./bin/openmvide.sh\n\n")
        # Add setup.sh...
        with open(os.path.join(installdir, "setup.sh"), 'w') as f:
            f.write("#! /bin/sh\n\n")
            f.write("sudo apt-get install -y libxcb* libGLES* libts* libsqlite* libodbc* libsybdb* libusb-1.0 python-pip\n")
            f.write("sudo pip install pyusb\n\n")
            f.write("sudo cp $( dirname \"$0\" )/share/qtcreator/pydfu/50-openmv.rules /etc/udev/rules.d/50-openmv.rules\n")
            f.write("sudo udevadm control --reload-rules\n\n")
            f.write("if [ -z \"${QT_QPA_PLATFORM}\" ]; then\n")
            f.write("    echo >> ~/.bashrc\n")
            f.write("    echo \"# Force Qt Apps to use xcb\" >> ~/.bashrc\n")
            f.write("    echo \"export QT_QPA_PLATFORM=xcb\" >> ~/.bashrc\n")
            f.write("    echo\n")
            f.write("    echo Please type \"source ~/.bashrc\".\n")
            f.write("fi\n\n")
        os.chmod(os.path.join(installdir, "setup.sh"),
            os.stat(os.path.join(installdir, "setup.sh")).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        # Build...
        if os.system("cd " + builddir +
        " && qmake ../qt-creator/qtcreator.pro -r" +
        " && make -r -w -j" + str(cpus) +
        " && make bindist INSTALL_ROOT="+installdir):
            sys.exit("Make Failed...")
        installer = glob.glob(os.path.join(builddir, "openmv-ide-*.tar.gz"))[0]

    elif sys.platform.startswith('win'):
        if os.system("cd " + builddir +
        " && qmake ../qt-creator/qtcreator.pro -r -spec win32-g++" +
        " && jom -j" + str(cpus) +
        " && jom installer INSTALL_ROOT="+installdir + " IFW_PATH="+ifdir):
            sys.exit("Make Failed...")
        installer = glob.glob(os.path.join(builddir, "openmv-ide-*.exe"))[0]

    elif sys.platform.startswith('darwin'):
        if os.system("cd " + builddir +
        " && qmake ../qt-creator/qtcreator.pro -r -spec macx-clang CONFIG+=x86_64" +
        " && make -j" + str(cpus) +
        " && make deployqt"):
            sys.exit("Make Failed...")
        os.system("cd " + builddir + " && make codesign SIGNING_IDENTITY=Application")
        if os.system("cd " + builddir + " && make dmg"):
            sys.exit("Make Failed...")
        installer = glob.glob(os.path.join(builddir, "openmv-ide-*.dmg"))[0]

    elif sys.platform.startswith('linux'):
        # Add Fonts...
        if os.path.exists(os.path.join(installdir, "lib/Qt/lib/fonts")):
            shutil.rmtree(os.path.join(installdir, "lib/Qt/lib/fonts"), ignore_errors = True)
        shutil.copytree(os.path.join(__folder__, "dejavu-fonts/fonts/"),
                        os.path.join(installdir, "lib/Qt/lib/fonts"))
        # Add README.txt...
        with open(os.path.join(installdir, "README.txt"), 'w') as f:
            f.write("Please run setup.sh to install OpenMV IDE dependencies... e.g.\n\n")
            f.write("./setup.sh\n\n")
            f.write("./bin/openmvide.sh\n\n")
        # Add setup.sh...
        with open(os.path.join(installdir, "setup.sh"), 'w') as f:
            f.write("#! /bin/sh\n\n")
            f.write("sudo apt-get install -y libusb-1.0 python-pip\n")
            f.write("sudo pip install pyusb\n\n")
            f.write("sudo cp $( dirname \"$0\" )/share/qtcreator/pydfu/50-openmv.rules /etc/udev/rules.d/50-openmv.rules\n")
            f.write("sudo udevadm control --reload-rules\n\n")
        os.chmod(os.path.join(installdir, "setup.sh"),
            os.stat(os.path.join(installdir, "setup.sh")).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        # Build...
        if os.system("cd " + builddir +
        " && qmake ../qt-creator/qtcreator.pro -r -spec linux-g++" +
        " && make -r -w -j" + str(cpus) +
        " && make installer INSTALL_ROOT="+installdir + " IFW_PATH="+ifdir):
            sys.exit("Make Failed...")
        installer = glob.glob(os.path.join(builddir, "openmv-ide-*.run"))[0]

    else:
        sys.exit("Unknown Platform")

    ###########################################################################

    if args.upload:
        remotedir = os.path.splitext(os.path.basename(installer))[0]
        if args.rpi: # Remove .tar
            remotedir = os.path.splitext(remotedir)[0]
        uploaddir = os.path.join(builddir, remotedir)

        if not os.path.exists(uploaddir):
            os.mkdir(uploaddir)

        shutil.copy2(installer, uploaddir)

        subprocess.check_call(["python", "ftpsync.py", "-u", "-l",
        "ftp://upload@openmv.io:"+args.upload+"@ftp.openmv.io/"+remotedir,
        uploaddir])

if __name__ == "__main__":
    make()

