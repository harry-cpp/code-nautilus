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
VSCODE = 'code'

# what name do you want to see in the context menu?
VSCODENAME = 'Code'

# always create new window?
NEWWINDOW = False

# ui language check
lang = os.environ.get("LANG")
label = ""
if "zh" in lang:
    label = '在 ' + VSCODENAME + ' 中打开'
    tip_files = '用 VSCode 打开所选择的文件'
    tip_backgroud = '在 VSCode 中打开当前目录'
else:
    label = 'Open in ' + VSCODENAME
    tip_files = 'Opens the selected files with VSCode'
    tip_backgroud = 'Opens the current directory in VSCode'

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
            args = '--new-window '

        call(VSCODE + ' ' + args + safepaths + '&', shell=True)

    def get_file_items(self, *args):
        files = args[-1]
        item = Nautilus.MenuItem(
            name='VSCodeOpen',
            label=label,
            tip=tip_files
        )
        item.connect('activate', self.launch_vscode, files)

        return [item]

    def get_background_items(self, *args):
        file_ = args[-1]
        item = Nautilus.MenuItem(
            name='VSCodeOpenBackground',
            label=label,
            tip=tip_backgroud
        )
        item.connect('activate', self.launch_vscode, [file_])

        return [item]
