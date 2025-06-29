from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Assuming your Ollama server is running locally on port 11434.
ollama_model_client = OllamaChatCompletionClient(model="llama3.2")

import asyncio

async def main():
	response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
	print(response)
	await ollama_model_client.close()

asyncio.run(main())
