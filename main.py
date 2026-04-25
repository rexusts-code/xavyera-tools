import os
import sys

# Add local libs to path BEFORE other imports
sys.path.insert(0, os.path.join(os.getcwd(), ".libs"))

import click
from dotenv import load_dotenv

from lumina.core.agent import (
    LuminaAgent, 
    GeminiProvider, 
    AnthropicProvider, 
    OpenRouterProvider, 
    OpenAIProvider, 
    GroqProvider, 
    OllamaProvider
)
from lumina.ui import LuminaUI
from lumina.tools.base import ToolRegistry
from lumina.tools.file_system import register_file_tools
from lumina.tools.shell import register_shell_tools
from lumina.tools.search import register_search_tools
from lumina.core.prompts import SYSTEM_PROMPT, CODING_PROMPT, PLANNING_PROMPT
from lumina.core.quota import QuotaManager

load_dotenv()

def get_provider():
    p_name = os.getenv("LUMINA_PROVIDER", "gemini").lower()
    model = os.getenv("LUMINA_MODEL")
    
    key = None
    if p_name == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            print("\n[bold red]Authentication Required[/bold red]")
            key = click.prompt("Enter your Gemini API Key", hide_input=True)
            with open(".env", "a") as f:
                f.write(f"\nGEMINI_API_KEY={key}\n")
            os.environ["GEMINI_API_KEY"] = key
        return GeminiProvider(key, model or "gemini-1.5-flash")
    elif p_name == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            key = click.prompt("Enter your Anthropic API Key", hide_input=True)
            with open(".env", "a") as f:
                f.write(f"\nANTHROPIC_API_KEY={key}\n")
            os.environ["ANTHROPIC_API_KEY"] = key
        return AnthropicProvider(key, model or "claude-3-5-sonnet-20240620")
    # ... handle other providers similarly if needed
    elif p_name == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            key = click.prompt("Enter your OpenAI API Key", hide_input=True)
            with open(".env", "a") as f:
                f.write(f"\nOPENAI_API_KEY={key}\n")
            os.environ["OPENAI_API_KEY"] = key
        return OpenAIProvider(key, model or "gpt-4o")
    elif p_name == "openrouter":
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            key = click.prompt("Enter your OpenRouter API Key", hide_input=True)
            with open(".env", "a") as f:
                f.write(f"\nOPENROUTER_API_KEY={key}\n")
            os.environ["OPENROUTER_API_KEY"] = key
        return OpenRouterProvider(key, model or "anthropic/claude-3.5-sonnet")
    elif p_name == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key:
            key = click.prompt("Enter your Groq API Key", hide_input=True)
            with open(".env", "a") as f:
                f.write(f"\nGROQ_API_KEY={key}\n")
            os.environ["GROQ_API_KEY"] = key
        return GroqProvider(key, model or "llama3-70b-8192")
    elif p_name == "ollama":
        return OllamaProvider(model or "llama3")
    else:
        raise Exception(f"Unknown provider: {p_name}")

def create_app():
    ui = LuminaUI()
    ui.welcome()
    
    # Tier Selection
    tier_choice = click.prompt("\nSelect your Tier", type=click.Choice(['1', '2', '3']), default='1', show_choices=False)
    tier_map = {'1': 'silver', '2': 'gold', '3': 'master'}
    selected_tier = tier_map[tier_choice]
    
    quota = QuotaManager(selected_tier)
    
    try:
        provider = get_provider()
    except Exception as e:
        ui.error(str(e))
        sys.exit(1)
    agent = LuminaAgent(provider)
    registry = ToolRegistry()
    register_file_tools(registry)
    register_shell_tools(registry)
    register_search_tools(registry)
    agent.add_tool_registry(registry)
    return ui, agent, quota

def handle_slash_command(command: str, ui: LuminaUI, agent: LuminaAgent, quota: QuotaManager) -> bool:
    cmd = command.lower().strip()
    if cmd == "/help":
        ui.show_help()
        return True
    elif cmd == "/status":
        status_info = f"{agent.provider.__class__.__name__} ({agent.provider.model})\n- **Quota Remaining**: {quota.get_remaining()} tokens"
        ui.show_status(status_info)
        return True
    elif cmd == "/clear":
        agent.history = []
        ui.info("History cleared.")
        return True
    elif cmd == "/rewind":
        if len(agent.history) >= 2:
            agent.history.pop()
            agent.history.pop()
            ui.info("Last turn removed.")
        else:
            ui.error("Nothing to rewind.")
        return True
    elif cmd.startswith("/code"):
        agent.set_system_prompt(CODING_PROMPT)
        from rich.panel import Panel
        ui.console.print(Panel("[bold green]ENTERING ELITE ARCHITECT MODE[/bold green]\nSpecialized in fullstack, hacking tools, and complex systems.", border_style="green"))
        return True
    elif cmd == "/plan":
        agent.set_system_prompt(PLANNING_PROMPT)
        ui.console.print(Panel("[bold blue]ENTERING PLANNING MODE[/bold blue]\nI will analyze and propose steps before writing code.", border_style="blue"))
        return True
    elif cmd == "/config":
        # Show all env variables related to Lumina
        config_info = f"""
- **Provider**: {os.getenv("LUMINA_PROVIDER")}
- **Model**: {agent.provider.model}
- **API Key**: {'Configured' if agent.provider.api_key else 'Missing'}
"""
        ui.console.print(Panel(config_info, title="Configuration", border_style="yellow"))
        return True
    elif cmd == "/theme":
        ui.info("Theme selection menu reopened.")
        ui.welcome() # Re-show welcome and style menu
        return True
    elif cmd == "/exit":
        ui.info("Goodbye!")
        sys.exit(0)
    return False

@click.command()
@click.option('--query', '-q', help="Run a single query and exit.")
def main(query):
    ui, agent, quota = create_app()
    if query:
        if quota.is_exhausted():
            ui.error("QUOTA EXHAUSTED! Please upgrade your tier to continue.")
            return
        try:
            with ui.console.status("[bold green]Lumina is thinking..."):
                response, tokens = agent.run(query)
                quota.add_usage(tokens)
            ui.print_agent_thought(response)
        except Exception as e:
            ui.error(str(e))
        return
    
    ui.info(f"Active Provider: [bold cyan]{agent.provider.__class__.__name__}[/bold cyan]")
    ui.info(f"Active Model: [bold magenta]{agent.provider.model}[/bold magenta]")
    ui.info(f"Active Tier: [bold yellow]{quota.tier.upper()}[/bold yellow] ({quota.get_remaining()} tokens remaining)")
    
    while True:
        try:
            if quota.is_exhausted():
                ui.error("QUOTA EXHAUSTED! Xavyera Code access is now blocked. Upgrade to Master for unlimited access.")
                break

            user_input = ui.get_user_input()
            if not user_input.strip(): continue
            if user_input.startswith("/"):
                if handle_slash_command(user_input, ui, agent, quota): continue
            
            def on_tool_call(name, args):
                # Request ACC (Approval) for different tools
                if name == "execute_command":
                    ui.console.print(f"\n[bold yellow]⚠ AI wants to run command:[/bold yellow] [white]{args.get('command')}[/white]")
                    if not click.confirm("Allow execution?", default=False):
                        raise Exception("User denied command execution.")
                
                elif name == "write_file":
                    ui.console.print(f"\n[bold yellow]⚠ AI wants to WRITE to file:[/bold yellow] [cyan]{args.get('path')}[/cyan]")
                    if not click.confirm("Allow writing?", default=False):
                        raise Exception("User denied file write.")
                
                elif name == "read_file":
                    ui.console.print(f"\n[bold yellow]⚠ AI wants to READ file:[/bold yellow] [cyan]{args.get('path')}[/cyan]")
                    if not click.confirm("Allow reading?", default=True):
                        raise Exception("User denied file read.")

                elif name == "list_files":
                    ui.console.print(f"\n[bold yellow]⚠ AI wants to LIST directory:[/bold yellow] [cyan]{args.get('path')}[/cyan]")
                    if not click.confirm("Allow listing?", default=True):
                        raise Exception("User denied directory listing.")

                ui.print_tool_call(name, args)

            with ui.console.status("[bold green]Lumina is thinking..."):
                response, tokens = agent.run(user_input, on_tool_call=on_tool_call)
                quota.add_usage(tokens)
            ui.print_agent_thought(response)
        except KeyboardInterrupt:
            ui.info("\nUse /exit to quit.")
        except Exception as e:
            ui.error(str(e))

if __name__ == "__main__":
    main()
