# Coding Style Guide

Canonical style reference for all Client projects. Every new project should clone this template and keep this file updated.

---

## Referenced Standards

- **.editorconfig** - Editor formatting rules
- **.gitignore** - Version control ignore patterns
- **Error Prevention Checklist** - See AGENTS.MD section 10

---

## 1. Python Naming and Formatting

### Naming Conventions
- Files: lowercase with underscores `my_file.py`
- Classes: PascalCase `MyClass`
- Functions: snake_case `my_function()`
- Constants: UPPER_SNAKE_CASE
- Private methods: `_leading_underscore()`
- Config paths: `~/.config/<app-name>/config.json`

### Code Organization
- Maximum line length: 100 characters
- Use 4 spaces for indentation (never tabs)
- Sort imports: stdlib, then third-party, then local, alphabetically within groups
- One class per file for large classes; small utilities may share a module
- Keep `src/` for source, `docs/` for documentation, `scripts/` for helpers, `tests/` for tests

### Documentation
- Use docstrings for public APIs
- Comment complex logic (see ~/code-comments.md)
- Keep docs in `docs/` folder, not in `src/`
- Every project must have: `docs/Lessons_learned.md`, `docs/Changelog.md`, `Readme.md`

### Language
- Primary: English
- Secondary: Danish (-dk versions when needed)

---

## 2. GUI Framework Selection

### Decision Matrix

| Complexity | Tabs | Background Work | Framework | Rationale |
|---|---|---|---|---|
| Form / calculator (<500 lines) | 0-1 | No | **customtkinter** | Fastest to write, dark theme built-in |
| Dashboard / monitor (500-2000 lines) | 2-4 | Light threading | **customtkinter** | Good balance of features and simplicity |
| Complex multi-tab app (2000+ lines) | 5+ | Heavy workers | **PyQt6** | Modular tab architecture, signal/slot, proper threading |
| Web-native look needed | any | any | **React + Tauri** | Only when web UI is required |

### Existing Project Reference

| Framework | Projects | Use When |
|---|---|---|
| **customtkinter** | car-ownership, yearly-budget, solar-roi, drive-encrypter, password-auditor, credentials-manager, mac-changer, fisheye-gui, duplicate-sorter | Simple to moderate GUI, fast iteration |
| **PyQt6** | portfolio-optimizer-pro, server-services-sync | Complex apps needing modularity, worker threads, system tray |
| **PyQt5** | morning-news, manga-updater | Legacy or when PyQt5 is already available |
| **plain tkinter** | rsync-gui, house-roi, file-ai | Minimal UI or single-file constraint |

### When to Upgrade from CTk to PyQt
- More than 4 tabs needed
- Background workers emit progress frequently (more than 1/sec)
- Need system tray integration
- Multiple independent data sources refreshing concurrently
- Need dock widgets or complex layouts (splitters, dock areas)

---

## 3. GUI Architecture

### Main Window Pattern

**CTk apps:**
```python
class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("App Name")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        pass

    def _load_config(self):
        pass

    def _save_config(self):
        pass
```

**PyQt6 apps:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Name")
        self.resize(900, 600)
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(DashboardTab(), "Dashboard")
        tabs.addTab(SettingsTab(), "Settings")
        self.setCentralWidget(tabs)
```

### File Organization (PyQt6)
- `src/main.py` - entry point (under 300 lines)
- `src/ui/main_window.py` - MainWindow class
- `src/ui/<tab_name>.py` - one file per tab
- `src/workers.py` - QThread worker classes
- `src/config.py` - config loading/saving
- `src/<domain>.py` - business logic

### File Organization (CTk)
- `main.py` or `gui.py` - single file if under 1500 lines
- `src/<domain>.py` - business logic separated
- `lib/` - reusable engine/utils if complex

---

## 4. Theme and Dark Mode

### CTk Standard
```python
# At module top (runs once at startup)
ctk.set_appearance_mode("dark")     # "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
```

### Runtime Theme Switching
- CTk: `ctk.set_appearance_mode()` is live-switchable; `set_default_color_theme()` only affects new widgets
- PyQt: Swap full stylesheet string (see manga-updater's STYLE_DARK/STYLE_LIGHT pattern)
- Persist choice in config.json: `"theme": "dark"`

### PyQt Stylesheet Convention
Define as constants in a central location. Example styles: QMainWindow background `#1e1e1e`, QTabWidget pane border `1px solid #333`, QTableWidget background `#252525` with text `#ddd` and gridline `#333`.

### Color Palette (when manual)
```
bg_dark:    #1e1e1e
bg_medium:  #2d2d2d
bg_light:   #333333
text:       #dddddd
accent:     #0078d4
success:    #4caf50
warning:    #ff9800
error:      #f44336
```

---

## 5. Threading Patterns

### PyQt Workers
```python
class Worker(QThread):
    progress = pyqtSignal(int, str)   # (percent, message)
    finished = pyqtSignal(bool, str)  # (success, message)
    error = pyqtSignal(str)           # error message

    def run(self):
        try:
            self.finished.emit(True, "Done")
        except Exception as e:
            self.error.emit(str(e))
```

### CTk/tkinter Threading
```python
def _start_background(self):
    thread = threading.Thread(target=self._do_work, daemon=True)
    thread.start()

def _do_work(self):
    try:
        result = heavy_operation()
        self.after(0, lambda: self._update_ui(result))
    except Exception as e:
        self.after(0, lambda: self._show_error(str(e)))

def _safe_ui(self, callback):
    if threading.current_thread() is threading.main_thread():
        callback()
    else:
        self.after(0, callback)
```

### Rules
- **Never** update GUI widgets from a background thread
- **Always** use `daemon=True` for threads
- **Always** handle errors in worker threads
- **Always** re-enable buttons in both success AND failure paths
- **Prefer** QTimer for periodic refresh (PyQt)
- **Prefer** `self.after(ms, callback)` for delayed/polling work (CTk/tkinter)

---

## 6. Configuration and Persistence

### Config Location
```python
CONFIG_DIR = Path.home() / ".config" / "<app-name>"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
```

### Config Load/Save Pattern
```python
DEFAULTS = {"theme": "dark", "refresh_interval": 30}

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                user = json.load(f)
            return {**DEFAULTS, **user}
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULTS.copy()

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
```

### When to Use What
| Storage | Use For | Example |
|---|---|---|
| `config.json` | User preferences, theme, paths | Dark mode, log paths, refresh interval |
| SQLite DB | Structured data, history, caches | Portfolio holdings, scan results, price cache |
| `QSettings` | Window geometry, splitter positions | Auto-restore layout on reopen (PyQt only) |
| Log files | Audit trail, debug history | `~/.synced/<name>.log` |

---

## 7. Error Handling

### GUI Error Display Tiers

**Tier 1 - Status label** (non-critical):
```python
self.status_label.setText("Last sync: 2 min ago")
self.status_label.setStyleSheet("color: #4caf50;")
```

**Tier 2 - Toast/notification** (operation failed):
```python
self.statusBar().showMessage("Sync failed - check logs", 5000)
# CTk:
self.after(5000, lambda: self.status_label.setText(""))
```

**Tier 3 - Dialog** (data loss risk):
```python
QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
# or
messagebox.showerror("Error", f"Failed to save:\n{e}")
```

### Error Handling Rules
- Every try/except must have a purpose (do not catch-and-ignore)
- Buttons that start operations must be re-enabled in both success AND failure paths
- Background worker errors must be caught and surfaced to the UI
- Use `@log_errors(context)` decorator for non-critical operations
- Log the full traceback for debugging, show friendly message to user

### Log Prefix Convention (CTk log textboxes)
```
[i] Information message
[*] Success message
[!] Error/warning message
```

---

## 8. Logging

### Minimum Standard
```python
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
```

### Production Standard (for daemons/services)
```python
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = Path.home() / ".local" / "share" / "<app>"
LOG_DIR.mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=3,
)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logging.getLogger().addHandler(handler)
```

### Rules
- **Never** use bare print() in production code - use logging
- **Always** silence noisy third-party loggers
- Log files: `~/.synced/<name>.log` for sync scripts, `~/.local/share/<app>/` for GUI apps
- Rotate logs (10MB max, 3 backups) for long-running services

---

## 9. Data Display and Progress

### Rules
- **Never** use random/dummy/mock data in production code. If real data is unavailable, show "No data" or disable the widget.
- Use `rsync --info=progress2` for progress parsing (not --progress which is per-file only)
- Read real system data when available: `/proc/net/dev` for network, `nvidia-smi` for GPU, `df` for disk
- Show units with numbers: `1.2 MB/s`, `45%`, `ETA 8m` - never raw bytes without context
- For progress bars, use indeterminate mode when percentage is unknown

### Tables and Trees
- Define column headers once and document column order in a comment
- Use consistent column indices across all setItem(row, col, ...) calls
- For sortable tables, store data in a list-of-dicts and sort before display

---

## 10. Launch Scripts

### Standard Pattern
```bash
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

exec python3 src/main.py "$@"
```

### Rules
- Always cd to script directory first
- Auto-create venv if missing
- Auto-reinstall if requirements.txt is newer than venv
- Use exec to replace shell process
- Use "$@" to pass through CLI arguments

---

## 11. Git and Version Control

### Commit Messages
- Use conventional format: `type(scope): description`
- Types: feat, fix, docs, refactor, test, chore
- Scope: project name or module (optional)
- Example: `feat(seagate-sync): add progress2 parsing for live sync tracking`

### Pre-commit Checklist
- [ ] `python -m py_compile` passes on all changed files
- [ ] `bash -n` passes on all changed shell scripts
- [ ] No hardcoded secrets or API keys
- [ ] Config paths use `~/.config/<app>/` convention
- [ ] Error handling exists for all background operations

---

## 12. Anti-Patterns to Avoid

### Code Quality
- **Dummy data in production**: Never use random.random() for UI display. Use real system data or show "N/A".
- **Catch-and-ignore**: Every except must log or surface the error somehow
- **Missing self. prefix**: Widget referenced later must use self.widget_name in __init__
- **Unreachable code**: Code after return or break is dead code
- **Missing import after feature addition**: When adding methods that use new modules, verify imports at top of file

### Data and Sync
- **Schema drift between machines**: When syncing data between hosts, verify both sides use the same DB schema. Document which host is authoritative.
- **Missing progress flags**: Always add --info=progress2 to rsync when you need progress parsing
- **Log file conventions**: Use `~/.synced/<name>.log` for shell scripts, `~/.local/share/<app>/` for GUI apps

### GUI
- **Updating widgets from threads**: Always marshal back to main thread via .after() or signals
- **Forgetting button re-enable**: If a button starts an operation, it must be re-enabled in both success and failure paths
- **Hardcoded geometry**: Use self.geometry("900x600") then let user resize; save/restore with QSettings or config
- **No error feedback**: If an operation fails silently, the user has no way to know

### AI-Assisted Development
- **Trusting AI output without verification**: Always run py_compile, bash -n, and manual testing
- **Replacing real data with placeholders**: If AI generates mock data, replace it with real data
- **Skipping error handling**: AI often writes try/except with pass - replace with proper logging or surfacing

---

## 13. Systemd Timers and Network Patterns

### Timer/Service Conventions
- Use `Type=oneshot` for sync scripts (run once, exit)
- Set `TimeoutStartSec=7200` for large rsync operations (default 90s kills mid-transfer)
- Use `--no-block` when triggering from GUI: `systemctl --user start <service> --no-block`
- Check status via stdout string, not exit code: `systemctl --user is-active` returns rc=3 for "activating"
- Timer name may differ from service name — document the mapping in config

### LAN/Tailscale Fallback Pattern
A script that reaches a machine on another network should try one route and fall
back to the other, rather than failing outright when the direct route is down.

```bash
REMOTE_LAN="192.0.2.10"
REMOTE_TAILSCALE="192.0.2.10"

detect_remote() {
    if ping -c 1 -W 2 "$REMOTE_LAN" 2>/dev/null | grep -q "1 received"; then
        echo "$REMOTE_LAN"; return 0
    fi
    if ping -c 1 -W 3 "$REMOTE_TAILSCALE" 2>/dev/null | grep -q "1 received"; then
        echo "$REMOTE_TAILSCALE"; return 0
    fi
    return 1
}
```

- The addresses above are from 192.0.2.0/24 (TEST-NET-1), reserved for
  documentation and not routable. Read both from your own config rather than
  hard-coding them.
- A full-tunnel VPN client will normally blackhole the local subnet, which is the
  usual reason the direct route fails while an overlay route still works. Check
  that before concluding the remote machine is down.
- Keep the probe in one shared `common.sh` so every script uses the same order and
  the same timeouts. Divergence between scripts is how this pattern goes wrong.

### Log File Conventions
- Shell scripts: `~/.synced/<name>.log` or `~/.<app>/<name>.log`
- GUI apps: `~/.local/share/<app>/` or `~/.config/<app>/logs/`
- Always use `tee -a` to write to both journal and log file
- Include timestamps in log entries for debugging
