"""
Elysium AI Agent — unified core for Groq (Cloud) and Ollama (Local)
"""

from langchain_groq.chat_models import ChatGroq
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from Elysium_Config.Ai.config_groq import GROQ_API
from langchain.tools import tool
from AI.Tools.email import send_email
from AI.Tools.file_ops import (
    read_file,
    write_file,
    append_to_file,
    list_directory,
    get_file_info,
    execute_command,
    create_directory,
    delete_file,
    search_files,
)


# ── Available Models (ranked by capability) ──────────────────────
# 1. meta-llama/llama-4-scout-17b-16e-instruct  — best tool calling, fast
# 2. llama-3.3-70b-versatile                     — strongest reasoning
# 3. openai/gpt-oss-120b                         — large but slow, weak tool use
# 4. qwen/qwen3-32b                              — good reasoning, tool calling issues on Groq
# 5. llama-3.1-8b-instant                        — fastest, least capable

AGENT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ── Tools ────────────────────────────────────────────────────────
@tool
def turn_light_on_off(state: bool) -> dict:
    """
    Control the smart light in the room.

    Args:
        state: True to turn light on, False to turn light off.
    """
    print(f"Light turned {'ON' if state else 'OFF'}")
    return {"light_is": "on" if state else "off", "state": state}


@tool
def get_current_time() -> str:
    """
    Get the current date and time of the server.

    Returns:
        The current date and time as a formatted string.
    """
    from datetime import datetime

    now = datetime.now()
    return now.strftime("Date: %A, %B %d, %Y | Time: %I:%M:%S %p")


@tool
def get_system_info() -> str:
    """
    Get information about the server system (hostname, OS, CPU, memory, disk).

    Returns:
        System information as a formatted string.
    """
    import platform
    import shutil
    import os

    uname = platform.uname()
    disk = shutil.disk_usage("/")

    # Try to get memory info from /proc/meminfo (Linux)
    mem_info = ""
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()[:3]
            for line in lines:
                mem_info += line.strip() + "\n"
    except Exception:
        mem_info = "Memory info unavailable"

    # CPU count
    cpu_count = os.cpu_count() or "unknown"

    return (
        f"Hostname: {uname.node}\n"
        f"OS: {uname.system} {uname.release}\n"
        f"Architecture: {uname.machine}\n"
        f"Python: {platform.python_version()}\n"
        f"CPUs: {cpu_count}\n"
        f"Disk: {disk.used // (1024**3)}GB used / {disk.total // (1024**3)}GB total "
        f"({disk.used / disk.total * 100:.1f}% used)\n"
        f"{mem_info}"
    )


# ── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are **Elysium (EL)**, an advanced AI home server assistant created by Shishir Khatri.
You are running on a personal home server and have full system access.

## Your Capabilities
You can perform real actions on the server through your tools:
- **File operations**: read, write, append, delete files; create directories; search files; get file info
- **System**: execute shell commands, get system info, get current time
- **Communication**: send emails via the server's SMTP relay
- **Smart home**: control smart lights (on/off)
- **Directory browsing**: list directory contents

## Guidelines
1. **Think step by step** before using tools. Plan your approach, then execute.
2. **Be precise** with file paths — use absolute paths when possible.
3. **Safety first** — for destructive operations (rm, format, overwrite), describe what you'll do and why before executing. If the user's intent is clear, proceed.
4. **Be concise** — give clear, direct answers. No filler or unnecessary verbosity.
5. **Use tools proactively** — if the user asks about files, system status, etc., use the relevant tool rather than guessing.
6. **Multi-step tasks** — break complex requests into steps, execute them in order, and report results.
7. **Errors** — if a tool fails, explain the error clearly and suggest alternatives.
8. **Memory** — you remember the full conversation. Reference previous messages when relevant.

## Personality
- Professional but approachable. A capable system administrator who happens to be friendly.
- When greeting users, be brief: "Hey! How can I help?" not a wall of text.
- Use markdown formatting for code blocks, lists, and structured output.
"""

# ── All Tools ────────────────────────────────────────────────────
ALL_TOOLS = [
    read_file,
    write_file,
    append_to_file,
    list_directory,
    get_file_info,
    execute_command,
    create_directory,
    delete_file,
    search_files,
    send_email,
    turn_light_on_off,
    get_current_time,
    get_system_info,
]


class Agent:
    """Elysium AI Agent with conversation memory."""

    def __init__(self):
        self.provider = "groq"
        self.model_name = AGENT_MODEL
        
        # In-memory conversation store — persists across requests
        self.memory = MemorySaver()
        self._default_thread = "elysium-main"
        
        self._build_agent()

    def _build_agent(self):
        """Build the LangGraph agent with the current model."""
        if self.provider == "groq":
            self.model = ChatGroq(
                api_key=GROQ_API,
                model=self.model_name,
                temperature=0.6,
                max_tokens=4096,
                streaming=True,
            )
        elif self.provider == "ollama":
            self.model = ChatOllama(
                model=self.model_name,
                temperature=0.6,
                base_url="http://localhost:11434"
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        self.agent = create_agent(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            checkpointer=self.memory,
        )

    def set_model(self, provider: str, model_name: str) -> None:
        """Switch the underlying language model."""
        self.provider = provider.lower()
        self.model_name = model_name
        self._build_agent()

    async def chat(
        self,
        user_message: str,
        thread_id: str | None = None,
    ) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's message.
            thread_id: Optional thread ID for conversation isolation.
                       Defaults to 'elysium-main' for the home server use case.

        Returns:
            The agent's text response.
        """
        tid = thread_id or self._default_thread
        config = {"configurable": {"thread_id": tid}}

        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", user_message)]},
                config=config,
            )

            # Walk backwards through messages to find the final AI response
            messages = response.get("messages", [])
            for msg in reversed(messages):
                content = getattr(msg, "content", None)
                if content and not getattr(msg, "tool_calls", None):
                    # Skip tool messages, get the final AI response
                    msg_type = msg.__class__.__name__
                    if msg_type in ("AIMessage", "AIMessageChunk"):
                        return content

            # Fallback: just get the last message
            if messages:
                last = messages[-1]
                content = getattr(last, "content", None)
                if content:
                    return content
                if isinstance(last, dict):
                    return last.get("content", "No response")

            return "No response from agent"

        except Exception as e:
            error_msg = str(e)
            # Provide helpful error context
            if "rate_limit" in error_msg.lower():
                return "⚠️ Rate limited by Groq. Please wait a moment and try again."
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "⚠️ API key issue. Check your GROQ_API in .env."
            if "tool_use_failed" in error_msg.lower():
                return (
                    "⚠️ Tool call formatting error. "
                    "This sometimes happens with complex requests. "
                    "Try rephrasing your request more simply."
                )
            return f"I encountered an error: {error_msg}"

    def get_conversation_history(self, thread_id: str | None = None) -> list:
        """
        Get the conversation history for a thread.

        Args:
            thread_id: The thread to retrieve history for.

        Returns:
            List of messages in the conversation.
        """
        tid = thread_id or self._default_thread
        config = {"configurable": {"thread_id": tid}}
        try:
            state = self.agent.get_state(config)
            return state.values.get("messages", [])
        except Exception:
            return []

    def clear_history(self, thread_id: str | None = None) -> bool:
        """
        Clear conversation history for a thread by resetting the checkpointer.

        Args:
            thread_id: The thread to clear.

        Returns:
            True if cleared successfully.
        """
        # MemorySaver stores in a dict — we can reset by creating a new one
        # For a more robust solution, use a persistent store
        self.memory = MemorySaver()
        self._build_agent()
        return True
