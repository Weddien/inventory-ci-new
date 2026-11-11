#!/usr/bin/env python3
"""Учет устройств: добавление, просмотр и поиск по серийному номеру."""
import argparse
import json
import sys
from pathlib import Path


def load_inventory(path):
    p = Path(path)
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Файл учета должен содержать JSON-список")
    return data


def save_inventory(path, items):
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_device(items, name, serial):
    name = name.strip()
    serial = serial.strip().upper()
    if not name:
        raise ValueError("Название устройства не может быть пустым")
    if not serial:
        raise ValueError("Серийный номер не может быть пустым")
    if any(item["serial"] == serial for item in items):
        raise ValueError("Серийный номер уже существует: " + serial)
    items.append({"name": name, "serial": serial})
    return items


def find_device(items, serial):
    serial = serial.strip().upper()
    for item in items:
        if item["serial"] == serial:
            return item
    return None


def build_parser():
    parser = argparse.ArgumentParser(description="Учет устройств")
    parser.add_argument("--file", default="inventory.json",
                        help="путь к JSON-файлу учета")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="добавить устройство")
    add.add_argument("--name", required=True)
    add.add_argument("--serial", required=True)
    sub.add_parser("list", help="показать все устройства")
    find = sub.add_parser("find", help="найти устройство по серийному номеру")
    find.add_argument("--serial", required=True)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        items = load_inventory(args.file)
        if args.command == "add":
            add_device(items, args.name, args.serial)
            save_inventory(args.file, items)
            print("Добавлено:", args.serial.strip().upper())
        elif args.command == "list":
            for item in items:
                print(item["serial"], item["name"])
        elif args.command == "find":
            item = find_device(items, args.serial)
            if item is None:
                print("Не найдено", file=sys.stderr)
                return 1
            print(item["serial"], item["name"])
    except (ValueError, json.JSONDecodeError) as exc:
        print("Ошибка:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
