#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$HOME/.local/bin" "$HOME/.local/lib/speechy1"
install -m 755 "$root/speechy1.py" "$HOME/.local/lib/speechy1/speechy1.py"
cat > "$HOME/.local/bin/speechy1" <<'EOF'
#!/bin/sh
exec /usr/bin/python3 -B "$HOME/.local/lib/speechy1/speechy1.py" "$@"
EOF
chmod 755 "$HOME/.local/bin/speechy1"
if [ -d /usr/share/omarchy/shell ]; then
  plugin="$HOME/.config/omarchy/plugins/rohan.speechy1-indicator"
  mkdir -p "$plugin"
  install -m 644 "$root/omarchy/Indicator.qml" "$root/omarchy/manifest.json" "$plugin/"
fi
printf 'Installed speechy1. Run speechy1 setup, then install your desktop shortcut adapter.\n'
