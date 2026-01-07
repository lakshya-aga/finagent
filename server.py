from fastapi import FastAPI, WebSocket
from agent.core import CodingAgent
from models.gemini import GeminiModel
from call_functions import available_functions
from prompts import system_prompt
from google import genai
import os

app = FastAPI()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
model = GeminiModel(client)

agent = CodingAgent(
    model_client=model,
    tools=available_functions,
    system_prompt=system_prompt
)

@app.websocket("/terminal")
async def terminal(ws: WebSocket):
    await ws.accept()
    user_prompt = await ws.receive_text()

    async for event in agent.run(user_prompt):
        await ws.send_json({
            "type": event.type,
            "content": event.content
        })
