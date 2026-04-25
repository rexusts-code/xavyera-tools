import os
import glob
from typing import List, Optional
from pydantic import BaseModel, Field
from .base import Tool

class ListFilesParams(BaseModel):
    path: str = Field(..., description="The path to list files from (relative to project root).")
    recursive: bool = Field(False, description="Whether to list files recursively.")

def list_files(path: str, recursive: bool = False) -> str:
    try:
        if recursive:
            files = []
            for root, dirs, filenames in os.walk(path):
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root, f), path))
            return "\n".join(files)
        else:
            return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Error: {str(e)}"

class ReadFileParams(BaseModel):
    path: str = Field(..., description="The path of the file to read.")

def read_file(path: str) -> str:
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

class WriteFileParams(BaseModel):
    path: str = Field(..., description="The path of the file to write.")
    content: str = Field(..., description="The content to write to the file.")

def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {str(e)}"

def register_file_tools(registry):
    registry.register(Tool(
        name="list_files",
        description="Lists files in a directory.",
        parameters=ListFilesParams,
        func=list_files
    ))
    registry.register(Tool(
        name="read_file",
        description="Reads the content of a file.",
        parameters=ReadFileParams,
        func=read_file
    ))
    registry.register(Tool(
        name="write_file",
        description="Writes content to a file.",
        parameters=WriteFileParams,
        func=write_file
    ))
