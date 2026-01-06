import os
from google.genai import types
import subprocess

def install_packages(packages):
    """
    Installs Python packages into the current environment using uv.

    Args:
        packages: A list of package names, e.g. ["numpy", "pandas==2.1.0"]

    Returns:
        Combined stdout and stderr from the installation command.
    """
    if not packages:
        return "No packages specified."

    command = ["uv", "pip", "install"] + packages

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        output = []
        if result.stdout:
            output.append("STDOUT:\n" + result.stdout)
        if result.stderr:
            output.append("STDERR:\n" + result.stderr)

        return "\n".join(output) if output else "Installation completed with no output."

    except FileNotFoundError:
        return "Error: uv is not installed or not available in PATH."
    except Exception as e:
        return f"Unexpected error during installation: {e}"
    

schema_install_packages = types.FunctionDeclaration(
    name='install_packages',
    description='Installs specified python packages in current environment using uv',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "packages": types.Schema(
                type=types.Type.ARRAY,
                description="List of strings that will be used as arguments for installing packages e.g. numpy",
                items=types.Schema(
                    type=types.Type.STRING
                )
            ),
        },
    ),
)