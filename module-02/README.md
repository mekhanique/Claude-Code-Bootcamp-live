# task — CLI Task Manager

A single-file terminal task manager. Tasks persist to `tasks.json` in whatever directory you run the command from.

## Requirements

Python 3.11+ (no third-party packages).

## Install

```bash
# Make the script executable and put it on your PATH
chmod +x task.py
ln -s "$(pwd)/task.py" /usr/local/bin/task
```

Or run it directly without installing:

```bash
python3 task.py <command> [args]
```

## Commands

| Command | Description | Example |
|---|---|---|
| `task add "<text>"` | Add a new task | `task add "Write the spec"` |
| `task list` | List all tasks (id, status, created_at, text) | `task list` |
| `task done <id>` | Mark a task as done | `task done 1` |
| `task delete <id>` | Delete a task permanently | `task delete 1` |

## Example session

```
$ task add "Write the spec"
Added task #1: Write the spec

$ task add "Review PR #42"
Added task #2: Review PR #42

$ task list
ID  Status  Created At            Text
------------------------------------------
1   todo    2026-05-30T10:00:00Z  Write the spec
2   todo    2026-05-30T10:00:05Z  Review PR #42

$ task done 1
Marked #1 as done

$ task delete 99
No task with id 99          # exit code 1
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | User error (task not found, bad arguments) |
| `2` | Internal error (corrupt or unreadable `tasks.json`) |
