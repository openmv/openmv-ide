[![IDE Build 🔥](https://github.com/openmv/openmv-ide/actions/workflows/main.yml/badge.svg)](https://github.com/openmv/openmv-ide/actions/workflows/main.yml)
[![GitHub license](https://img.shields.io/github/license/openmv/openmv-ide?label=license%20%E2%9A%96)](https://github.com/openmv/openmv-ide/blob/master/LICENSE)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/openmv/openmv-ide?sort=semver)
[![GitHub forks](https://img.shields.io/github/forks/openmv/openmv-ide?color=green)](https://github.com/openmv/openmv-ide/network)
[![GitHub stars](https://img.shields.io/github/stars/openmv/openmv-ide?color=yellow)](https://github.com/openmv/openmv-ide/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/openmv/openmv-ide?color=orange)](https://github.com/openmv/openmv-ide/issues)

<img  width="480" src="https://raw.githubusercontent.com/openmv/openmv-media/master/logos/openmv-logo/logo.png">

# OpenMV IDE based on Qt Creator

  - [Overview](#overview)
  - [Compiling OpenMV IDE for Windows, Linux, and Mac](#compiling-openmv-ide-for-windows-linux-and-mac)
  - [Compiling OpenMV IDE for RaspberryPi on Linux](#compiling-openmv-ide-for-raspberrypi-on-linux)
  - [Instructions for running the installer silently](#instructions-for-running-the-installer-silently)
    + [Windows](#windows)
    + [Linux](#linux)
    + [Mac](#mac)
  - [Contributing to the project](#contributing-to-the-project)
    + [Contribution guidelines](#contribution-guidelines)

## Overview

OpenMV IDE is a cross platform integrated development enviornment for writing python code to run on your OpenMV Cam. It includes all the necessary features and tools to update your OpenMV Cam's firmware and help you develop your application quickly.

## Compiling OpenMV IDE for Windows, Linux, and Mac

* Install Qt (to the default location).

In `/`, build the ide (using the standard bare terminal):

     git clone --recursive https://github.com/openmv/openmv-ide.git
     cd openmv-ide
     ./make.py

You'll find the installer in `build`.

## Compiling OpenMV IDE for RaspberryPi on Linux

* Install QtRpi.
* Install Qt (to the default location).

In `/`, build the ide (using the standard bare terminal):

     git clone --recursive https://github.com/openmv/openmv-ide.git
     cd openmv-ide
     ./make.py --rpi <path-to-qtrpi-installdir e.g. /opt/qtrpi/raspi/qt5>

You'll find the installer in `build`.

## Instructions for running the installer silently

The Qt Installer Framework features a robust set of command line actions. Using these you can install OpenMV IDE from the command line silently. You can also uninstall the IDE silently using the uninstaller generated by the installer. Please note that the command line installer will not automatically delete an old installation during an upgrade like when in GUI mode.

### Windows

The installer will need administrator privileges which it should ask for when run.

     ./openmv-ide-windows-*.exe --al --am -c in

### Linux

Note: `libxcb-xinerama0` may be required for the installer to run.

     ./openmv-ide-linux-x86_64-*.run --al --am -c in

And then you will need to manually install required libraries for yourself (e.g. for Ubuntu):

     sudo apt-get install -y libpng16-16 libusb-1.0 python3 python3-pip
     sduo pip install pyusb

And **potentially** required libraries (e.g. for Ubuntu):

     sudo apt-get install -y libfontconfig1 libfreetype6 libxcb1 libxcb-glx0 libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 libxcb-xfixes0 libxcb-shape0 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0

Finally, you need to install the udev rules yourself:

     sudo cp openmv-ide/share/qtcreator/pydfu/*.rules /etc/udev/rules.d/
     sudo udevadm trigger
     sudo udevadm control --reload-rules

### Mac

The installer is a DMG with the app inside of it.

     hdiutil attach openmv-ide-linux-mac-*.dmg
     sudo cp -rf /Volumes/OpenMV\ IDE/OpenMV\ IDE.app /Applications
     sudo hdiutil detach /Volumes/OpenMV\ IDE

## Contributing to the project

Contributions are most welcome. If you are interested in contributing to the project, start by creating a fork of each of the following repositories:

* https://github.com/openmv/openmv-ide.git
* https://github.com/openmv/qt-creator.git

Clone the forked openmv-ide repository, and add a remote to the main openmv-ide repository:
```bash
git clone --recursive https://github.com/<username>/openmv-ide.git
git -C openmv-ide remote add upstream https://github.com/openmv/openmv-ide.git
```

Set the `origin` remote of the qt-creator submodule to the forked qt-creator repo:
```bash
git -C openmv-ide/qt-creator remote set-url origin https://github.com/<username>/qtcreator.git
```

Finally add a remote to openmv's qt-creator fork:
```bash
git -C openmv-ide/qt-creator remote add upstream https://github.com/openmv/qt-creator.git
```

Now the repositories are ready for pull requests. To send a pull request, create a new feature branch and push it to origin, and use Github to create the pull request from the forked repository to the upstream openmv/qt-creator repository. For example:
```bash
git checkout -b <some_branch_name>
<commit changes>
git push origin -u <some_branch_name>
```

### Contribution guidelines
Please follow the [best practices](https://developers.google.com/blockly/guides/modify/contribute/write_a_good_pr) when sending pull requests upstream. In general, the pull request should:
* Fix one problem. Don't try to tackle multiple issues at once.
* Split the changes into logical groups using git commits.
* Pull request title should be less than 78 characters, and match this pattern:
  * `<scope>:<1 space><description><.>`
* Commit subject line should be less than 78 characters, and match this pattern:
  * `<scope>:<1 space><description><.>`
