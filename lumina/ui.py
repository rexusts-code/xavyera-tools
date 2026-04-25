import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
import os

console = Console()

WELCOME_ASCII = """
    *   Checking connectivity...
    [bold red]Welcome to Xavyera Code v1.0.0[/bold red]
    ----------------------------------------------------------
          *                   .             .
               .                    .              .
    .               [white]████████[/white]                   .
                 [white]███      ███[/white]          .
          .     [white]███[/white]          .
                [white]███[/white]                  *
          *      [white]███      ███[/white]
    .           [white]████████[/white]             .
                 
    .         [bold orange3]█████████[/bold orange3]         .             *
              [bold orange3]█ █   █ █[/bold orange3]
    *         [bold orange3]█████████[/bold orange3]                 .
              [bold orange3]  █   █[/bold orange3]
    ----------------------------------------------------------
"""

class LuminaUI:
    def __init__(self):
        self.console = console

    def welcome(self):
        # 1. Connectivity Check
        with self.console.status("[dim]* Checking connectivity...[/dim]", spinner="dots"):
            time.sleep(1.0)
        
        self.console.print(WELCOME_ASCII)

        # 2. Subscription Tier Selection
        self.console.print("Xavyera Code can be used with your Xavyera subscription or specialized AI tier.")
        self.console.print("Select your power level:\n")
        tiers = [
            ("[bold cyan]Xavyera Silver[/bold cyan]", "5,000 tokens quota."),
            ("[bold gold1]Xavyera Gold[/bold gold1]", "10,000 tokens quota."),
            ("[bold magenta]Xavyera Master[/bold magenta]", "Unlimited access & Elite Mode.")
        ]
        for i, (name, desc) in enumerate(tiers, 1):
            self.console.print(f"  {i}. {name} · {desc}")
        
        # We handle selection in main.py, but for UI flow we just show it.
        self.console.print("\n----------------------------------------------------------\n")

        # 3. Trust Screen (Image 1)
        self.console.print("[bold yellow]Accessing workspace:[/bold yellow]\n")
        self.console.print(f"[bold]{os.getcwd()}[/bold]\n")
        self.console.print("Quick safety check: Is this a project you created or one you trust? (Like your own code, a well-known open source project, or work from a colleague.) If you're not sure, take a moment to review what's in this folder first.\n")
        self.console.print("Xavyera Code will be able to read, edit, and execute files here.\n")
        self.console.print("[dim]Security guide[/dim]\n")
        
        self.console.print("> 1. [bold blue]Yes, I trust this folder[/bold blue]")
        self.console.print("  2. No, exit\n")
        
        if not Confirm.ask("Do you trust this folder and want to proceed?", default=True):
            self.console.print("[red]Exit requested. Goodbye![/red]")
            sys.exit(0)

        # 4. Project Overview (Image 2)
        overview_table = Table.grid(expand=True)
        overview_table.add_column(style="cyan", ratio=1)
        overview_table.add_column(style="white", ratio=2)

        left_content = Text.assemble(
            ("\nWelcome back xavyera!\n\n", "bold white"),
            ("      █████████      \n", "bold orange3"),
            ("      █ █   █ █      \n", "bold orange3"),
            ("      █████████      \n\n", "bold orange3"),
            ("Master 1.0  ·  Individual Org\n", "dim"),
            (f"{os.getcwd()}\n", "dim")
        )

        right_content = Text.assemble(
            ("\nTips for getting started\n", "bold orange3"),
            ("Run /init to create a XAVYERA.md file with instructions\n", "dim"),
            ("Note: You have launched Xavyera in your home directory.\n\n", "dim"),
            ("Recent activity\n", "bold orange3"),
            ("No recent activity", "dim")
        )

        overview_table.add_row(
            Panel(left_content, border_style="orange3"),
            Panel(right_content, border_style="orange3")
        )

        self.console.print(overview_table)
        self.console.print("[dim]? for shortcuts                                                                          • high  /effort[/dim]")
        self.console.print("\n----------------------------------------------------------\n")

    def print_agent_thought(self, thought: str):
        if thought:
            self.console.print(Markdown(thought))

    def print_tool_call(self, name: str, args: dict):
        self.console.print(f"[bold yellow]→ Calling tool:[/bold yellow] [cyan]{name}[/cyan] [dim]{args}[/dim]")

    def print_tool_result(self, result: str):
        self.console.print("[bold green]✓ Tool execution complete[/bold green]")

    def show_help(self):
        help_text = """
### Available Commands:
- **`/help`**: Show this help message.
- **`/code`**: Enter Elite Architect Mode.
- **`/plan`**: Enter Planning Mode.
- **`/config`**: Show current settings.
- **`/theme`**: Reopen theme selection.
- **`/rewind`**: Undo the last turn.
- **`/status`**: Show status & quota.
- **`/exit`**: Exit.
"""
        self.console.print(Panel(Markdown(help_text), title="Help", border_style="blue"))

    def show_status(self, info: str):
        status_text = f"""
- **Status**: Active
- **Details**: {info}
- **Project Root**: {os.getcwd()}
"""
        self.console.print(Panel(Markdown(status_text), title="Status", border_style="magenta"))

    def get_user_input(self) -> str:
        return Prompt.ask("[bold green]>[/bold green]")

    def error(self, msg: str):
        self.console.print(f"[bold red]Error:[/bold red] {msg}")

    def info(self, msg: str):
        self.console.print(f"[bold blue]Info:[/bold blue] {msg}")
