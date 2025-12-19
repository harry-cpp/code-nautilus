# VSCode Nautilus Extension
#
# Adds "Open in Code" context menu items to Nautilus file manager.
# Supports both VS Code stable and Insiders versions.
#
# Installation:
#   Place in ~/.local/share/nautilus-python/extensions/
#   Ensure python-nautilus package is installed
#   Restart Nautilus
#
# Configuration:
#   Edit ~/.config/code-nautilus/targets.conf to enable/disable specific VS Code versions
#
# This script is released to the public domain.

from gi.repository import Nautilus, GObject
from subprocess import call
import os
import shutil

# Configuration file location
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'code-nautilus')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'targets.conf')

# Available VS Code targets
# Format: 'config-key': ('Display Name', 'Environment Variable', 'Default Command')
TARGET_OPTIONS = {
    'code': ('Code', 'VSCODE_BIN', 'code'),
    'code-insiders': ('Code - Insiders', 'VSCODE_INSIDERS_BIN', 'code-insiders'),
}


def _register_editor(name, env_var, default_cmd, targets):
    """
    Register a VS Code editor if it exists on the system.

    Args:
        name: Display name for the menu item (e.g., "Code", "Code - Insiders")
        env_var: Environment variable to check for custom command path
        default_cmd: Default command to use if env var is not set
        targets: List to append the registered editor to
    """
    cmd = os.environ.get(env_var)
    cmd = cmd.strip() if cmd else default_cmd
    if not cmd:
        return
    # Only register if the command is actually available on the system
    if shutil.which(cmd):
        targets.append((name, cmd))


def _load_configured_target_keys():
    """
    Load which VS Code targets are enabled from the configuration file.

    Reads ~/.config/code-nautilus/targets.conf and returns a list of
    enabled target keys (e.g., ['code', 'code-insiders']).

    Configuration format:
        code=1
        code-insiders=0

    Returns:
        List of enabled target keys. Defaults to ['code'] if config is missing
        or no targets are enabled.
    """
    selected = []
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as config:
                for raw_line in config:
                    line = raw_line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    # Only process valid target keys
                    if key.strip() not in TARGET_OPTIONS:
                        continue
                    # Check if target is enabled (value is truthy)
                    if value.strip().lower() in ('1', 'true', 'yes', 'y'):
                        selected.append(key.strip())
        except OSError:
            pass

    # Default to stable VS Code if no configuration found
    if not selected:
        selected.append('code')
    return selected


# Build list of available VS Code targets based on configuration and system availability
VSCODE_TARGETS = []
for target_key in _load_configured_target_keys():
    option = TARGET_OPTIONS.get(target_key)
    if option:
        _register_editor(option[0], option[1], option[2], VSCODE_TARGETS)

# Fallback: if no configured targets are available, default to stable VS Code
if not VSCODE_TARGETS:
    fallback = TARGET_OPTIONS['code']
    VSCODE_TARGETS.append((fallback[0], fallback[2]))

# Set to True to always open files in a new VS Code window
# When False, files/folders will open in existing window unless a folder is opened
NEWWINDOW = False


class VSCodeExtension(GObject.GObject, Nautilus.MenuProvider):
    """
    Nautilus extension that adds VS Code context menu items.

    Provides two types of menu items:
    1. File items: When right-clicking on files/folders
    2. Background items: When right-clicking on empty space in a directory
    """

    def launch_vscode(self, menu, data):
        """
        Launch VS Code with the selected files/folders.

        Args:
            menu: The menu item that was clicked (unused)
            data: Tuple of (files, executable) where:
                  - files: List of Nautilus file objects
                  - executable: Path to VS Code executable
        """
        files, executable = data
        safepaths = ''
        args = ''

        for file in files:
            filepath = file.get_location().get_path()
            # Quote paths to handle spaces and special characters
            safepaths += '"' + filepath + '" '

            # If opening a folder, always create a new VS Code window
            # This prevents folders from opening as workspace additions
            if os.path.isdir(filepath) and os.path.exists(filepath):
                args = '--new-window '

        # Force new window if NEWWINDOW is enabled
        if NEWWINDOW:
            args = '--new-window '

        # Execute VS Code in background
        call(executable + ' ' + args + safepaths + '&', shell=True)

    def get_file_items(self, *args):
        """
        Create context menu items when right-clicking on files/folders.

        Returns:
            List of Nautilus.MenuItem objects, one for each enabled VS Code variant
        """
        files = args[-1]
        items = []
        for idx, (name, executable) in enumerate(VSCODE_TARGETS):
            item = Nautilus.MenuItem(
                name='VSCodeOpen{0}'.format(idx),
                label='Open in ' + name,
                tip='Opens the selected files with VSCode'
            )
            item.connect('activate', self.launch_vscode, (files, executable))
            items.append(item)

        return items

    def get_background_items(self, *args):
        """
        Create context menu items when right-clicking on empty space in a directory.

        Returns:
            List of Nautilus.MenuItem objects for opening the current directory
        """
        file_ = args[-1]
        items = []
        for idx, (name, executable) in enumerate(VSCODE_TARGETS):
            item = Nautilus.MenuItem(
                name='VSCodeOpenBackground{0}'.format(idx),
                label='Open in ' + name,
                tip='Opens the current directory in VSCode'
            )
            item.connect('activate', self.launch_vscode, ([file_], executable))
            items.append(item)

        return items
