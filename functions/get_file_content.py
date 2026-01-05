import os
from google.genai import types

def get_file_content(working_directory, file_path="."):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))

    if os.path.commonpath([target_file, abs_working_dir]) != abs_working_dir:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
    if not os.path.isfile(target_file):
        print(target_file)
        return f'Error: "{file_path}" is not a file'
    MAX_CHARS = 10000
    with open(target_file, 'r') as f:
        ans = f.read(MAX_CHARS)
        if(f.read(1)):
            ans += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    return ans

schema_get_file_content = types.FunctionDeclaration(
    name='get_file_content',
    description='Retrieves the content of a specified file relative to the working directory',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the current working directory"
            ),
        },
    ),
)