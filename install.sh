#!/bin/bash

# Install python-nautilus
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1; then
    pkgmgr="pacman"
    update="-Sy"
    upgrade="-Syu"
    install="-S"
    silent_yes="--noconfirm"
    check_install="-Qi"
    package_name="python-nautilus"
elif type "apt-get" > /dev/null 2>&1; then
    pkgmgr="apt-get"
    update="update"
    upgrade="upgrade"
    install="install"
    silent_yes="-y"
    check_install="list --installed -qq"
    package_name="python-nautilus"

    # make sure you have the right package name for ubuntu
    [ -z `apt-cache search -n $package_name` ] && package_name="python3-nautilus"
elif type "dnf" > /dev/null 2>&1; then
    pkgmgr="dnf"
    update="check-update"
    upgrade="upgrade"
    install="install"
    silent_yes="-y"
    check_install="list --installed"
    package_name="nautilus-python"
else
    echo "Distribution package manager not supported yet"
    echo "Please read instructions on installing extensions manually"
    exit 1
fi

echo  "Checking if Python bindings for Nautilus are installed"
$pkgmgr $check_install $package_name &> /dev/null

if [ `echo $?` -eq 1 ]; then
    echo "$package_name not installed"
    echo "Synchronozing package databases"
    sudo $pkgmgr $update $silent_yes

    echo "Installing $package_name ..."
    sudo $pkgmgr $install $silent_yes $package_name
    [ `echo $?` -eq 1 ] && echo "Error Installing $package_name. Please install manually"
else
    echo "Python bindings package already installed"
fi

echo "Creating nautilus extensions folder..."
mkdir -p ~/.local/share/nautilus-python/extensions

# Remove previous version
echo "Removing previous version (if found)..."
rm -f ~/.local/share/nautilus-python/extensions/VSCodeExtension.py
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py

# Download and install the extension
echo "Downloading newest version..."
wget --show-progress -q -O ~/.local/share/nautilus-python/extensions/code-nautilus.py https://raw.githubusercontent.com/harry-cpp/code-nautilus/master/code-nautilus.py

# Restart nautilus
echo "Restarting nautilus..."
nautilus -q

echo "Installation Complete"
