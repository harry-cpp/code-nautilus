# code-nautilus

This repo provides a visual studio code extension for Nautilus.

## Install Extension

```
wget -qO- https://raw.githubusercontent.com/harry-cpp/code-nautilus/master/install.sh | bash
```

If you are using Ubuntu 22.04 LTS, you must also install python3-nautilus

```
sudo apt install python3-nautilus
```

and restart Gnome or restart Nautilus

```
nautilus -q && nautilus &
```

## Uninstall Extension

```
rm -f ~/.local/share/nautilus-python/extensions/code-nautilus.py
```
