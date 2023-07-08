# openmv-ide #

OpenMV IDE based on Qt Creator.

Instructions for Compiling OpenMV IDE for Desktop (Windows 64-bit, Ubuntu 64-bit, Mac)
======================================================================================

* Install Qt (to the default location).

In `/`, build the ide (using the standard bare terminal):

     git clone --recursive https://github.com/openmv/openmv-ide.git
     cd openmv-ide
     ./make.py

You'll find the installer in `build`.

Instructions for Compiling OpenMV IDE for the RaspberryPi on Ubuntu (64-bit)
============================================================================

* Install QtRpi.
* Install Qt (to the default location).

In `/`, build the ide (using the standard bare terminal):

     git clone --recursive https://github.com/openmv/openmv-ide.git
     cd openmv-ide
     ./make.py --rpi <path-to-qtrpi-installdir e.g. /opt/qtrpi/raspi/qt5>

You'll find the installer in `build`.

Instructions for running the installer silently
===============================================

The Qt Installer Framework features a robust set of command line actions. Using these you can install OpenMV IDE from the command line silently. You can also uninstall the IDE silently. Please note that the command line installer will not automatically delete an old installation like when in GUI mode. Additionally, on linux it will not allow you to select to run root install operations.

Windows
-------

     ./openmv-ide-windows-*.exe --al --am -c in

Linux
-----

Note: `libxcb-xinerama0` may be required for the installer to run.

     ./openmv-ide-linux-x86_64-*.run --al --am -c in

And then you will need to manually install required libraries yourself (e.g. for Ubuntu):

     sudo apt-get install -y libpng16-16 libusb-1.0 python3 python3-pip

And **potentially** required libraries (e.g. for Ubuntu):

     sudo apt-get install -y libfontconfig1 libfreetype6 libxcb1 libxcb-glx0 libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 libxcb-xfixes0 libxcb-shape0 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0

Finally, then you need to install the udev rules yourself:

     sudo cp openmv-ide/share/qtcreator/pydfu/*.rules /etc/udev/rules.d/
     sudo udevadm trigger
     sudo udevadm control --reload-rules
