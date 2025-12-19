#!/bin/bash

# Check if running in local test mode
# When --local or -l flag is provided, the script will copy the local code-nautilus.py
# instead of downloading from GitHub. This is useful for testing local changes.
LOCAL_MODE=false
if [ "$1" = "--local" ] || [ "$1" = "-l" ]; then
    LOCAL_MODE=true
    echo "Local test mode enabled"
fi

# Helper function to ask yes/no questions with default answer
# Args:
#   $1 - The prompt message to display
#   $2 - The default answer (Y or N)
# Returns:
#   0 for yes, 1 for no
ask_yes_no() {
    local prompt="$1"
    local default_answer="$2"
    local reply
    while true
    do
        read -r -p "$prompt" reply
        if [ -z "$reply" ]
        then
            reply="$default_answer"
        fi
        case "$reply" in
            [yY]) return 0 ;;
            [nN]) return 1 ;;
            *) echo "Please enter y or n." ;;
        esac
    done
}

# Configure which VS Code versions to register in Nautilus context menu
# Creates a configuration file that the Python extension reads to determine
# which VS Code variants should appear in the right-click menu.
# Configuration is saved to ~/.config/code-nautilus/targets.conf
configure_targets() {
    local config_dir="$HOME/.config/code-nautilus"
    local config_file="$config_dir/targets.conf"
    mkdir -p "$config_dir"

    echo "Select VS Code version(s) to register in Nautilus:"
    local register_code
    local register_insiders

    # Ask if user wants to register stable VS Code
    if ask_yes_no "  - Register stable VS Code (code)? [Y/n] " "Y"
    then
        register_code=1
    else
        register_code=0
    fi

    # Ask if user wants to register VS Code Insiders
    if ask_yes_no "  - Register VS Code Insiders (code-insiders)? [y/N] " "N"
    then
        register_insiders=1
    else
        register_insiders=0
    fi

    # If neither version is selected, default to stable version
    if [ "$register_code" -eq 0 ] && [ "$register_insiders" -eq 0 ]
    then
        echo "No version selected. Defaulting to stable VS Code."
        register_code=1
    fi

    # Write configuration file
    # Format: key=value where value is 1 (enabled) or 0 (disabled)
    cat > "$config_file" <<EOF
# VS Code Nautilus Extension Configuration
# Set to 1 to enable, 0 to disable
code=$register_code
code-insiders=$register_insiders
EOF

    echo "Configuration saved to $config_file"
}

# Install python-nautilus dependency
# This package is required for Nautilus to load Python extensions
echo "Installing python-nautilus..."
if type "pacman" > /dev/null 2>&1
then
    # Arch Linux / Manjaro
    if ! pacman -Qi python-nautilus &> /dev/null
    then
        sudo pacman -S --noconfirm python-nautilus
    else
        echo "python-nautilus is already installed"
    fi
elif type "apt-get" > /dev/null 2>&1
then
    # Debian / Ubuntu
    # Package name varies by Ubuntu version (python-nautilus vs python3-nautilus)
    package_name="python-nautilus"
    found_package=$(apt-cache search --names-only $package_name)
    if [ -z "$found_package" ]
    then
        package_name="python3-nautilus"
    fi

    # Check if the package is already installed
    installed=$(apt list --installed $package_name -qq 2> /dev/null)
    if [ -z "$installed" ]
    then
        sudo apt-get install -y $package_name
    else
        echo "$package_name is already installed."
    fi
elif type "dnf" > /dev/null 2>&1
then
    # Fedora / RHEL
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

# Remove previous versions and ensure extension directory exists
# VSCodeExtension.py is the old filename, code-nautilus.py is the new one
echo "Removing previous version (if found)..."
mkdir -p ~/.local/share/nautilus-python/extensions
rm -f ~/.local/share/nautilus-python/extensions/VSCodeExtension.py
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py

# Download and install the extension
# In local mode, copy from current directory; otherwise download from GitHub
if [ "$LOCAL_MODE" = true ]; then
    echo "Using local version for testing..."
    cp "$(dirname "$0")/code-nautilus.py" ~/.local/share/nautilus-python/extensions/code-nautilus.py
else
    echo "Downloading newest version..."
    wget -q -O ~/.local/share/nautilus-python/extensions/code-nautilus.py https://raw.githubusercontent.com/harry-cpp/code-nautilus/master/code-nautilus.py
fi

# Prompt user to configure which VS Code versions to register
configure_targets

# Restart Nautilus to load the new extension
echo "Restarting nautilus..."
nautilus -q

echo "Installation Complete"
