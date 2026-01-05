import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
from prompts import system_prompt
from call_functions import available_functions, call_function
import sys

def call_agent(client, args):

    max_iters = 20

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    for i in range(max_iters):
        config=types.GenerateContentConfig(
            tools=[available_functions], 
            system_instruction=system_prompt
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents = messages,
            config=config
        )
        if response.usage_metadata is None:
            print("Response is None")
            break

        if args.verbose:
            print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
            print(f'Response tokens: {response.usage_metadata.candidates_token_count}')
            print(f"User prompt: {args.user_prompt}")

        if response.candidates:
            [messages.append(candidate.content) for candidate in response.candidates]

        if response.function_calls:
            for function_call in response.function_calls:
                print(f"Calling function: {function_call.name} {function_call.args}")

                function_call_result = call_function(function_call, verbose=args.verbose)
                messages.append(function_call_result)

                if not (function_call_result.parts):
                    raise RuntimeError("No parts in function call result")
                
                function_response_part = function_call_result.parts[0].function_response

                if function_response_part is None:
                    raise RuntimeError("No response from function")
                if function_response_part.response is None:
                    raise RuntimeError("No response from function")

                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")                   
        else:
            print(response.text)
            return 0
    return 1

def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("No Key found")
    client = genai.Client(api_key=api_key)
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    res = call_agent(client, args)
    sys.exit(res)
    

main()