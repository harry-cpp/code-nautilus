# VSCode Nautilus Extension
#
# Place me in ~/.local/share/nautilus-python/extensions/,
# ensure you have python-nautilus package, restart Nautilus, and enjoy :)
#
# This script is released to the public domain.

from gi.repository import Nautilus, GObject
from subprocess import call
import os


# path to vscode
FLATPAK_VSCODE_PATH = "/var/lib/flatpak/exports/bin/com.visualstudio.code"
VSCODE_PATH = "/usr/bin/code"

# path to vscodium
FLATPAK_VSCODIUM_PATH = "/var/lib/flatpak/exports/bin/com.vscodium.codium"
VSCODIUM_PATH = "/usr/bin/codium"

# VSCODENAME: what name do you want to see in the context menu? 

if os.path.exists(FLATPAK_VSCODE_PATH):
    VSCODE = "flatpak run com.visualstudio.code"
    VSCODENAME = 'Code'
elif os.path.exists(FLATPAK_VSCODIUM_PATH):
    VSCODE = "flatpak run com.vscodium.codium"
    VSCODENAME = 'VSCodium'
elif os.path.exists(VSCODE_PATH):
    VSCODE = 'code'
    VSCODENAME = 'Code'
elif os.path.exists(VSCODIUM_PATH):
    VSCODE = 'codium'
    VSCODENAME = 'VSCodium'

# always create new window?
NEWWINDOW = False

# Force wayland? ( Flatpak packages may need to add permissions for wayland )
WAYLAND = True

class VSCodeExtension(GObject.GObject, Nautilus.MenuProvider):

    def launch_vscode(self, menu, files):
        safepaths = ''
        args = ''

        for file in files:
            filepath = file.get_location().get_path()
            safepaths += '"' + filepath + '" '

            # If one of the files we are trying to open is a folder
            # create a new instance of vscode
            if os.path.isdir(filepath) and os.path.exists(filepath):
                args = '--new-window '

        if NEWWINDOW:
            args = '--new-window'

        if WAYLAND and os.environ.get('XDG_SESSION_TYPE') == "wayland":
            print("true")
            args += ' --ozone-platform-hint=auto --enable-features=WaylandWindowDecorations'
        call(VSCODE + ' ' + args + ' ' + safepaths + '&', shell=True)

    def get_file_items(self, *args):
        files = args[-1]
        item = Nautilus.MenuItem(
            name='VSCodeOpen',
            label='Open in ' + VSCODENAME,
            tip='Opens the selected files with VSCode'
        )
        item.connect('activate', self.launch_vscode, files)

        return [item]

    def get_background_items(self, *args):
        file_ = args[-1]
        item = Nautilus.MenuItem(
            name='VSCodeOpenBackground',
            label='Open in ' + VSCODENAME,
            tip='Opens the current directory in VSCode'
        )
        item.connect('activate', self.launch_vscode, [file_])

        return [item]
