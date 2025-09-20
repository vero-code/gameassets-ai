import os
import fal_client
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    raise ValueError("FAL_KEY is missing! Please add it to your .env file.")

fal_client.api_key = FAL_KEY

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/flux-kontext/dev",
    arguments={
        "prompt": "Change the setting to a day time, add a lot of people walking the sidewalk while maintaining the same style of the painting",
        "image_url": "https://storage.googleapis.com/falserverless/example_inputs/kontext_example_input.webp"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)