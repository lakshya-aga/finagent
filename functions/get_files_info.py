import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    abs_working_dir = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))

    if os.path.commonpath([target_dir, abs_working_dir]) != abs_working_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        return
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'
        
    current = "current" if directory == "." else directory
    ans = ""
    ans+= f"Result for {current} directory:"
    for f in os.listdir(target_dir):
        filename = os.path.join(target_dir,f)
        ans+= f' - {f}: filesize={os.path.getsize(filename)}, is_dir={os.path.isdir(filename)}\n'
    return ans

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)