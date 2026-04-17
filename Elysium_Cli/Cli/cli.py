"""
Elysium TUI — Beautiful Home Agent Dashboard
Built with Textual (modern Python TUI framework)
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
import platform
import shutil
import time
import threading
from datetime import datetime
from pathlib import Path

import httpx
from rich.markup import escape
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.content import Content
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    ProgressBar,
    RichLog,
    Rule,
    Static,
    TextArea,
    ContentSwitcher,
    Select,
)


# ═════════════════════════════════════════════════════════════════
#  PROCESS MANAGER — manages subprocesses for services
# ═════════════════════════════════════════════════════════════════
class ProcessManager:
    """Manages background service subprocesses."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self._processes: dict[str, subprocess.Popen] = {}
        self._readers: dict[str, threading.Thread] = {}
        self._log_callbacks: dict[str, list] = {}
        self._stop_events: dict[str, threading.Event] = {}

    @property
    def running(self) -> dict[str, bool]:
        """Return dict of service_name -> is_running."""
        result = {}
        for name, proc in self._processes.items():
            result[name] = proc.poll() is None
        return result

    def is_running(self, name: str) -> bool:
        proc = self._processes.get(name)
        return proc is not None and proc.poll() is None

    def register_log_callback(self, name: str, callback) -> None:
        """Register a callback(line: str) for a service's output."""
        self._log_callbacks.setdefault(name, []).append(callback)

    def start_service(
        self,
        name: str,
        cmd: list[str],
        env: dict[str, str] | None = None,
    ) -> bool:
        """Start a service subprocess. Returns True if started successfully."""
        if self.is_running(name):
            return False  # already running

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(self.project_root),
                env=merged_env,
                preexec_fn=os.setsid,  # create process group for clean kill
            )
            self._processes[name] = proc

            # Start a reader thread for stdout
            stop_event = threading.Event()
            self._stop_events[name] = stop_event
            reader = threading.Thread(
                target=self._read_output,
                args=(name, proc, stop_event),
                daemon=True,
            )
            self._readers[name] = reader
            reader.start()
            return True

        except Exception:
            return False

    def stop_service(self, name: str) -> bool:
        """Stop a running service. Returns True if stopped."""
        proc = self._processes.get(name)
        if proc is None or proc.poll() is not None:
            return False

        # Signal the reader to stop
        stop_event = self._stop_events.get(name)
        if stop_event:
            stop_event.set()

        try:
            # Kill the entire process group
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                proc.wait(timeout=3)
        except (ProcessLookupError, OSError):
            pass

        return True

    def get_pid(self, name: str) -> int | None:
        proc = self._processes.get(name)
        if proc and proc.poll() is None:
            return proc.pid
        return None

    def get_return_code(self, name: str) -> int | None:
        proc = self._processes.get(name)
        if proc:
            return proc.poll()
        return None

    def stop_all(self) -> None:
        for name in list(self._processes.keys()):
            self.stop_service(name)

    def _read_output(
        self,
        name: str,
        proc: subprocess.Popen,
        stop_event: threading.Event,
    ) -> None:
        """Read stdout/stderr line-by-line and dispatch to callbacks."""
        try:
            for raw_line in iter(proc.stdout.readline, b""):
                if stop_event.is_set():
                    break
                line = raw_line.decode("utf-8", errors="replace").rstrip()
                for cb in self._log_callbacks.get(name, []):
                    try:
                        cb(line)
                    except Exception:
                        pass
        except Exception:
            pass

# ── Project root ─────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ELYSIUM_BASE_URL = os.environ.get("ELYSIUM_URL", "http://localhost:8000")

# ── ASCII Logo ───────────────────────────────────────────────────
LOGO = r"""
[bold #b48ead] /$$$$$$$$ /$$                     /$$
| $$_____/| $$                    |__/
| $$      | $$ /$$   /$$  /$$$$$$$ /$$ /$$   /$$ /$$$$$$/$$$$/$$
| $$$$$   | $$| $$  | $$ /$$_____/| $$| $$  | $$| $$_  $$_  $$
| $$__/   | $$| $$  | $$|  $$$$$$ | $$| $$  | $$| $$ \ $$ \ $$
| $$      | $$| $$  | $$ \____  $$| $$| $$  | $$| $$ | $$ | $$
| $$$$$$$$| $$|  $$$$$$$ /$$$$$$$/| $$|  $$$$$$/| $$ | $$ | $$
|________/|__/ \____  $$|_______/ |__/ \______/ |__/ |__/ |__/
               /$$  | $$
              |  $$$$$$/
               \______/[/]
"""


# ═════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═════════════════════════════════════════════════════════════════
class Sidebar(Container):
    """Sidebar navigation panel."""

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold #b48ead]⟐[/] [bold #81a1c1]ELYSIUM[/]",
            id="sidebar-title",
        )
        yield Rule()
        with Vertical(id="nav-list"):
            yield Button("🏠  Dashboard", id="nav-dashboard", classes="nav-btn -active")
            yield Button("🤖  AI Agent", id="nav-chat", classes="nav-btn")
            yield Button("📧  Email", id="nav-email", classes="nav-btn")
            yield Button("⚙️  Services", id="nav-services", classes="nav-btn")
            yield Button("📋  Logs", id="nav-logs", classes="nav-btn")
            yield Button("🛡️  Sentinel", id="nav-sentinel", classes="nav-btn")
        yield Rule()
        yield Static(
            "[dim #616e88]v0.1.0 · Home Agent[/]",
            id="sidebar-version",
        )


# ═════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ═════════════════════════════════════════════════════════════════
class DashboardPage(Container):
    """Main dashboard with system metrics and status overview."""

    def compose(self) -> ComposeResult:
        yield Static(LOGO, id="logo-display")
        with Container(classes="dashboard-grid"):
            # ── Server Status ──
            with Vertical(classes="status-panel"):
                yield Static("[bold #81a1c1]🖥  SERVER STATUS[/]", classes="panel-title")
                yield Rule()
                yield Static("", id="server-status-content")

            # ── System Info ──
            with Vertical(classes="status-panel"):
                yield Static("[bold #81a1c1]📊  SYSTEM INFO[/]", classes="panel-title")
                yield Rule()
                yield Static("", id="system-info-content")

            # ── Services Overview ──
            with Vertical(classes="status-panel"):
                yield Static("[bold #81a1c1]⚡  SERVICES[/]", classes="panel-title")
                yield Rule()
                yield Static("", id="services-overview-content")

            # ── Quick Stats ──
            with Vertical(classes="status-panel"):
                yield Static("[bold #81a1c1]📈  QUICK STATS[/]", classes="panel-title")
                yield Rule()
                yield Static("", id="quick-stats-content")


# ═════════════════════════════════════════════════════════════════
#  AI CHAT PAGE
# ═════════════════════════════════════════════════════════════════
class ChatPage(Container):
    """Interactive AI agent chat interface."""

    def compose(self) -> ComposeResult:
        with Vertical(id="chat-container"):
            with Horizontal(id="chat-header"):
                with Vertical(classes="panel-title-container"):
                    yield Static(
                        "[bold #81a1c1]🤖  ELYSIUM AI AGENT[/]  "
                        "[dim]— memory enabled[/]",
                        classes="panel-title",
                    )
                yield Select([], id="model-select", prompt="Loading models...")
                yield Button("🗑 Clear", id="clear-chat-btn", classes="chat-clear-btn")
            yield Rule()
            yield RichLog(
                id="chat-log",
                highlight=True,
                markup=True,
                wrap=True,
                auto_scroll=True,
            )
            with Horizontal(id="chat-input-bar"):
                ta = TextArea(
                    id="chat-input",
                    show_line_numbers=False,
                )
                yield ta
                yield Button("Send ›", id="send-btn", variant="primary")


# ═════════════════════════════════════════════════════════════════
#  EMAIL PAGE
# ═════════════════════════════════════════════════════════════════
class EmailPage(Container):
    """Email sending interface."""

    def compose(self) -> ComposeResult:
        with Vertical(id="email-container"):
            yield Static(
                "[bold #81a1c1]📧  SEND EMAIL[/]  [dim]— via Celery workers[/]",
                classes="panel-title",
            )
            yield Rule()
            with Vertical(classes="email-field"):
                yield Label("To:")
                yield Input(placeholder="recipient@example.com", id="email-to")
            with Vertical(classes="email-field"):
                yield Label("Subject:")
                yield Input(placeholder="Email subject", id="email-subject")
            yield Label("Body:", classes="email-field")
            yield TextArea(id="email-body")
            yield Button(
                "⚡ Send Email",
                id="send-email-btn",
                variant="success",
            )


# ═════════════════════════════════════════════════════════════════
#  SERVICES PAGE — with process controls
# ═════════════════════════════════════════════════════════════════
class ServicesPage(Container):
    """Service management panel with start/stop controls."""

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold #81a1c1]⚙️  SERVICES[/]  [dim]— manage Elysium services[/]",
            classes="panel-title",
        )
        yield Rule()

        # ── Control Buttons ──
        with Horizontal(classes="svc-controls"):
            yield Button("▶  Start Server", id="svc-start-fastapi", classes="svc-btn svc-start")
            yield Button("⏹  Stop Server", id="svc-stop-fastapi", classes="svc-btn svc-stop")
            yield Button("🔄  Restart Server", id="svc-restart-fastapi", classes="svc-btn svc-restart")
        with Horizontal(classes="svc-controls"):
            yield Button("▶  Start Celery", id="svc-start-celery", classes="svc-btn svc-start")
            yield Button("⏹  Stop Celery", id="svc-stop-celery", classes="svc-btn svc-stop")
            yield Button("▶  Start Sentinel", id="svc-start-sentinel", classes="svc-btn svc-start")
            yield Button("⏹  Stop Sentinel", id="svc-stop-sentinel", classes="svc-btn svc-stop")
        with Horizontal(classes="svc-controls"):
            yield Button("▶  Start Valkey", id="svc-start-valkey", classes="svc-btn svc-start")
            yield Button("⏹  Stop Valkey", id="svc-stop-valkey", classes="svc-btn svc-stop")

        yield Rule()
        yield Static("", id="svc-status-bar")
        yield Rule()

        # ── Status Table ──
        table = DataTable(id="services-table")
        table.cursor_type = "row"
        yield table

        yield Rule()
        yield Static(
            "[bold #81a1c1]📟  LIVE OUTPUT[/]  [dim]— service process logs[/]",
            classes="panel-title",
        )
        yield RichLog(id="svc-live-log", highlight=True, markup=True, wrap=True, auto_scroll=True)


# ═════════════════════════════════════════════════════════════════
#  LOGS PAGE
# ═════════════════════════════════════════════════════════════════
class LogsPage(Container):
    """Live log viewer."""

    def compose(self) -> ComposeResult:
        with Vertical(id="logs-container"):
            yield Static(
                "[bold #81a1c1]📋  LOGS[/]  [dim]— live server output[/]",
                classes="panel-title",
            )
            yield Rule()
            with Horizontal():
                yield Button("All", id="log-all", classes="nav-btn")
                yield Button("Elysium", id="log-elysium", classes="nav-btn")
                yield Button("Hyper", id="log-hyper", classes="nav-btn")
            yield RichLog(id="log-output", highlight=True, markup=True, wrap=True, auto_scroll=True)


# ═════════════════════════════════════════════════════════════════
#  SENTINEL PAGE
# ═════════════════════════════════════════════════════════════════
class SentinelPage(Container):
    """Sentinel file integrity dashboard."""

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold #81a1c1]🛡️  SENTINEL[/]  [dim]— file integrity monitor[/]",
            classes="panel-title",
        )
        yield Rule()
        yield Static("", id="sentinel-info")
        yield Rule()
        yield DataTable(id="sentinel-table")


# ═════════════════════════════════════════════════════════════════
#  MAIN APP
# ═════════════════════════════════════════════════════════════════
class ElysiumApp(App):
    """Elysium — Beautiful Home Agent TUI."""

    CSS_PATH = "styles.tcss"
    TITLE = "Elysium"
    SUB_TITLE = "Home Agent"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("d", "switch_page('dashboard')", "Dashboard", show=True),
        Binding("a", "switch_page('chat')", "AI Chat", show=True),
        Binding("e", "switch_page('email')", "Email", show=True),
        Binding("s", "switch_page('services')", "Services", show=True),
        Binding("l", "switch_page('logs')", "Logs", show=True),
        Binding("w", "switch_page('sentinel')", "Sentinel", show=True),
        Binding("r", "refresh_dashboard", "Refresh", show=True),
        Binding("f5", "start_server", "Start Server", show=False),
        Binding("f6", "stop_server", "Stop Server", show=False),
    ]

    current_page: reactive[str] = reactive("dashboard")

    def __init__(self) -> None:
        super().__init__()
        self.pm = ProcessManager(PROJECT_ROOT)

    # ── Layout ───────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield Sidebar(id="sidebar")
            with ContentSwitcher(id="content", initial="dashboard"):
                yield DashboardPage(id="dashboard")
                yield ChatPage(id="chat")
                yield EmailPage(id="email")
                yield ServicesPage(id="services")
                yield LogsPage(id="logs")
                yield SentinelPage(id="sentinel")
        yield Footer()

    # ── Lifecycle ────────────────────────────────────────────────
    def on_mount(self) -> None:
        self._populate_dashboard()
        self._populate_services_table()
        self._populate_sentinel()
        self._init_chat_log()
        self._load_logs("all")
        self._start_auto_refresh()
        self._register_process_log_callbacks()
        self._update_svc_status_bar()
        self._fetch_ai_models()

    # ── Navigation ───────────────────────────────────────────────
    def action_switch_page(self, page: str) -> None:
        self.current_page = page
        switcher = self.query_one("#content", ContentSwitcher)
        switcher.current = page

        # Update sidebar active state
        for btn in self.query(".nav-btn"):
            btn.remove_class("-active")
        try:
            self.query_one(f"#nav-{page}").add_class("-active")
        except NoMatches:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        # Sidebar navigation
        if btn_id.startswith("nav-"):
            page = btn_id.replace("nav-", "")
            self.action_switch_page(page)
            return

        # Chat send
        if btn_id == "send-btn":
            self._handle_chat_send()
            return

        # Email send
        if btn_id == "send-email-btn":
            self._handle_email_send()
            return

        # Log filters
        if btn_id.startswith("log-"):
            log_type = btn_id.replace("log-", "")
            self._load_logs(log_type)
            return

        # ── Service controls ──
        if btn_id == "svc-start-fastapi":
            self._do_start_server()
            return
        if btn_id == "svc-stop-fastapi":
            self._do_stop_server()
            return
        if btn_id == "svc-restart-fastapi":
            self._do_restart_server()
            return
        if btn_id == "svc-start-celery":
            self._do_start_celery()
            return
        if btn_id == "svc-stop-celery":
            self._do_stop_celery()
            return
        if btn_id == "svc-start-sentinel":
            self._do_start_sentinel()
            return
        if btn_id == "svc-stop-sentinel":
            self._do_stop_sentinel()
            return
        if btn_id == "svc-start-valkey":
            self._do_start_valkey()
            return
        if btn_id == "svc-stop-valkey":
            self._do_stop_valkey()
            return

        # Clear chat history
        if btn_id == "clear-chat-btn":
            self._handle_clear_chat()
            return

    # ── Dashboard ────────────────────────────────────────────────
    @work(thread=True)
    def _populate_dashboard(self) -> None:
        """Fill in dashboard metrics."""
        import shutil

        # Server Status
        server_online = False
        try:
            resp = httpx.get(f"{ELYSIUM_BASE_URL}/api/v1/health", timeout=3)
            server_online = resp.status_code == 200
        except Exception:
            pass

        status_icon = "🟢" if server_online else "🔴"
        status_text = "ONLINE" if server_online else "OFFLINE"
        status_style = "status-online" if server_online else "status-offline"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        server_content = (
            f"  {status_icon}  Elysium Server: [{status_style}]{status_text}[/]\n"
            f"  🌐  URL: [#88c0d0]{ELYSIUM_BASE_URL}[/]\n"
            f"  🕐  Checked: [dim]{now}[/]\n"
            f"  📡  Endpoints: [#a3be8c]6 routes[/]"
        )
        self.call_from_thread(
            self._update_static, "#server-status-content", server_content
        )

        # System Info
        uname = platform.uname()
        disk = shutil.disk_usage("/")
        disk_used_pct = (disk.used / disk.total) * 100
        disk_color = "#a3be8c" if disk_used_pct < 70 else "#ebcb8b" if disk_used_pct < 90 else "#bf616a"

        sys_content = (
            f"  💻  Host: [#88c0d0]{uname.node}[/]\n"
            f"  🐧  OS: [#88c0d0]{uname.system} {uname.release[:20]}[/]\n"
            f"  🏗️  Arch: [#88c0d0]{uname.machine}[/]\n"
            f"  💾  Disk: [{disk_color}]{disk_used_pct:.1f}%[/] used "
            f"([dim]{disk.used // (1024**3)}G / {disk.total // (1024**3)}G[/])"
        )
        self.call_from_thread(
            self._update_static, "#system-info-content", sys_content
        )

        # Services Overview
        redis_ok = self._check_redis()
        redis_icon = "🟢" if redis_ok else "🔴"
        redis_status = "RUNNING" if redis_ok else "STOPPED"

        hyper_ok = False
        try:
            r = httpx.get("https://hyper-backend-8y8v.onrender.com/api/v1/", timeout=5)
            hyper_ok = bool(r.text)
        except Exception:
            pass
        hyper_icon = "🟢" if hyper_ok else "🔴"
        hyper_status = "ONLINE" if hyper_ok else "OFFLINE"

        svc_content = (
            f"  {status_icon}  FastAPI: [{status_style}]{status_text}[/]\n"
            f"  {redis_icon}  Redis: [{'#a3be8c' if redis_ok else '#bf616a'}]{redis_status}[/]\n"
            f"  {hyper_icon}  Hyper: [{'#a3be8c' if hyper_ok else '#bf616a'}]{hyper_status}[/]\n"
            f"  🛡️  Sentinel: [#ebcb8b]STANDBY[/]"
        )
        self.call_from_thread(
            self._update_static, "#services-overview-content", svc_content
        )

        # Quick Stats
        log_dir = PROJECT_ROOT / "Logs"
        log_count = sum(1 for _ in log_dir.rglob("*.log")) if log_dir.exists() else 0
        py_files = sum(1 for _ in PROJECT_ROOT.rglob("*.py"))
        sentinel_dir = PROJECT_ROOT / "Elysium_back_up"
        backup_exists = sentinel_dir.exists()

        stats_content = (
            f"  📂  Python files: [#a3be8c]{py_files}[/]\n"
            f"  📋  Log files: [#88c0d0]{log_count}[/]\n"
            f"  💾  Backup: [{'#a3be8c' if backup_exists else '#bf616a'}]"
            f"{'EXISTS' if backup_exists else 'NONE'}[/]\n"
            f"  🐍  Python: [#88c0d0]{platform.python_version()}[/]"
        )
        self.call_from_thread(
            self._update_static, "#quick-stats-content", stats_content
        )

    def _update_static(self, selector: str, content: str) -> None:
        try:
            widget = self.query_one(selector, Static)
            widget.update(content)
        except NoMatches:
            pass

    def _check_redis(self) -> bool:
        try:
            import redis as r
            client = r.Redis(host="127.0.0.1", port=6379, socket_timeout=2)
            return client.ping()
        except Exception:
            return False

    @work(thread=True)
    def _fetch_ai_models(self) -> None:
        """Fetch available models from the backend and populate the Select dropdown."""
        try:
            resp = httpx.get(f"{ELYSIUM_BASE_URL}/api/v1/chat/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.call_from_thread(self._update_model_select, data)
        except Exception:
            pass

    def _update_model_select(self, data: dict) -> None:
        try:
            select = self.query_one("#model-select", Select)
            options = []
            
            # Add Groq models
            groq_models = data.get("providers", {}).get("groq", [])
            if groq_models:
                options.append(("--- Cloud Models (Groq) ---", Select.BLANK))
                for m in sorted(groq_models):
                    options.append((f"☁️ {m}", f"groq|{m}"))
            
            # Add Ollama models
            ollama_models = data.get("providers", {}).get("ollama", [])
            if ollama_models:
                options.append(("--- Local Models (Ollama) ---", Select.BLANK))
                for m in sorted(ollama_models):
                    options.append((f"🖥️ {m}", f"ollama|{m}"))
            
            # Update Select options
            select.set_options(options)
            
            # Set currently active
            current = data.get("current", {})
            provider = current.get("provider")
            model_name = current.get("model_name")
            
            if provider and model_name:
                active_val = f"{provider}|{model_name}"
                select.value = active_val
                
        except NoMatches:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle model selection change."""
        if event.select.id == "model-select" and event.value and event.value != Select.BLANK:
            provider, model_name = event.value.split("|", 1)
            self._switch_model(provider, model_name)

    @work(thread=True)
    def _switch_model(self, provider: str, model_name: str) -> None:
        try:
            resp = httpx.post(
                f"{ELYSIUM_BASE_URL}/api/v1/chat/model",
                json={"provider": provider, "model_name": model_name},
                timeout=5,
            )
            if resp.status_code == 200:
                self.call_from_thread(self.notify, f"Switched to {model_name} ({provider})", severity="information")
                self.call_from_thread(self._append_chat_system_msg, f"Switched AI model to {model_name} [{provider.upper()}]")
            else:
                self.call_from_thread(self.notify, f"❌ Failed to switch model", severity="error")
        except Exception as e:
            self.call_from_thread(self.notify, f"❌ Error switching model: {str(e)[:50]}", severity="error")

    def _append_chat_system_msg(self, msg: str) -> None:
        try:
            log = self.query_one("#chat-log", RichLog)
            log.write(Text.from_markup(f"\n[dim italic #ebcb8b]⚙️ {escape(msg)}[/]"))
        except NoMatches:
            pass

    # ── Chat ─────────────────────────────────────────────────────
    def _init_chat_log(self) -> None:
        try:
            log = self.query_one("#chat-log", RichLog)
            log.write(
                Text.from_markup(
                    "[bold #b48ead]Welcome to Elysium AI Agent[/]\n"
                    "[dim]Type a message to chat with your home assistant.\n"
                    "The agent can control lights, send emails, manage files, and more.[/]\n"
                )
            )
        except NoMatches:
            pass

    def _handle_chat_send(self) -> None:
        try:
            chat_input = self.query_one("#chat-input", TextArea)
        except NoMatches:
            return

        message = chat_input.text.strip()
        if not message:
            return

        chat_input.text = ""

        log = self.query_one("#chat-log", RichLog)
        timestamp = datetime.now().strftime("%H:%M")
        log.write(
            Text.from_markup(
                f"\n[dim]{timestamp}[/] [bold #81a1c1]You ›[/]  {escape(message)}"
            )
        )

        self._send_chat_message(message)

    @work(thread=True)
    def _handle_clear_chat(self) -> None:
        """Clear the AI chat history via the API and update the UI."""
        try:
            resp = httpx.post(
                f"{ELYSIUM_BASE_URL}/api/v1/chat/Agent/clear",
                json={"thread_id": "elysium-main"},
                timeout=10,
            )
            if resp.status_code == 200:
                self.call_from_thread(self._do_clear_chat_ui)
            else:
                self.call_from_thread(
                    self.notify, f"❌ Failed to clear memory: {resp.text[:50]}", "error"
                )
        except httpx.ConnectError:
            self.call_from_thread(
                self.notify, "⚠ Cannot connect to Elysium server to clear memory.", "warning"
            )
        except Exception as e:
            self.call_from_thread(
                self.notify, f"❌ Error: {str(e)[:50]}", "error"
            )

    def _do_clear_chat_ui(self) -> None:
        """Update the UI after chat memory is cleared."""
        try:
            log = self.query_one("#chat-log", RichLog)
            log.clear()
            log.write(
                Text.from_markup(
                    "[bold #bf616a]Memory Cleared[/]\n"
                    "[dim]Elysium has forgotten the previous conversation and is ready for a fresh start.[/]\n"
                )
            )
            self.notify("Chat memory cleared!", severity="information")
        except NoMatches:
            pass

    @work(thread=True)
    def _send_chat_message(self, message: str) -> None:
        """Send message to AI agent API."""
        try:
            resp = httpx.post(
                f"{ELYSIUM_BASE_URL}/api/v1/chat/Agent",
                json={"chat": message},
                timeout=30,
            )

            if resp.status_code == 200:
                data = resp.json()
                # The response is just a string
                if isinstance(data, str):
                    reply = data
                elif isinstance(data, dict):
                    reply = data.get("response", data.get("content", str(data)))
                else:
                    reply = str(data)
            else:
                reply = f"[Error {resp.status_code}] {resp.text[:200]}"

        except httpx.ConnectError:
            reply = "[dim red]⚠ Cannot connect to Elysium server. Is it running?[/]"
        except Exception as e:
            reply = f"[dim red]⚠ {escape(str(e))}[/]"

        timestamp = datetime.now().strftime("%H:%M")
        self.call_from_thread(self._append_chat_reply, timestamp, reply)

    def _append_chat_reply(self, timestamp: str, reply: str) -> None:
        try:
            log = self.query_one("#chat-log", RichLog)
            log.write(
                Text.from_markup(
                    f"[dim]{timestamp}[/] [bold #a3be8c]EL ›[/]  {escape(reply)}"
                )
            )
        except NoMatches:
            pass

    # ── Email ────────────────────────────────────────────────────
    def _handle_email_send(self) -> None:
        try:
            to_input = self.query_one("#email-to", Input)
            subject_input = self.query_one("#email-subject", Input)
            body_input = self.query_one("#email-body", TextArea)
        except NoMatches:
            return

        to = to_input.value.strip()
        subject = subject_input.value.strip()
        body = body_input.text.strip()

        if not to or not subject or not body:
            self.notify("⚠ Please fill all fields", severity="warning")
            return

        self._send_email_request(to, subject, body)

    @work(thread=True)
    def _send_email_request(self, to: str, subject: str, body: str) -> None:
        try:
            resp = httpx.post(
                f"{ELYSIUM_BASE_URL}/api/v1/send/email",
                json={"subject": subject, "reciver": to, "content": body},
                timeout=10,
            )
            if resp.status_code == 200:
                self.call_from_thread(
                    self.notify, "✅ Email queued successfully!", "information"
                )
                # Clear fields
                self.call_from_thread(self._clear_email_fields)
            else:
                self.call_from_thread(
                    self.notify,
                    f"❌ Failed: {resp.text[:100]}",
                    "error",
                )
        except httpx.ConnectError:
            self.call_from_thread(
                self.notify,
                "⚠ Cannot connect to server",
                "error",
            )
        except Exception as e:
            self.call_from_thread(self.notify, f"❌ {str(e)[:100]}", "error")

    def _clear_email_fields(self) -> None:
        try:
            self.query_one("#email-to", Input).value = ""
            self.query_one("#email-subject", Input).value = ""
            self.query_one("#email-body", TextArea).clear()
        except NoMatches:
            pass

    # ═════════════════════════════════════════════════════════════
    #  SERVICE PROCESS MANAGEMENT
    # ═════════════════════════════════════════════════════════════

    def _find_uv(self) -> str:
        """Find the uv binary path."""
        uv = shutil.which("uv")
        return uv if uv else "uv"

    def _register_process_log_callbacks(self) -> None:
        """Wire up process stdout to the live log widget."""
        for svc in ("fastapi", "celery", "sentinel", "valkey"):
            self.pm.register_log_callback(svc, self._make_log_writer(svc))

    def _make_log_writer(self, svc_name: str):
        """Return a callback that writes lines to the svc-live-log widget."""
        tag_colors = {
            "fastapi": "#a3be8c",
            "celery": "#ebcb8b",
            "sentinel": "#b48ead",
            "valkey": "#bf616a",
        }
        color = tag_colors.get(svc_name, "#81a1c1")

        def _writer(line: str):
            self.call_from_thread(self._append_svc_log, svc_name, color, line)

        return _writer

    def _append_svc_log(self, svc_name: str, color: str, line: str) -> None:
        try:
            log = self.query_one("#svc-live-log", RichLog)
            ts = datetime.now().strftime("%H:%M:%S")
            tag = svc_name.upper().ljust(8)
            log.write(
                Text.from_markup(
                    f"[dim]{ts}[/] [{color}]{tag}[/] │ {escape(line)}"
                )
            )
        except NoMatches:
            pass

    def _update_svc_status_bar(self) -> None:
        """Update the compact status bar on the services page."""
        parts = []
        for svc, label in [("fastapi", "FastAPI"), ("celery", "Celery"), ("sentinel", "Sentinel"), ("valkey", "Valkey")]:
            if self.pm.is_running(svc):
                pid = self.pm.get_pid(svc)
                parts.append(f"  🟢  {label}: [#a3be8c]RUNNING[/] [dim](PID {pid})[/]")
            else:
                rc = self.pm.get_return_code(svc)
                if rc is not None:
                    parts.append(f"  🔴  {label}: [#bf616a]EXITED[/] [dim](code {rc})[/]")
                else:
                    parts.append(f"  ⚪  {label}: [#616e88]STOPPED[/]")
        self._update_static("#svc-status-bar", "\n".join(parts))

    # ── FastAPI ──────────────────────────────────────────────────
    def _do_start_server(self) -> None:
        if self.pm.is_running("fastapi"):
            self.notify("⚠ FastAPI server is already running", severity="warning")
            return
        uv = self._find_uv()
        env = {"PYTHONPATH": str(PROJECT_ROOT)}
        ok = self.pm.start_service(
            "fastapi",
            [uv, "run", "uvicorn", "main:elysium_server", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            env=env
        )
        if ok:
            self.notify("🚀 FastAPI server started!", severity="information")
            self._append_svc_log("fastapi", "#a3be8c", "── Server process started ──")
        else:
            self.notify("❌ Failed to start FastAPI server", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    def _do_stop_server(self) -> None:
        if not self.pm.is_running("fastapi"):
            self.notify("⚠ FastAPI server is not running", severity="warning")
            return
        ok = self.pm.stop_service("fastapi")
        if ok:
            self.notify("⏹ FastAPI server stopped", severity="information")
            self._append_svc_log("fastapi", "#bf616a", "── Server process stopped ──")
        else:
            self.notify("❌ Failed to stop server", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    def _do_restart_server(self) -> None:
        self._append_svc_log("fastapi", "#ebcb8b", "── Restarting server... ──")
        if self.pm.is_running("fastapi"):
            self.pm.stop_service("fastapi")
            # Small delay to let the port free up
            time.sleep(0.5)
        self._do_start_server()

    def action_start_server(self) -> None:
        """F5 keybinding handler."""
        self._do_start_server()

    def action_stop_server(self) -> None:
        """F6 keybinding handler."""
        self._do_stop_server()

    # ── Celery ───────────────────────────────────────────────────
    def _do_start_celery(self) -> None:
        if self.pm.is_running("celery"):
            self.notify("⚠ Celery worker is already running", severity="warning")
            return
        uv = self._find_uv()
        # Pass PYTHONPATH so celery can find local modules
        env = {"PYTHONPATH": str(PROJECT_ROOT)}
        ok = self.pm.start_service(
            "celery",
            [uv, "run", "celery", "-A", "Elysium_Celery.config", "worker", "--loglevel=info"],
            env=env
        )
        if ok:
            self.notify("🚀 Celery worker started!", severity="information")
            self._append_svc_log("celery", "#ebcb8b", "── Celery worker started ──")
        else:
            self.notify("❌ Failed to start Celery", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    def _do_stop_celery(self) -> None:
        if not self.pm.is_running("celery"):
            self.notify("⚠ Celery worker is not running", severity="warning")
            return
        ok = self.pm.stop_service("celery")
        if ok:
            self.notify("⏹ Celery worker stopped", severity="information")
            self._append_svc_log("celery", "#bf616a", "── Celery worker stopped ──")
        else:
            self.notify("❌ Failed to stop Celery", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    # ── Sentinel ─────────────────────────────────────────────────
    def _do_start_sentinel(self) -> None:
        if self.pm.is_running("sentinel"):
            self.notify("⚠ Sentinel is already running", severity="warning")
            return
        uv = self._find_uv()
        env = {"PYTHONPATH": str(PROJECT_ROOT)}
        ok = self.pm.start_service(
            "sentinel",
            [uv, "run", "python", "Sentinel/watcher.py"],
            env=env
        )
        if ok:
            self.notify("🛡️ Sentinel started!", severity="information")
            self._append_svc_log("sentinel", "#b48ead", "── Sentinel watcher started ──")
        else:
            self.notify("❌ Failed to start Sentinel", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    def _do_stop_sentinel(self) -> None:
        if not self.pm.is_running("sentinel"):
            self.notify("⚠ Sentinel is not running", severity="warning")
            return
        ok = self.pm.stop_service("sentinel")
        if ok:
            self.notify("⏹ Sentinel stopped", severity="information")
            self._append_svc_log("sentinel", "#bf616a", "── Sentinel stopped ──")
        else:
            self.notify("❌ Failed to stop Sentinel", severity="error")
        self._update_svc_status_bar()
        self._refresh_services_table()

    # ── Valkey (Native Subprocess) ────────────────────────────────
    def _do_start_valkey(self) -> None:
        if self.pm.is_running("valkey") or self._check_redis():
            self.notify("⚠ Valkey/Redis is already running on port 6379", severity="warning")
            return
        
        # Valkey is just a drop-in replacement for Redis
        # Make sure 'valkey-server' is in PATH.
        ok = self.pm.start_service(
            "valkey",
            ["valkey-server", "--port", "6379"]
        )
        if ok:
            # Wait a moment for Valkey to accept connections
            time.sleep(1)
            if self._check_redis():
                self.notify("🚀 Valkey server started natively!", severity="information")
                self._append_svc_log("valkey", "#a3be8c", "── Valkey is ready ──")
            else:
                # Started process, but still not answering pings?
                self.notify("⚠ Valkey process started, but may not be ready", severity="warning")
        else:
            self.notify("❌ Failed to start Valkey (is it installed?)", severity="error")
            self._append_svc_log("valkey", "#bf616a", "── Failed to find valkey-server ──")
        
        self._update_svc_status_bar()
        self._refresh_services_table()

    def _do_stop_valkey(self) -> None:
        if not self.pm.is_running("valkey"):
            self.notify("⚠ Valkey is not running under the TUI manager", severity="warning")
            return
            
        self._append_svc_log("valkey", "#bf616a", "── Stopping Valkey server ──")
        ok = self.pm.stop_service("valkey")
        if ok:
            self.notify("⏹ Valkey server stopped", severity="information")
            self._append_svc_log("valkey", "#bf616a", "── Valkey stopped ──")
        else:
            self.notify("❌ Failed to stop Valkey", severity="error")
            
        self._update_svc_status_bar()
        self._refresh_services_table()

    # ── Services Table ───────────────────────────────────────────
    def _populate_services_table(self) -> None:
        try:
            table = self.query_one("#services-table", DataTable)
        except NoMatches:
            return

        table.add_columns("Service", "Description", "Type", "PID", "Status")

        services = [
            ("FastAPI Server", "Core HTTP API server (uvicorn)", "HTTP", "-", "checking..."),
            ("Celery Workers", "Background task processing", "Worker", "-", "checking..."),
            ("Redis / Valkey", "Message broker & cache", "Broker", "-", "checking..."),
            ("Sentinel", "File integrity watcher", "Monitor", "-", "checking..."),
            ("Hyper Server", "External health monitor", "External", "-", "checking..."),
            ("AI Agent", "LangChain + Groq", "AI", "-", "ready"),
        ]

        for name, desc, stype, pid, status in services:
            table.add_row(name, desc, stype, pid, status)

        self._check_services_status()

    def _refresh_services_table(self) -> None:
        """Re-check statuses after a start/stop action."""
        self._check_services_status()

    @work(thread=True)
    def _check_services_status(self) -> None:
        """Check all service statuses."""
        statuses = {}

        # FastAPI — check managed process first, then HTTP
        if self.pm.is_running("fastapi"):
            pid = str(self.pm.get_pid("fastapi") or "")
            # Also verify it's actually responding
            try:
                resp = httpx.get(f"{ELYSIUM_BASE_URL}/api/v1/health", timeout=2)
                if resp.status_code == 200:
                    statuses[0] = (pid, "🟢 online")
                else:
                    statuses[0] = (pid, "🟡 starting...")
            except Exception:
                statuses[0] = (pid, "🟡 starting...")
        else:
            # Not managed — maybe running externally?
            try:
                resp = httpx.get(f"{ELYSIUM_BASE_URL}/api/v1/health", timeout=2)
                statuses[0] = ("-", "🟢 online (ext)") if resp.status_code == 200 else ("-", "🔴 error")
            except Exception:
                statuses[0] = ("-", "🔴 offline")

        # Celery
        if self.pm.is_running("celery"):
            statuses[1] = (str(self.pm.get_pid("celery") or ""), "🟢 running")
        else:
            try:
                from Elysium_Celery.config import celery as celery_app
                inspector = celery_app.control.inspect(timeout=2)
                active = inspector.active()
                statuses[1] = ("-", "🟢 running (ext)") if active else ("-", "🟡 no workers")
            except Exception:
                statuses[1] = ("-", "⚪ stopped")

        # Redis / Valkey
        redis_ok = self._check_redis()
        if self.pm.is_running("valkey"):
            pid = str(self.pm.get_pid("valkey") or "")
            statuses[2] = (pid, "🟢 running") if redis_ok else (pid, "🟡 starting...")
        else:
            statuses[2] = ("-", "🟢 running (ext)") if redis_ok else ("-", "⚪ stopped")

        # Sentinel
        if self.pm.is_running("sentinel"):
            statuses[3] = (str(self.pm.get_pid("sentinel") or ""), "🟢 watching")
        else:
            statuses[3] = ("-", "⚪ stopped")

        # Hyper
        try:
            r = httpx.get("https://hyper-backend-8y8v.onrender.com/api/v1/", timeout=5)
            statuses[4] = ("-", "🟢 online") if r.text else ("-", "🔴 offline")
        except Exception:
            statuses[4] = ("-", "🔴 offline")

        # AI Agent
        statuses[5] = ("-", "🟢 ready")

        self.call_from_thread(self._update_services_table, statuses)
        self.call_from_thread(self._update_svc_status_bar)

    def _update_services_table(self, statuses: dict) -> None:
        try:
            table = self.query_one("#services-table", DataTable)
            for row_idx, (pid, status) in statuses.items():
                row_key = table._row_order[row_idx]  # noqa
                table.update_cell(row_key, "PID", pid)
                table.update_cell(row_key, "Status", status)
        except Exception:
            pass

    # ── Logs ─────────────────────────────────────────────────────
    def _load_logs(self, log_type: str = "all") -> None:
        try:
            log_widget = self.query_one("#log-output", RichLog)
        except NoMatches:
            return

        log_widget.clear()
        log_dir = PROJECT_ROOT / "Logs"

        if not log_dir.exists():
            log_widget.write(
                Text.from_markup("[dim]No log directory found.[/]")
            )
            return

        log_files: list[Path] = []

        if log_type == "all":
            log_files = sorted(log_dir.rglob("*.log"))
        elif log_type == "elysium":
            elysium_dir = log_dir / "Elysium"
            if elysium_dir.exists():
                log_files = sorted(elysium_dir.glob("*.log"))
        elif log_type == "hyper":
            hyper_dir = log_dir / "Hyper"
            if hyper_dir.exists():
                log_files = sorted(hyper_dir.glob("*.log"))

        if not log_files:
            log_widget.write(
                Text.from_markup(f"[dim]No {log_type} logs found.[/]")
            )
            return

        for lf in log_files:
            log_widget.write(
                Text.from_markup(f"\n[bold #81a1c1]━━━ {lf.name} ━━━[/]")
            )
            try:
                content = lf.read_text(errors="replace")
                lines = content.strip().split("\n")
                # Show last 50 lines per file
                for line in lines[-50:]:
                    if "ERROR" in line:
                        log_widget.write(
                            Text.from_markup(f"[#bf616a]{escape(line)}[/]")
                        )
                    elif "WARNING" in line:
                        log_widget.write(
                            Text.from_markup(f"[#ebcb8b]{escape(line)}[/]")
                        )
                    elif "INFO" in line:
                        log_widget.write(
                            Text.from_markup(f"[#81a1c1]{escape(line)}[/]")
                        )
                    else:
                        log_widget.write(
                            Text.from_markup(f"[#616e88]{escape(line)}[/]")
                        )
            except Exception as e:
                log_widget.write(
                    Text.from_markup(f"[red]Error reading {lf.name}: {e}[/]")
                )

    # ── Sentinel ─────────────────────────────────────────────────
    def _populate_sentinel(self) -> None:
        self._load_sentinel_info()
        self._load_sentinel_table()

    def _load_sentinel_info(self) -> None:
        backup_dir = PROJECT_ROOT / "Elysium_back_up"
        backup_exists = backup_dir.exists()
        backup_icon = "🟢" if backup_exists else "🔴"

        info = (
            f"  🛡️  Sentinel watches your project files for changes\n"
            f"  {backup_icon}  Backup: [{'#a3be8c' if backup_exists else '#bf616a'}]"
            f"{'Available' if backup_exists else 'Not created'}[/]\n"
            f"  📂  Project: [#88c0d0]{PROJECT_ROOT}[/]\n"
            f"  ⏱️  Watch interval: [#a3be8c]5s[/]"
        )
        self._update_static("#sentinel-info", info)

    def _load_sentinel_table(self) -> None:
        try:
            table = self.query_one("#sentinel-table", DataTable)
        except NoMatches:
            return

        table.add_columns("Directory", "Type", "Files", "Status")

        for item in sorted(PROJECT_ROOT.iterdir()):
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            if item.name in ("Elysium_back_up", "Logs", ".venv", ".git"):
                continue

            if item.is_dir():
                file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                table.add_row(
                    item.name,
                    "📁 directory",
                    str(file_count),
                    "🟢 tracked",
                )
            elif item.is_file():
                size = item.stat().st_size
                size_str = (
                    f"{size}B"
                    if size < 1024
                    else f"{size / 1024:.1f}KB"
                    if size < 1024 * 1024
                    else f"{size / (1024 * 1024):.1f}MB"
                )
                table.add_row(
                    item.name,
                    "📄 file",
                    size_str,
                    "🟢 tracked",
                )

    # ── Auto-refresh ─────────────────────────────────────────────
    def _start_auto_refresh(self) -> None:
        self.set_interval(30, self._auto_refresh)
        self.set_interval(5, self._auto_refresh_services)

    def _auto_refresh(self) -> None:
        if self.current_page == "dashboard":
            self._populate_dashboard()

    def _auto_refresh_services(self) -> None:
        """Periodically refresh service status bar & table."""
        if self.current_page == "services":
            self._check_services_status()

    def action_refresh_dashboard(self) -> None:
        self._populate_dashboard()
        self._check_services_status()
        self.notify("🔄 Refreshed!", severity="information")

    # ── Cleanup on exit ──────────────────────────────────────────
    def on_unmount(self) -> None:
        """Stop all managed processes when TUI exits."""
        self.pm.stop_all()


# ═════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════
def main():
    app = ElysiumApp()
    app.run()


if __name__ == "__main__":
    main()
