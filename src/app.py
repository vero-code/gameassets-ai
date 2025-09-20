import gradio as gr
import os
import fal_client
from dotenv import load_dotenv
from PIL import Image
import requests
import io
import tempfile

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    raise ValueError("FAL_KEY is missing! Please add it to your .env file.")

fal_client.api_key = FAL_KEY

def generate_asset(input_image: Image.Image, prompt_text: str):
    """
    Sends an image and prompt to the FAL API and returns the result.
    """
    if input_image is None:
        raise gr.Error("Please upload the source image!")
    if not prompt_text:
        raise gr.Error("Please enter a text prompt!")

    print("Input data verified. Starting generation...")

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            input_image.save(tmp_file, "PNG")
            tmp_file_path = tmp_file.name
        
        print(f"Image saved to temporary file: {tmp_file_path}")
        image_url = fal_client.upload_file(tmp_file_path)
        print(f"Image uploaded, URL obtained: {image_url}")

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            print("The temporary file has been deleted.")

    try:
        print("Sending a request to the FAL API...")
        result = fal_client.run(
            "fal-ai/flux-kontext/dev",
            arguments={
                "prompt": prompt_text,
                "image_url": image_url
            }
        )
        print("API response received.")

        output_image_url = result['images'][0]['url']
        print(f"Result URL received: {output_image_url}")

        response = requests.get(output_image_url)
        response.raise_for_status()

        output_image = Image.open(io.BytesIO(response.content))
        print("The resulting image has been processed successfully.")

        return output_image

    except Exception as e:
        print(f"An error occurred: {e}")
        raise gr.Error(f"An error occurred while generating: {e}")

# --- Gradio interface---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # GameAssets AI ⚔️
        *AI-powered forge for indie developers. Upload a base sprite and instantly create endless fantasy variations.*
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="Base Sprite")
            prompt_input = gr.Textbox(
                label="Prompt",
                placeholder="e.g., a magic sword made of ice and crystals"
            )
            generate_button = gr.Button("Generate!", variant="primary")

        with gr.Column(scale=1):
            image_output = gr.Image(label="Result")

    generate_button.click(
        fn=generate_asset,
        inputs=[image_input, prompt_input],
        outputs=image_output,
        api_name="generate"
    )


if __name__ == "__main__":
    demo.launch()