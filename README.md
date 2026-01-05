
# What Does the Agent Do?

The program we're building is a CLI tool that:

    Accepts a coding task (e.g., "strings aren't splitting in my app, pweeze fix 🥺👉🏽👈🏽")
    Chooses from a set of predefined functions to work on the task, for example:
        Scan the files in a directory
        Read a file's contents
        Overwrite a file's contents
        Execute the Python interpreter on a file
    Repeats step 2 until the task is complete (or it fails miserably, which is possible)

For example, I have a buggy calculator app, so I used my agent to fix the code:
```
> uv run main.py "fix my calculator app, it's not starting correctly"
```
- Calling function: get_files_info
- Calling function: get_file_content
- Calling function: write_file
- Calling function: run_python_file
- Calling function: write_file
- Calling function: run_python_file
- Final response:
- Great! The calculator app now seems to be working correctly. The output shows the expression and the result in a formatted way.

What Does the Agent Do?

The program we're building is a CLI tool that:

    Accepts a coding task (e.g., "strings aren't splitting in my app, pweeze fix 🥺👉🏽👈🏽")
    Chooses from a set of predefined functions to work on the task, for example:
        Scan the files in a directory
        Read a file's contents
        Overwrite a file's contents
        Execute the Python interpreter on a file
    Repeats step 2 until the task is complete (or it fails miserably, which is possible)

For example, I have a buggy calculator app, so I used my agent to fix the code:
```
> uv run main.py "fix my calculator app, it's not starting correctly"
```
- Calling function: get_files_info
- Calling function: get_file_content
- Calling function: write_file
- Calling function: run_python_file
- Calling function: write_file
- Calling function: run_python_file
- Final response:
- Great! The calculator app now seems to be working correctly. The output shows the expression and the result in a formatted way.

Prerequisites

- Python 3.10+ installed
- The uv project/package manager (installation docs) - https://docs.astral.sh/uv/getting-started/installation/
- Access to a Unix-like shell (e.g. zsh or bash)

Installation:

```
uv init your-project-name
cd your-project-name

uv venv

source .venv/bin/activate

uv add google-genai==1.12.1
uv add python-dotenv==1.1.0
```

Create a .env file, sign up for a Gemini API key from google ai studio, and place it here (There is some free tier usage - enough to test the project)

```
GEMINI_API_KEY='your_api_key_here'
```
To Check if you are setup correctly run
```
uv run main.py "Explain the calculator code to me"
```

Sample out below:


Calling function: get_files_info {}
 - Calling function: get_files_info
Calling function: get_file_content {'file_path': 'main.py'}
 - Calling function: get_file_content
Calling function: get_file_content {'file_path': 'pkg/calculator.py'}
 - Calling function: get_file_content
The calculator code is split into two main files: `main.py` and `pkg/calculator.py`.

**1. `main.py`**
This is the entry point of the application.
- It imports `Calculator` from `pkg.calculator` and `format_json_output` from `pkg.render`.
- The `main` function checks if any command-line arguments are provided. If not, it prints a usage message.
- If arguments are provided, it joins them to form the `expression` string.
- It creates an instance of the `Calculator` class.
- It calls the `evaluate` method of the `Calculator` to get the result.
- It then uses `format_json_output` to display the expression and its result in a structured JSON format.
- It includes error handling to catch and print any exceptions that occur during evaluation.

**2. `pkg/calculator.py`**
This file defines the `Calculator` class, which contains the core logic for evaluating mathematical expressions.

- **`__init__(self)`**:
    - Initializes a dictionary `self.operators` that maps operator symbols (`+`, `-`, `*`, `/`) to their corresponding lambda functions for performing the arithmetic operations.
    - Initializes a dictionary `self.precedence` that defines the order of operations for each operator (e.g., multiplication and division have higher precedence than addition and subtraction).

- **`evaluate(self, expression)`**:
    - Takes an `expression` string as input.
    - Checks if the expression is empty or just whitespace; if so, it returns `None`.
    - Splits the expression into `tokens` (numbers and operators) based on spaces.
    - Calls the private method `_evaluate_infix` to process these tokens and return the final result.

- **`_evaluate_infix(self, tokens)`**:
    - This is the core method that evaluates an infix expression using a variation of the shunting-yard algorithm.
    - It uses two lists: `values` to store numbers and `operators` to store operators.
    - It iterates through each `token`:
        - If the token is an operator:
            - It repeatedly applies operators from the `operators` stack to the `values` stack as long as the `operators` stack is not empty, the top element is an operator, and the top operator's precedence is greater than or equal to the current token's precedence.
            - Then, the current operator is pushed onto the `operators` stack.
        - If the token is a number:
            - It converts the token to a `float` and pushes it onto the `values` stack.
            - If conversion fails, it raises a `ValueError`.
    - After processing all tokens, it applies any remaining operators in the `operators` stack to the `values` stack.
    - Finally, it returns the single remaining value in the `values` stack, which is the result of the expression. If there isn't exactly one value, it means the expression was invalid, and a `ValueError` is raised.

- **`_apply_operator(self, operators, values)`**:
    - This helper method performs the actual arithmetic operation.
    - It pops an operator from the `operators` stack and the top two operands (b, then a) from the `values` stack.
    - It uses the popped operator to retrieve the correct lambda function from `self.operators` and applies it to `a` and `b`.
    - The result of the operation is then pushed back onto the `values` stack.
    - It includes error checking to ensure there are enough operands for the operator.

In essence, the calculator parses an arithmetic expression, respects operator precedence, and then computes the result.
