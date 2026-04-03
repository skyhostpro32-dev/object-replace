import streamlit as st
from streamlit_drawable_canvas import st_canvas
import replicate
from PIL import Image
import numpy as np
import io
import os

st.set_page_config(page_title="Pro Eraser & Replacer", layout="wide")

# API Configuration
if "r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI" in st.secrets:
    os.environ["r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI"] = st.secrets["r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI"]
else:
    api_key = st.sidebar.text_input("r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI", type="password")
    if api_key: os.environ["r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI"] = api_key

st.title("Magic Object Replacer ✨")

# 1. Upload & Pre-process
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Essential for 2026 browsers: Force RGB and consistent size
    base_img = Image.open(uploaded_file).convert("RGB")
    if base_img.width > 800:
        base_img = base_img.resize((800, int(base_img.height * (800 / base_img.width))))

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Edit Area")
        mode = st.radio("Tool Mode:", ["Fast Draft (Tier 1)", "Pro Polish (Tier 2)"], horizontal=True)
        
        # Interactive Canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 1.0)",
            stroke_width=30,
            stroke_color="#FFFFFF",
            background_image=base_img,
            update_streamlit=True,
            height=base_img.height,
            width=base_img.width,
            drawing_mode="freedraw",
            key="pro_canvas",
        )

    prompt = st.text_input("What should the AI put here?", "solid background")

    if st.button("Generate Result"):
        if not os.environ.get("REPLICATE_API_TOKEN"):
            st.error("Please add your Replicate API Token.")
        elif canvas_result.image_data is not None:
            with st.spinner("Processing..."):
                # Prepare Mask
                mask_data = canvas_result.image_data[:, :, 3] 
                mask_img = Image.fromarray(mask_data.astype(np.uint8))
                
                # Convert to bytes for API
                img_buf, mask_buf = io.BytesIO(), io.BytesIO()
                base_img.save(img_buf, format="PNG")
                mask_img.save(mask_buf, format="PNG")

                # TIERED LOGIC
                if mode == "Fast Draft (Tier 1)":
                    # SDXL-Lightning: Ultra fast 4-step generation
                    model = "stability-ai/sdxl-lightning-4step:72a15f0d"
                    params = {"image": img_buf, "mask": mask_buf, "prompt": prompt}
                else:
                    # Flux Fill: Professional 2026 Standard (High Detail)
                    model = "black-forest-labs/flux-fill-pro"
                    params = {
                        "image": img_buf, "mask": mask_buf, "prompt": prompt,
                        "guidance_scale": 3.5, "num_inference_steps": 28
                    }

                try:
                    output = replicate.run(model, input=params)
                    with col2:
                        st.subheader("Result")
                        st.image(output[0])
                        st.balloons()
                except Exception as e:
                    st.error(f"AI Error: {e}")
