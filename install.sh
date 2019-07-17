#!/bin/bash

# Install python-nautilus
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1
then
    sudo pacman -S --noconfirm python-nautilus
elif type "apt-get" > /dev/null 2>&1
then
    sudo apt-get install -y python-nautilus
elif type "dnf" > /dev/null 2>&1
then
    sudo dnf install -y nautilus-python
else
    echo "Failed to find python-nautilus, please install it manually."
fi

# Remove previous version and setup folder
echo "Removing previous version (if found)..."
if [ $(id -u) == 0 ]; then
  EXT_DIR=/usr/share/nautilus-python/extensions
else
  EXT_DIR=~/.local/share/nautilus-python/extensions
fi 
mkdir -p $EXT_DIR
rm -f $EXT_DIR/VSCodeExtension.py
rm -f $EXT_DIR/code-nautilus.py

# Download and install the extension
echo "Downloading newest version..."
wget --show-progress -O $EXT_DIR/code-nautilus.py https://raw.githubusercontent.com/cra0zy/code-nautilus/master/code-nautilus.py

# Restart nautilus
echo "Restarting nautilus..."
nautilus -q

echo "Installation Complete"
