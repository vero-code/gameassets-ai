import gradio as gr
import time

def generate_asset_placeholder(input_image, prompt_text):
    """
    Placeholder function to simulate asset generation.
    """
    print("Image received. Type:", type(input_image))
    print("Prompt received:", prompt_text)

    if input_image is None:
        raise gr.Error("Please upload the original image!")

    print("Simulating generation...")
    time.sleep(2)
    print("Generation complete.")

    return input_image

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
        fn=generate_asset_placeholder,
        inputs=[image_input, prompt_input],
        outputs=image_output,
        api_name="generate"
    )


if __name__ == "__main__":
    demo.launch()