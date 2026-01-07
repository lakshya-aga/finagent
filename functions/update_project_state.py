
from functions.get_project_state import PROJECT_STATE_PATH
import os
from google.genai import types

def update_project_state(working_directory, update: str) -> str:
    """
    Appends a concise, human-readable update to the project state.
    Should only be called after successful changes.
    """
    update = update.strip()
    if not update:
        return "No update provided."
    abs_working_dir = os.path.abspath(working_directory)
    print(abs_working_dir)
    target_file = os.path.normpath(os.path.join(abs_working_dir, PROJECT_STATE_PATH))

    if os.path.commonpath([target_file, abs_working_dir]) != abs_working_dir:
        return f'Error: Cannot write to "{PROJECT_STATE_PATH}" as it is outside the permitted working directory'
    
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{PROJECT_STATE_PATH}" as it is a directory'
    
    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    with open(target_file, "a", encoding="utf-8") as f:
        f.write("\n\n---\n")
        f.write(update)
    return f'Successfully wrote to "{PROJECT_STATE_PATH}" ({len(update)} characters written)'

schema_update_project_state = types.FunctionDeclaration(
    name="update_project_state",
    description="Updates the project state with a new update",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "update": types.Schema(
                type=types.Type.STRING,
                description="String to be appended to the specified file"
            ),
        },
    ),
)