#!/usr/bin/env bash
# Fix slow/broken apt on Iranian VPS (DNS + local Ubuntu mirror).
# Run: sudo bash deploy/fix-apt-iran.sh
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/fix-apt-iran.sh"
  exit 1
fi

echo "==> Configuring DNS (Shekan + fallback)..."
mkdir -p /etc/systemd/resolved.conf.d
cat > /etc/systemd/resolved.conf.d/dns.conf <<'EOF'
[Resolve]
DNS=178.22.122.100 185.51.200.2
FallbackDNS=94.140.14.14 8.8.8.8
EOF
systemctl restart systemd-resolved
resolvectl flush-caches 2>/dev/null || true

echo "==> Switching apt to Arvan mirror..."
SOURCES_DEB822=/etc/apt/sources.list.d/ubuntu.sources
SOURCES_LIST=/etc/apt/sources.list

if [[ -f "${SOURCES_DEB822}" ]]; then
  sed -i \
    -e 's|http://archive.ubuntu.com/ubuntu|http://mirror.arvancloud.ir/ubuntu|g' \
    -e 's|http://security.ubuntu.com/ubuntu|http://mirror.arvancloud.ir/ubuntu|g' \
    "${SOURCES_DEB822}"
elif [[ -f "${SOURCES_LIST}" ]]; then
  sed -i \
    -e 's|http://archive.ubuntu.com/ubuntu|http://mirror.arvancloud.ir/ubuntu|g' \
    -e 's|http://security.ubuntu.com/ubuntu|http://mirror.arvancloud.ir/ubuntu|g' \
    "${SOURCES_LIST}"
else
  echo "No apt sources file found."
  exit 1
fi

echo "==> Testing DNS..."
getent hosts mirror.arvancloud.ir || { echo "DNS still failing for mirror.arvancloud.ir"; exit 1; }

echo "==> apt update..."
apt-get update

echo "Done. Now run: sudo apt-get install -y postgresql nginx python3-venv python3-pip certbot python3-certbot-nginx"
