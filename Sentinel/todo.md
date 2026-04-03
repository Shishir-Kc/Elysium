# Sentinel TODO

## New Feature: Auto-Restore from Backup

- [ ] Add `restore_from_backup()` method to restore root files from `Elysium_back_up`
- [ ] Modify `watch()` to trigger restore when file changes detected
- [ ] Add configurable restore targets (which files to restore)
- [ ] Add `restart_server()` method to restart FastAPI after restore

## Additional Feature Suggestions

### High Priority
- [ ] Add notification alerts (email/Discord webhook) when changes detected
- [ ] Add backup versioning with timestamps instead of single backup
- [ ] Add graceful server restart after restore

### Medium Priority
- [ ] Add selective restore (only restore specific files, not all changes)
- [ ] Add exclusion patterns (regex for files that shouldn't trigger restore)
- [ ] Add change audit log (log what changed, when, allow rollback to version)

### Low Priority
- [ ] Add dry-run mode (test restore without modifying files)
- [ ] Add configuration file for Sentinel settings (restore targets, watch intervals, etc.)

## Bugs

- [ ] Fix `logo()` path — `assets/Watcher/eye.txt` doesn't exist
- [ ] Fix `for...else` in `create_hash()` — `else` block on for loop still runs after exceptions

## Dead Code

- [x] ~~Remove unused `hasher` class attribute from `__init__`~~
- [x] ~~Remove `look_dir()` method~~
- [x] ~~Remove leftover debug comments~~
- [x] ~~Remove `sys.path.append` hack~~ (wontfix — standalone tool)

## Improvements

- [ ] Replace `print()` with proper logging (`server_logging.py`)
- [ ] Add type hints to all methods
- [ ] Rename `Changed_files` to `changed_files` (snake_case)
- [ ] Make watch interval configurable instead of hardcoded `time.sleep(5)`
- [ ] Convert `ignore.json` from numbered keys to a JSON array
- [ ] Add missing ignore entries: `.env`, `uv.lock`, `.venv`
