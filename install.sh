#!/bin/bash

# Install python-nautilus
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1
then
    sudo pacman -S --noconfirm python-nautilus
elif type "apt-get" > /dev/null 2>&1
then
    package_name="python-nautilus"
    if [ -z `apt-cache search --names-only $package_name` ]
    then
        package_name="python3-nautilus"
    fi
    installed=`apt list --installed $package_name -qq 2> /dev/null`
    if [ -z "$installed" ]
    then
        sudo apt-get install -y $package_name
    else
        echo "python-nautilus is already installed."
    fi
elif type "dnf" > /dev/null 2>&1
then
    installed=`dnf list --installed nautilus-python 2> /dev/null`
    if [ -z "$installed" ]
    then
        sudo dnf install -y nautilus-python
    else
        echo "nautilus-python is already installed."
    fi
else
    echo "Failed to find python-nautilus, please install it manually."
fi

# Remove previous version and setup folder
echo "Removing previous version (if found)..."
mkdir -p ~/.local/share/nautilus-python/extensions
rm -f ~/.local/share/nautilus-python/extensions/VSCodeExtension.py
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py

# Download and install the extension
echo "Downloading newest version..."
wget --show-progress -q -O ~/.local/share/nautilus-python/extensions/code-nautilus.py https://raw.githubusercontent.com/cra0zy/code-nautilus/master/code-nautilus.py

# Restart nautilus
echo "Restarting nautilus..."
nautilus -q

echo "Installation Complete"
