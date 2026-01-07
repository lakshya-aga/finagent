from google.genai import types

class GeminiModel:
    def __init__(self, client, model="gemini-2.5-flash"):
        self.client = client
        self.model = model

    async def generate(self, messages, system_prompt, tools):
        contents = [
            types.Content(
                role=m["role"],
                parts=[types.Part(text=m["content"])]
            )
            for m in messages
        ]

        config = types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_prompt
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )

        result = {
            "message": response.candidates[0].content,
            "text": response.text,
            "tool_calls": []
        }

        if response.function_calls:
            for fc in response.function_calls:
                result["tool_calls"].append({
                    "name": fc.name,
                    "args": fc.args
                })
        print(result)
        return result
