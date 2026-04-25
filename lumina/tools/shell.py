import subprocess
import os
from pydantic import BaseModel, Field
from .base import Tool

class ExecuteCommandParams(BaseModel):
    command: str = Field(..., description="The bash command to execute.")

def execute_command(command: str) -> str:
    try:
        # Note: In a real app, you'd want to ask for user permission before calling this.
        # This implementation will be called by the agent loop after UI approval.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output if output else "Command executed successfully (no output)."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error: {str(e)}"

def register_shell_tools(registry):
    registry.register(Tool(
        name="execute_command",
        description="Executes a bash command in the terminal.",
        parameters=ExecuteCommandParams,
        func=execute_command
    ))
