import os
import subprocess
from google.genai import types
def run_python_file(working_directory, file_path, args=None):
    try: 
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))

        if os.path.commonpath([target_file, abs_working_dir]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
            
        if os.path.isdir(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not os.path.exists(target_file):
            return f"Error: \"{file_path}\" does not exist"
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ['python3', target_file]
        if args is not None:
            command.extend(args)
        ans = ""
        result = subprocess.run(command, capture_output=True, cwd=abs_working_dir, text=True, timeout=30)
        if result.returncode != 0:
            ans+= f"Process exited with code {result.returncode}"
        if not result.stderr and not result.stdout:
            ans+= "No output produced"
        else:
            ans+= f"""
STDOUT: {result.stdout}
STDERR: {result.stderr}
        """
        return ans
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a specified python file, relative to the current working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the python file to be run, relative to the working directory"
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Option List of strings to be used as arguments to the python file during execution",
                items=types.Schema(
                    type=types.Type.STRING
                )
            )
        }
    )
)