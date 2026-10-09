#!/usr/bin/env bash
# Fetch the two datasets. Neither is redistributed in this repository;
# see data/README.md for the licence reasons.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data && cd data

if [ ! -d ml-1m ]; then
  echo "==> MovieLens 1M"
  curl -fL -o ml-1m.zip https://files.grouplens.org/datasets/movielens/ml-1m.zip
  unzip -q ml-1m.zip && rm ml-1m.zip
else
  echo "==> MovieLens 1M already present"
fi

if [ ! -d frappe ]; then
  echo "==> Frappe"
  mkdir -p frappe && cd frappe
  curl -fL -o frappe.zip https://www.baltrunas.info/context-aware/frappe/frappe.zip
  unzip -q frappe.zip && rm frappe.zip
  cd ..
else
  echo "==> Frappe already present"
fi

echo
echo "Expected layout:"
echo "  data/ml-1m/{ratings,users,movies}.dat"
echo "  data/frappe/Mobile_Frappe/frappe/frappe.csv"
echo
ls -d ml-1m frappe 2>/dev/null || true
