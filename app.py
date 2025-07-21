import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="Realistic AI Interior Designer", layout="wide")

from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from concurrent.futures import ThreadPoolExecutor
import numpy as np

@st.cache_resource
def load_pipeline():
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except:
            st.warning("Xformers not available, using default attention")
    else:
        pipe.enable_attention_slicing()
    return pipe

pipe = load_pipeline()

DESIGN_STYLES = {
    "modern": "clean lines, minimalist, neutral colors, sleek furniture",
    "rustic": "natural wood, earthy tones, vintage accessories, cozy textures",
    "bohemian": "eclectic patterns, vibrant colors, indoor plants, layered textiles",
    "scandinavian": "light woods, white walls, functional furniture, minimal decor",
    "industrial": "exposed brick, metal accents, raw materials, leather furniture"
}

def resize_and_preserve_aspect_ratio(image, target_size=1024):
    """Resize image preserving aspect ratio with padding if needed"""
    width, height = image.size
    ratio = min(target_size/width, target_size/height)
    new_width, new_height = int(width*ratio), int(height*ratio)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create a white canvas with target dimensions
    result = Image.new("RGB", (target_size, target_size), (255, 255, 255))

    # Paste the resized image in the center
    offset_x = (target_size - new_width) // 2
    offset_y = (target_size - new_height) // 2
    result.paste(resized, (offset_x, offset_y))

    return result

@st.cache_data(max_entries=10, ttl=3600, show_spinner=False)
def generate_design(_pipe, image, style, style_desc, room_type, _strength=0.6, _guidance=7.5):
    # Preprocess image while preserving aspect ratio
    processed_image = resize_and_preserve_aspect_ratio(image)

    # Create base prompt with room type and style
    if room_type.lower() == "bedroom":
        prompt = f"a photorealistic {style} bedroom, {style_desc}, interior design. Keep as bedroom. Maintain the same room layout, architecture and function. Redesign with {style} bedroom furniture and decor. Keep bed as central feature. Keep the same window and door positions. 8k ultra HD photography, interior design magazine quality"
        negative_prompt = "cartoon, 3d render, illustration, drawing, painting, sketch, anime, unrealistic, distorted proportions, blurry, low quality, text, watermark, signature, deformed, living room, sofa, dining table, coffee table, tv stand, kitchen, stove, refrigerator, office, desk, chair, converting to living room, converting to kitchen, converting to office"
    elif room_type.lower() == "kitchen":
        prompt = f"a photorealistic {style} kitchen, {style_desc}, interior design. Keep as kitchen. Maintain the same room layout, architecture and function. Redesign with {style} kitchen furniture and decor. Keep countertops and appliances as central features. Keep the same window and door positions. 8k ultra HD photography, interior design magazine quality"
        negative_prompt = "cartoon, 3d render, illustration, drawing, painting, sketch, anime, unrealistic, distorted proportions, blurry, low quality, text, watermark, signature, deformed, bedroom, bed, living room, sofa, dining table, coffee table, tv stand, office, desk, chair, converting to bedroom, converting to living room, converting to office"
    elif room_type.lower() == "office":
        prompt = f"a photorealistic {style} office, {style_desc}, interior design. Keep as office. Maintain the same room layout, architecture and function. Redesign with {style} office furniture and decor. Keep desk and chair as central features. Keep the same window and door positions. 8k ultra HD photography, interior design magazine quality"
        negative_prompt = "cartoon, 3d render, illustration, drawing, painting, sketch, anime, unrealistic, distorted proportions, blurry, low quality, text, watermark, signature, deformed, bedroom, bed, living room, sofa, dining table, coffee table, tv stand, kitchen, stove, refrigerator, converting to bedroom, converting to living room, converting to kitchen"
    else:  # Living room/hall
        prompt = f"a photorealistic {style} living room, {style_desc}, interior design. Keep as living room. Maintain the same room layout, architecture and function. Redesign with {style} living room furniture and decor. Keep sofa/seating as central feature. Keep the same window and door positions. 8k ultra HD photography, interior design magazine quality"
        negative_prompt = "cartoon, 3d render, illustration, drawing, painting, sketch, anime, unrealistic, distorted proportions, blurry, low quality, text, watermark, signature, deformed, bedroom, bed, kitchen, stove, refrigerator, office, desk, chair, converting to bedroom, converting to kitchen, converting to office"

    try:
        # Different strength settings for more realistic results
        # Lower strength preserves more of the original image structure
        return _pipe(
            prompt=prompt,
            image=processed_image,
            strength=_strength,
            guidance_scale=_guidance,
            num_inference_steps=75,  # Increase steps for better quality
            negative_prompt=negative_prompt
        ).images[0]
    except Exception as e:
        st.error(f"Error generating {style} design: {str(e)}")
        return None

def main():
    st.title("📸 Realistic AI Interior Design Generator")
    st.markdown("""
    <style>
    .stProgress > div > div > div > div { background: #4CAF50 }
    div.stButton > button:first-child {background-color: #4CAF50; color:white;}
    div.stDownloadButton > button:first-child {background-color: #2196F3; color:white;}
    </style>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ How it works", expanded=True):
        st.markdown("""
        1. Upload or take a photo of your room
        2. Select the room type and design style
        3. Adjust the realism slider (lower = more realistic but subtle changes)
        4. Generate realistic interior design transformations
        5. Download your favorite designs
        """)

    # Input Selection
    col1, col2 = st.columns([2, 1])

    with col1:
        input_method = st.radio("Choose input method:",
                              ["Camera 📷", "Upload 📁"],
                              horizontal=True)

        image = None
        if input_method == "Camera 📷":
            img_file = st.camera_input("Take room photo", help="Capture well-lit room image")
        else:
            img_file = st.file_uploader("Upload room photo",
                                      type=["jpg", "jpeg", "png"])

    with col2:
        room_type = st.selectbox("Select room type:", ["Bedroom", "Hall (Living Room)", "Kitchen", "Office"])

        # Let user select styles from expanded options
        selected_styles = st.multiselect(
            "Select design styles (max 3):",
            list(DESIGN_STYLES.keys()),
            default=["modern", "rustic"],
            max_selections=3
        )

        # Realism control
        strength = st.slider(
            "Transformation strength:",
            min_value=0.3,
            max_value=0.8,
            value=0.5,
            step=0.05,
            help="Lower values preserve more of the original room (more realistic)"
        )

        guidance = st.slider(
            "Style guidance:",
            min_value=5.0,
            max_value=10.0,
            value=7.5,
            step=0.5,
            help="How strongly to apply the style (higher = stronger style elements)"
        )

    if img_file:
        image = Image.open(img_file).convert("RGB")
        st.image(image, caption=f"Your {room_type}", use_column_width=True)

        if not selected_styles:
            st.warning("Please select at least one design style")
        elif st.button("✨ Generate Designs", use_container_width=True):
            with st.spinner(f"Generating {len(selected_styles)} realistic designs (30-60 seconds)..."):
                progress_bar = st.progress(0)

                with ThreadPoolExecutor() as executor:
                    futures = {
                        executor.submit(
                            generate_design,
                            pipe,
                            image,
                            style,
                            DESIGN_STYLES[style],
                            room_type,
                            strength,
                            guidance
                        ): style for style in selected_styles
                    }

                    designs = []
                    for i, future in enumerate(futures):
                        style = futures[future]
                        try:
                            result = future.result()
                            if result:
                                designs.append((style, result))
                            progress_bar.progress((i + 1) / len(selected_styles))
                        except Exception as e:
                            st.error(f"{style} generation failed: {str(e)}")

                if designs:
                    st.success(f"Generated {len(designs)} realistic designs for your {room_type.lower()}!")

                    # For before/after comparison
                    with st.expander("Compare with original", expanded=True):
                        st.image(image, caption="Original Room", use_column_width=True)

                    # Display designs in a grid
                    cols = st.columns(min(len(designs), 3))
                    for i, (style, img) in enumerate(designs):
                        with cols[i % len(cols)]:
                            st.image(img,
                                   caption=f"{style.title()} {room_type} Style",
                                   use_column_width=True)
                            st.download_button(
                                f"Download {style} design",
                                data=img.tobytes(),
                                file_name=f"{style}-{room_type.lower()}-design.png",
                                mime="image/png",
                                use_container_width=True
                            )

                            # Add realism level information
                            st.caption(f"Transformation: {int(strength*100)}% | Style intensity: {int(guidance*10)}%")
                else:
                    st.error("Failed to generate any designs. Please try again with different settings.")

if __name__ == "__main__":
    main()