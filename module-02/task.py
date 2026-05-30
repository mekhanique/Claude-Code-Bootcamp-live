#!/usr/bin/env python3
"""Single-file CLI task manager. Persists to tasks.json in CWD."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASKS_FILE = Path("tasks.json")


def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    try:
        data = json.loads(TASKS_FILE.read_text())
        if not isinstance(data, list):
            raise ValueError("tasks.json must contain a JSON array")
        return data
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"error: tasks.json is corrupt: {exc}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: cannot read tasks.json: {exc}", file=sys.stderr)
        sys.exit(2)


def save_tasks(tasks: list[dict]) -> None:
    try:
        TASKS_FILE.write_text(json.dumps(tasks, indent=2) + "\n")
    except OSError as exc:
        print(f"error: cannot write tasks.json: {exc}", file=sys.stderr)
        sys.exit(2)


def next_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


def cmd_add(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "status": "todo",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "text": args.text,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {task['text']}")


def cmd_list(_args: argparse.Namespace) -> None:
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return

    id_w = max(max(len(str(t["id"])) for t in tasks), 2)
    status_w = max(max(len(t["status"]) for t in tasks), 6)
    created_w = 20  # "YYYY-MM-DDTHH:MM:SSZ"

    def row(id_val: str, status: str, created: str, text: str) -> str:
        return (
            f"{id_val:<{id_w}}  "
            f"{status:<{status_w}}  "
            f"{created:<{created_w}}  "
            f"{text}"
        )

    header = row("ID", "Status", "Created At", "Text")
    print(header)
    print("-" * len(header))
    for t in tasks:
        print(row(str(t["id"]), t["status"], t["created_at"], t["text"]))


def cmd_done(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            if task["status"] == "done":
                print(f"Task #{args.id} is already done.")
                return
            task["status"] = "done"
            save_tasks(tasks)
            print(f"Marked #{args.id} as done")
            return
    print(f"No task with id {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    remaining = [t for t in tasks if t["id"] != args.id]
    if len(remaining) == len(tasks):
        print(f"No task with id {args.id}", file=sys.stderr)
        sys.exit(1)
    save_tasks(remaining)
    print(f"Deleted task #{args.id}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="task",
        description="Manage TODOs from the terminal. Data stored in ./tasks.json.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("text", help='Task description, e.g. "Write the spec"')

    sub.add_parser("list", help="List all tasks")

    done_p = sub.add_parser("done", help="Mark a task as done")
    done_p.add_argument("id", type=int, metavar="ID", help="Task id")

    del_p = sub.add_parser("delete", help="Delete a task")
    del_p.add_argument("id", type=int, metavar="ID", help="Task id")

    dispatch = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "delete": cmd_delete,
    }

    args = parser.parse_args()
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
