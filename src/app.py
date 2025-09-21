import gradio as gr
import os
import fal_client
from dotenv import load_dotenv
from PIL import Image
import requests
import io
import tempfile
import time

# --- DEBUG MODE ---
# Set to False to use the real FAL API.
DEBUG_MODE = False

# --- FAL API Setup ---
if not DEBUG_MODE:
    load_dotenv()
    FAL_KEY = os.getenv("FAL_KEY")
    if not FAL_KEY:
        raise ValueError("FAL_KEY is missing! Please add it to your .env file.")
    fal_client.api_key = FAL_KEY

STYLE_MODIFIERS = {
    "Fiery": "made of fire, lava, and embers",
    "Icy": "made of ice, frost, and crystals",
    "Ancient": "ancient, covered in moss and vines, weathered stone",
    "Magic": "glowing with magical energy, ethereal, enchanted runes",
}

# --- Dummy Data for Debugging ---
DUMMY_IMAGES = [
    "assets/shield.png",
    "assets/mace.png",
    "assets/potion.png",
    "assets/boots.png"
]
for p in DUMMY_IMAGES:
    if not os.path.exists(p):
        raise FileNotFoundError(f"Debug image not found: {p}. Please make sure it's in the assets folder.")

def upload_image_to_fal(image: Image.Image) -> str:
    """Saves the image, uploads it to FAL, and returns the URL."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            image.save(tmp_file, "PNG")
            tmp_file_path = tmp_file.name
        image_url = fal_client.upload_file(tmp_file_path)
        print(f"Image uploaded: {image_url}")
        return image_url
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# --- Generation of one img -> Single Image ---
def generate_asset(input_image: Image.Image, prompt_text: str):
    """
    Sends an image and prompt to the FAL API and returns the result.
    """
    if input_image is None: raise gr.Error("Please upload the source image!")
    if not prompt_text: raise gr.Error("Please enter a text prompt!")

    if DEBUG_MODE:
        print("DEBUG MODE: Simulating single image generation.")
        time.sleep(1)
        return Image.open(DUMMY_IMAGES[0])

    image_url = upload_image_to_fal(input_image)

    try:
        result = fal_client.run("fal-ai/flux-kontext/dev", arguments={"prompt": prompt_text, "image_url": image_url})
        output_url = result['images'][0]['url']
        response = requests.get(output_url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        raise gr.Error(f"An error occurred while generating: {e}")

# --- Generation of options -> Inspiration Mode ---
def generate_variations(input_image: Image.Image, base_prompt_text: str):
    """
    Generates multiple asset variants based on a base prompt and modifiers.
    """
    if input_image is None: raise gr.Error("Please upload the source image!")
    if not base_prompt_text: raise gr.Error("Please enter a base prompt (e.g., 'a sword')!")

    if DEBUG_MODE:
        print("DEBUG MODE: Simulating variations generation.")
        time.sleep(2)
        return [Image.open(p) for p in DUMMY_IMAGES]

    image_url = upload_image_to_fal(input_image)
    output_images = []

    for style_name, style_prompt in STYLE_MODIFIERS.items():
        full_prompt = f"{base_prompt_text}, {style_prompt}"
        print(f"Generating '{style_name}'...")
        
        try:
            result = fal_client.run("fal-ai/flux-kontext/dev", arguments={"prompt": full_prompt, "image_url": image_url})
            output_url = result['images'][0]['url']
            response = requests.get(output_url)
            response.raise_for_status()
            output_images.append(Image.open(io.BytesIO(response.content)))
        except Exception as e:
            print(f"Error generating variant '{style_name}': {e}")
            pass

    if not output_images: raise gr.Error("Unable to create any variants.")
    return output_images

# --- Main function-dispatcher ---
def master_generate(mode: str, image: Image.Image, prompt: str):
    """Calls the required function depending on the selected mode."""
    if mode == "Single Image":
        single_result = generate_asset(image, prompt)
        return {
            gallery_output: gr.update(visible=False),
            single_output: gr.update(value=single_result, visible=True)
        }
    else: # "Inspiration Mode"
        variations_result = generate_variations(image, prompt)
        return {
            single_output: gr.update(visible=False),
            gallery_output: gr.update(value=variations_result, visible=True)
        }

# --- Gradio interface ---
with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
    gr.Markdown(
        """
        # GameAssets AI ⚔️ *AI-powered forge for indie developers. Upload a base sprite and instantly create endless fantasy variations.*
        """
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=450):
            image_input = gr.Image(type="pil", label="Base Sprite", height=480)
            
            with gr.Group():
                mode_selector = gr.Radio(
                    ["Single Image", "Inspiration Mode"],
                    label="Generation Mode",
                    value="Inspiration Mode" # Default
                )
                prompt_input = gr.Textbox(
                    label="Base Prompt",
                    placeholder="e.g., a pixel art sword",
                    lines=2
                )
            
            generate_button = gr.Button("Generate Variations!", variant="primary")

            gr.Examples(
                examples=[
                    ["assets/shield.png", "an ancient pixel art shield with ornament"],
                    ["assets/mace.png", "a heavy spiked mace, fantasy weapon"],
                    ["assets/potion.png", "a magic potion bottle, bubbling with poison"],
                    ["assets/boots.png", "a pair of ornate leather boots, fantasy armor"],
                ],
                inputs=[image_input, prompt_input],
                label="Click an example to start",
                examples_per_page=4
            )
        
        with gr.Column(scale=2, min_width=600):
            single_output = gr.Image(label="Result", visible=False, show_label=False, height=480)
            gallery_output = gr.Gallery(
                label="Variations", columns=2, object_fit="contain", visible=True, show_label=False, height=480
            )

    # --- Dynamic UI update ---
    def update_ui_on_mode_change(mode: str):
        if mode == "Single Image":
            return {
                prompt_input: gr.update(label="Full Prompt", placeholder="e.g., a sword made of fire and lava"),
                generate_button: gr.update(value="Generate!"),
                single_output: gr.update(visible=True),
                gallery_output: gr.update(visible=False),
            }
        else: # Inspiration Mode
            return {
                prompt_input: gr.update(label="Base Prompt", placeholder="e.g., a pixel art sword"),
                generate_button: gr.update(value="Generate Variations!"),
                single_output: gr.update(visible=False),
                gallery_output: gr.update(visible=True),
            }

    # --- Application logic ---
    mode_selector.change(
        fn=update_ui_on_mode_change,
        inputs=mode_selector,
        outputs=[prompt_input, generate_button, single_output, gallery_output]
    )

    generate_button.click(
        fn=master_generate,
        inputs=[mode_selector, image_input, prompt_input],
        outputs=[single_output, gallery_output]
    )


if __name__ == "__main__":
    demo.launch()