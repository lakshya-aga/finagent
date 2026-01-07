from pathlib import Path
import os
from google.genai import types
PROJECT_STATE_PATH = Path("PROJECT_STATE.md")

def get_project_state(working_directory) -> str:
    """
    Returns the current summarized project state.
    This is long-term memory and should be treated as source of truth.
    """
    target_path = os.path.join(working_directory, PROJECT_STATE_PATH)
    if os.path.exists(working_directory) is False:
        return "Error: Working directory does not exist."
    
    if os.path.commonpath([os.path.abspath(working_directory), os.path.abspath(target_path)]) != os.path.abspath(working_directory):
        return "Error: Project state path is outside the working directory."
    
    if os.path.isfile(target_path) is False:
        return "Error: Project state file not found."

    return Path(target_path).read_text(encoding="utf-8")

schema_get_project_state = types.FunctionDeclaration(
    name='get_project_state',
    description='Retrieves the current state of the project from PROJECT_STATE.md',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
    ),
)