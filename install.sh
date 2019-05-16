#!/bin/bash

# Install python-nautilus
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1
then
    sudo pacman -S python-nautilus
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
mkdir -p ~/.local/share/nautilus-python/extensions
rm -f ~/.local/share/nautilus-python/extensions/VSCodeExtension.py
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py

# Download and install the extension
echo "Downloading newest version..."
wget --show-progress -O ~/.local/share/nautilus-python/extensions/code-nautilus.py https://raw.githubusercontent.com/cra0zy/code-nautilus/master/code-nautilus.py

# Restart nautilus
echo "Restarting nautilus..."
nautilus -q

echo "Installation Complete"
