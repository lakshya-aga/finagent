import os

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