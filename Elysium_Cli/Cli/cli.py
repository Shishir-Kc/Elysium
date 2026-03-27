from rich.panel import Panel
from rich.live import Live
from rich.console import Console
from rich.text import Text

console = Console()


def main():
    user_input = ""
    console.clear()

    while True:
        # Create a panel that mimics the input box
        panel_content = Text(user_input + "█", style="bold white")  # █ cursor effect
        panel = Panel(
            panel_content, title="opencode", subtitle="Type 'exit' to quit", width=50
        )

        # Render the panel live
        with Live(panel, refresh_per_second=10, console=console, transient=True):
            # Wait for user input character-by-character
            new_char = console.input("", markup=False)
            if new_char.lower() == "exit":
                console.print(Panel("Exiting...", title="Goodbye"))
                break
            user_input += new_char

        # Print what the user entered
        console.print(Panel(f"You entered: {user_input}", title="Your Input"))


if __name__ == "__main__":
    main()
