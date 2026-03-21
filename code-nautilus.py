# VSCode Nautilus Extension
#
# Place me in ~/.local/share/nautilus-python/extensions/,
# ensure you have python-nautilus package, restart Nautilus, and enjoy :)
#
# This script is released to the public domain.

from gi.repository import Nautilus, GObject
from pathlib import Path
import subprocess
import json
import binascii
import re
import shutil

# path to vscode
VSCODE = "code"

# what name do you want to see in the context menu?
VSCODENAME = "Code"

# always create new window?
NEWWINDOW = False

# Decide where you want to open multi files in
# First window 0, last window -1
OPEN_MULTI_FILES_IN = -1

if not shutil.which(VSCODE):
    raise RuntimeError(f"VSCode executable '{VSCODE}' not found on PATH")

# VsCode uses JSONC not JSON, I dont want to include another dependency for this
# Need to read the devcontainer.json to pull out workspace name if it exists
def _strip_jsonc_comments(text: str) -> str:
    # Skip // sequences that appear inside quoted strings
    return re.sub(r'"(?:[^"\\]|\\.)*"|//[^\n]*', lambda m: m.group(0) if m.group(0).startswith('"') else "", text)


class VSCodeExtension(GObject.GObject, Nautilus.MenuProvider):
    def launch_vscode(self, _, paths: list[Path], reuse_window: bool = False):
        dirs = [p for p in paths if p.is_dir()]
        files = [p for p in paths if not p.is_dir()]

        if dirs:
            # Open all but the last directory each in their own window
            for d in dirs[:-1]:
                subprocess.Popen([VSCODE, "--new-window", str(d)])
            # Open the last directory (and any selected files) together in one window
            window_flag = "--reuse-window" if reuse_window else "--new-window"
            subprocess.Popen([VSCODE, window_flag, str(dirs[OPEN_MULTI_FILES_IN])] + [str(f) for f in files])
        else:
            cmd = [VSCODE]
            if reuse_window:
                cmd.append("--reuse-window")
            elif NEWWINDOW:
                cmd.append("--new-window")
            cmd.extend(str(p) for p in files)
            subprocess.Popen(cmd)

    def launch_vscode_reuse(self, menu_item, paths: list[Path]):
        self.launch_vscode(menu_item, paths, reuse_window=True)

    def launch_vscode_devcontainer(self, _, path: Path):
        hex_config = binascii.hexlify(json.dumps({"hostPath": str(path)}).encode()).decode()
        # Determine workspace path inside the container.
        # Check devcontainer.json for a custom workspaceFolder first.
        workspace_path = self._get_container_workspace(path)
        uri = f"vscode-remote://dev-container+{hex_config}{workspace_path}"
        subprocess.Popen([VSCODE, "--folder-uri", uri])

    def _get_container_workspace(self, hostpath: Path) -> str:
        folder_name = hostpath.name
        default = str(Path("/workspaces") / folder_name)
        devcontainer_json = hostpath / ".devcontainer" / "devcontainer.json"
        if devcontainer_json.exists():
            try:
                text = devcontainer_json.read_text(encoding="utf-8")
                config = json.loads(_strip_jsonc_comments(text))
                return config.get("workspaceFolder") or default
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                pass
        return default

    def _devcontainer_item(self, name, filepath: Path):
        if not (filepath.is_dir() and (filepath / ".devcontainer" / "devcontainer.json").is_file()):
            return None
        item = Nautilus.MenuItem(
            name=name,
            label=f"Open in {VSCODENAME} DevContainer",
            tip="Opens the folder in a VSCode DevContainer",
        )
        item.connect("activate", self.launch_vscode_devcontainer, filepath)
        return item

    # nautilus-python passes (files,) or (window, files) depending on API version;
    # args[-1] is always the file list.
    def get_file_items(self, *args):
        files = args[-1]
        paths = [Path(p) for f in files if (p := f.get_location().get_path()) is not None]
        items = []
        item = Nautilus.MenuItem(
            name="VSCodeOpen",
            label=f"Open in {VSCODENAME}",
            tip="Opens the selected files with VSCode",
        )
        item.connect("activate", self.launch_vscode, paths)
        items.append(item)

        dirs = [p for p in paths if p.is_dir()]
        if len(dirs) <= 1:
            reuse_item = Nautilus.MenuItem(
                name="VSCodeOpenReuse",
                label=f"Open in Active {VSCODENAME} Window",
                tip="Opens the selected files in the active VSCode window",
            )
            reuse_item.connect("activate", self.launch_vscode_reuse, paths)
            items.append(reuse_item)

        if len(paths) == 1:
            devcontainer_item = self._devcontainer_item("VSCodeOpenDevContainer", paths[0])
            if devcontainer_item:
                items.append(devcontainer_item)

        return items

    # nautilus-python passes (file,) or (window, file) depending on API version;
    # args[-1] is always the current directory file object.
    def get_background_items(self, *args):
        current_dir = args[-1]
        filepath = Path(current_dir.get_location().get_path())
        paths = [filepath]
        items = []
        item = Nautilus.MenuItem(
            name="VSCodeOpenBackground",
            label=f"Open in {VSCODENAME}",
            tip="Opens the current directory in VSCode",
        )
        item.connect("activate", self.launch_vscode, paths)
        items.append(item)

        reuse_item = Nautilus.MenuItem(
            name="VSCodeOpenBackgroundReuse",
            label=f"Open in Active {VSCODENAME} Window",
            tip="Opens the current directory in the active VSCode window",
        )
        reuse_item.connect("activate", self.launch_vscode_reuse, paths)
        items.append(reuse_item)

        devcontainer_item = self._devcontainer_item("VSCodeOpenDevContainerBackground", filepath)
        if devcontainer_item:
            items.append(devcontainer_item)

        return items