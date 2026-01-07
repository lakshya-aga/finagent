from call_functions import call_function
class AgentEvent:
    def __init__(self, type, content):
        self.type = type      # "thought", "tool", "code", "stdout", "stderr", "final"
        self.content = content


class CodingAgent:
    def __init__(self, model_client, tools, system_prompt, max_iters=20):
        self.model = model_client
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iters = max_iters
        self.messages = []

    async def run(self, user_prompt):
        self.messages = [{"role": "user", "content": user_prompt}]
        yield AgentEvent("thought", "Agent started")

        for _ in range(self.max_iters):
            response = await self.model.generate(
                messages=self.messages,
                system_prompt=self.system_prompt,
                tools=self.tools
            )
            self.messages.append({"role": "model", "content": response["message"]})
            # response = response["message"]
            if response.get("tool_calls"):
                for function_call in response.get("tool_calls"):
                    yield AgentEvent("tool",
                        f"Calling function: {function_call['name']} "
                        f"{[
                            f'{k}: {v[:100] + "..." if len(v) > 100 else v}'
                            for k, v in function_call['args'].items()
                        ]}"
                    )

                    function_call_result = call_function(function_call)
                    self.messages.append({"role": "model", "content": str(function_call_result)})
                    
                    yield AgentEvent("tool_result", function_call_result)
            else:
                yield AgentEvent("final", response["text"])
                return
