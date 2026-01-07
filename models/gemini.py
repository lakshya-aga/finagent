from google.genai import types

class GeminiModel:
    def __init__(self, client, model="gemini-2.5-flash"):
        self.client = client
        self.model = model

    async def generate(self, messages, system_prompt, tools):
        contents = []
        for m in messages:
            # HARD NORMALIZATION

            text = m["content"]
            if not isinstance(text, str):
                text = str(text)

            contents.append(
                types.Content(
                    role=m["role"],
                    parts=[types.Part(text=text)]
                )
            )

        config = types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_prompt
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )

        text = response.text or ""

        result = {
            "message": response.candidates[0].content,
            "text": text,
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
