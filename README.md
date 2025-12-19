# code-nautilus

This repo provides a visual studio code extension for Nautilus.

## Install Extension

```
wget -qO- https://raw.githubusercontent.com/harry-cpp/code-nautilus/master/install.sh | bash
```

During the install process you will be prompted to choose whether you want to register the stable `code` binary, `code-insiders`, or both inside Nautilus. Your choices are stored in `~/.config/code-nautilus/targets.conf`, so you can rerun the installer any time to update them.

## Local Installation (for development)

If you want to install from a local copy (for testing changes or contributing):

```bash
# Clone the repository
git clone https://github.com/harry-cpp/code-nautilus.git
cd code-nautilus

# Install using local files
bash install.sh --local
```

The `--local` (or `-l`) flag tells the installer to use your local `code-nautilus.py` file instead of downloading from GitHub. This is useful when:

- Testing local changes before contributing
- Developing new features
- Running the extension from a forked repository

## Uninstall Extension

```
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py
```
