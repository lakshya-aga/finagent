import os
from google.genai import types

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))

    if os.path.commonpath([target_file, abs_working_dir]) != abs_working_dir:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'
    
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, 'w') as f:
        f.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file to be written to, relative to the working directory"
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="String to be written to the specified file"
            ),
        },
    ),
)