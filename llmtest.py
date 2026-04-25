from ollama import generate, chat
from tqdm import tqdm
import requests
import json

max_tokens = 100

PROMPT = "Tell me something about the sky, why is it blue?" 
stream = generate(model="llama3.2", prompt = PROMPT, stream=True, options={'num_predict': max_tokens})
pbar = tqdm(total=max_tokens, unit=" tokens", desc="Generating")

full_response = ""
generated_tokens = 0

for chunk in stream:
    if generated_tokens < max_tokens:
        pbar.update(1)
        generated_tokens += 1

    full_response += chunk.get('response', '')

    if chunk.get('done'):
        pbar.n = generated_tokens
        pbar.refresh()
        break

pbar.close()

print(full_response)
