# openmv-ide #
Qt Creator based OpenMV IDE

Instructions for Compiling OpenMV-IDE for Desktop
=================================================

* Install 7-Zip and add it to PATH.
* Install Python 2.7 and add it to PATH.
* Install Qt (to the default location).
* Install The Qt Installer Framework (to the default location).

In `/`, build the ide (using the standard bare terminal):

     make.py

You'll find the installer in `build`.



Instructions for How to Cross-Compile Qt 5.6.2 and OpenMV-IDE for the Raspberry Pi 2 and 3 from an Ubuntu 14.04+ Host machine
===============================================================================

Note: You will need a Raspberry Pi (preferrably a RPi 3) in order to create the
sysroot image.  Once you have a sysroot image, the RPi is no longer needed
for cross-compiling unless you need to rebuild the sysroot for system updates.


Cross Compiling Qt 5.6.2
------------------------

1. Create a sysroot image to use on your RPi:

    1. Download latest Raspbian Jessie SDCard image from:
		https://www.raspberrypi.org/downloads/raspbian/

    2. Burn image to SDCard using their instructions (recommend at least a 16GB card)
		This can either be the same SDCard you plan to use with your RPi for running
		OpenMV-IDE or can be a separate SDCard used only for the cross-compile process.

    3. Boot and configure your RPi as needed for your monitor and expand the SDCard

    4. Enable source code packages by editing the sources.list:
          ```
          $ cd /etc/apt
          $ nano sources.list
          (Remove the comment on the "deb-src" lines and save the file)
          ```

    5. Upgrade your RPi image and reboot to handle kernel updates, etc.:
          ```
          $ sudo apt-get update
          $ sudo upgrade --with-new-pkgs
          $ sudo shutdown -r now
          ```
    6. Install build dependencies for Qt:
         ```
          $ sudo apt-get build-dep qt4-x11
          $ sudo apt-get build-dep libqt5gui5
          $ sudo apt-get install libudev-dev libinput-dev libts-dev libxcb-xinerama0-dev libxcb-xinerama0
          $ sudo apt-get install chrpath
          $ sudo apt-get install p7zip-full
          ```
    7. Install additional build dependencies for OpenMV-IDE:
		Note: If in the future OpenMV-IDE dependencies change as new functionality is added, this
		list will have to be updated and a new sysroot image will have to be created:
          ```
          $ sudo apt-get install libusb-1.0.0 libusb-1.0.0-dev libusb-dev python-pip
          $ sudo pip install pyusb
          ```

2. Prepare the Host PC (the following should be run on your Host PC):

    1. Enable source code packages by editing the sources.list:
          ```
          $ cd /etc/apt
          $ nano sources.list
          (Remove the comment on the "deb-src" lines and save the file)
          ```
    2. Install Qt and OpenMV-IDE build dependencies so that all build-essential
	parts get installed:
          ```
          $ sudo apt-get update
          $ sudo apt-get build-dep qt4-x11
          $ sudo apt-get build-dep libqt5gui5
          $ sudo apt-get install libudev-dev libinput-dev libts-dev libxcb-xinerama0-dev libxcb-xinerama0
          $ sudo apt-get install chrpath
          $ sudo apt-get install p7zip-full
          $ sudo apt-get install libusb-1.0.0 libusb-1.0.0-dev libusb-dev python-pip
          $ sudo pip install pyusb
          $ sudo apt-get install git
          ```
    3. Download and install QtIFW (Installer Framework) from:
		https://download.qt.io/official_releases/qt-installer-framework/
		(You should be able to just select the latest available version)

    4. Create the folder for doing the cross-compile and install the Raspberry Pi Cross-Compile Tools:
          ```
          $ mkdir ~/raspi
          $ cd ~/raspi
          $ git clone https://github.com/raspberrypi/tools
          ```

3. Copy the sysroot to the Host PC.  Here, you have two options.  Do one of the following:

    1. You can shutdown the RPi and mount the SDCard on your Host PC and copy the necessary files to your working copy.  Replace <card-path> with the correct mount path to your SDCard:
          ```
          $ cd ~/raspi
          $ mkdir sysroot sysroot/usr sysroot/opt
          $ cp -dR /<card-path>/lib sysroot
          $ cp -dR /<card-path>/usr/include sysroot/usr
          $ cp -dR /<card-path>/usr/lib sysroot/usr
          $ cp -dR /<card-path>/opt/vc sysroot/opt
          ```

    2. OR, You can leave your RPi running and use rsync to transfer the files via the network.  Replace "raspberrypi.local" below with the correct network name or IP address of your RPi, which must be network accessible for this method.  Note that this option is slower than #1, but on future updates, 'rsync' can be used to simply update files that have changed and will be faster next time:
          ```
          $ cd ~/raspi
          $ mkdir sysroot sysroot/usr sysroot/opt
          $ rsync -avz pi@raspberrypi.local:/lib sysroot
          $ rsync -avz pi@raspberrypi.local:/usr/include sysroot/usr
          $ rsync -avz pi@raspberrypi.local:/usr/lib sysroot/usr
          $ rsync -avz pi@raspberrypi.local:/opt/vc sysroot/opt
          ```

4. Update the symlinks in the sysroot copy on the Host PC:
	This downloads a helper script that will automatically fix all
	absolute symlink paths in the copied sysroot to be relative symlinks:
     ```
     $ cd ~/raspi
     $ wget https://raw.githubusercontent.com/riscv/riscv-poky/master/scripts/sysroot-relativelinks.py
     $ chmod +x sysroot-relativelinks.py
     $ ./sysroot-relativelinks.py sysroot
     ```


5. Download and Cross-Compile Qt 5.6.2 on the Host PC:

      ```
     $ cd ~/raspi
     $ wget https://download.qt.io/official_releases/qt/5.6/5.6.2/single/qt-everywhere-opensource-src-5.6.2.7z
     (or if that link doesn't work, download from https://download.qt.io/ possibly in the archives)
	
     $ 7z x qt-everywhere-opensource-src-5.6.2.7z
     $ cd qt-everywhere-opensource-src-5.6.2

     $ ./configure -release -opengl es2 -device linux-rasp-pi2-g++ -device-option CROSS_COMPILE=~/raspi/tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf- -sysroot ~/raspi/sysroot -opensource -confirm-license -make libs -skip wayland -no-pkg-config -prefix /usr/local/qt5pi -extprefix ~/raspi/qt5pi -hostprefix ~/raspi/qt5 -v
     (NOTE: If your Host is 32-bit instead of 64-bit, remove the "-x64" suffix in the "gcc-linaro-arm-linux-gnueabihf-raspbian-x64" path on the call to configure)
     (NOTE: You may be able to remove the "-skip wayland" if you need wayland support on the RPi.  But I only encountered errors and problems trying to compile it and omitted it since I didn't need it on my RPi)

     $ make -j 8
     (NOTE: the "-j 8" will speed up the build by using parallel building on multiple cores.
     This number can be adjusted based on the amount of memory and number of cores on the host
     or the option can be removed entirely, albeit the compile will be slower without it)

     $ make install
     (NOTE: The "make install" will install the cross-compiled Qt in the "~/raspi" folder
     with the Host packages in "~/raspi/qt5" and the target RPi packages in "~/raspi/qt5pi")
     ```

At this point, Qt 5.6.2 should be completely cross-compiled and ready for use.  For
     future rebuilds of OpenMV-IDE, you can continue to use this existing Qt without needing
     to rebuild it, though you may need to update the sysroot image if dependencies for
     OpenMV-IDE change.


Cross Compiling OpenMV-IDE
--------------------------

1. First complete the cross-compile of Qt 5.6.2 as outlined above

2. Clone the openmv-ide repository and submodules to the Host PC:

     ```
     $ cd ~/raspi
     $ git clone https://github.com/openmv/openmv-ide.git
     $ cd openmv-ide
     $ git submodule init
     $ git submodule update --recursive
     $ cd qt-creator
     $ git submodule init
     $ git submodule update --recursive
     ```

3. Set the environment to point to the cross-compiled Qt and Build openmv-ide:

     ```
     $ cd ~/raspi/openmv-ide
     $ export QTDIR=~/raspi/qt5
     $ export PATH=~/raspi/qt5/bin:$PATH
     $ ./make.py
     ```

4. When done, you should have a 7-Zip archive in the ~/raspi/openmv-ide/build
	folder.  Copy this to your RPi, either by copying it directly to the
	SDCard image on your Host PC or via sftp to the RPi via the network
	(replacing "raspberrypi.local" below with the correct network name or IP
	address of your RPi, which must be network accessible for this method.).
	Replace the "openmv-ide-linux-arm-1.6.0-installer-archive.7z" filename
	below with the one for the version of openmv-ide that you just compiled:
     ```
     $ cd ~/raspi/openmv-ide/build
     $ sftp pi@raspberrypi.local
     sftp> put openmv-ide-linux-arm-1.6.0-installer-archive.7z
     sftp> exit
     ```

5. Install it on your RPi, by running the following on your RPi:

     ```
     $ mkdir ~/openmvide
     $ cd ~/openmvide
     $ 7z x ../openmv-ide-linux-arm-1.6.0-installer-archive.7z
     ```

6. The openmvide application should now be ready to use on your RPi.
	At this point, follow the OpenMV-IDE website instructions for
	setting up udev rules for Linux environments so that your RPi will
	properly see your OpenMV Camera, and make sure the 'pi' user
	is part of the dialout group (outlined here for convenience):

     ```
     $ sudo adduser pi dialout
     $ sudo cp ~/openmvide/share/qtcreator/pydfu/50-openmv.rules /etc/udev/rules.d/50-openmv.rules
     $ sudo udevadm control --reload-rules
     ```

7. Running openmvide on the RPi will depend on what environment you
	want to run it in.  If you are running it inside of the X11 server
	that is default on most Raspbian images, you can bring up a terminal
	in your X11 server and enter the following:

     ```
     $ cd ~/openmvide/bin
     $ ./openmvide -platform xcb
     (NOTE: the "-platform xcb" is important to tell Qt to use the X11
     front-end.  The default is "eglfs" (OpenGL Full-Screen) which will
     likely hang or crash if trying to use it at the same time as X11.)
     ```

8. If you want to run openmvide outside of X11 as a single, stand-alone
	application on your RPi, you can make use of the eglfs front-end
	of Qt.  However, you'll first want to fix the EGL/GLES library
	issues by following step #11 at the following URL, which have been
	documented below in case this URL changes:
	https://wiki.qt.io/RaspberryPi2EGLFS#Step_by_step

     ```
     (on the RPi):
     $ cd /usr/lib/arm-linux-gnueabihf/
     $ sudo cp libEGL.so.1.0.0 libEGL.so.1.0.0.orig
     $ sudo cp libGLESv2.so.2.0.0 libGLESv2.so.2.0.0.orig
     $ sudo rm /usr/lib/arm-linux-gnueabihf/libEGL.so.1.0.0 /usr/lib/arm-linux-gnueabihf/libGLESv2.so.2.0.0
     $ sudo ln -s /opt/vc/lib/libEGL.so /usr/lib/arm-linux-gnueabihf/libEGL.so.1.0.0
     $ sudo ln -s /opt/vc/lib/libGLESv2.so /usr/lib/arm-linux-gnueabihf/libGLESv2.so.2.0.0
     ```

And that's it...  At this point, OpenMV-IDE should be runnable on your Raspberry Pi.
