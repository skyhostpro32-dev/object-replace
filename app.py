import streamlit as st
from streamlit_drawable_canvas import st_canvas
import replicate
from PIL import Image
import numpy as np
import os

st.title("Object Replacer 🎨")

# 1. Setup API Key (Get this from replicate.com/account)
# You can also set this in Streamlit Cloud Secrets
os.environ["REPLICATE_API_TOKEN"] = st.sidebar.text_input("Replicate API Token", type="password")

uploaded_file = st.file_uploader("Step 1: Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    
    st.write("Step 2: Paint over the object you want to replace")
    
    # 2. Create a canvas for masking
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1.0)",  # Fixed white for mask
        stroke_width=20,
        stroke_color="#FFFFFF",
        background_image=img,
        update_streamlit=True,
        height=img.height * (600 / img.width), # Scale to fit screen
        width=600,
        drawing_mode="freedraw",
        key="canvas",
    )

    prompt = st.text_input("Step 3: What should the new object be?", "a rubber duck")

    if st.button("Replace Object"):
        if not os.environ.get("r8_QEkYb4q3CjxxuRmS1c6jINrmiOKCUXK3lXJGI"):
            st.error("Please enter your Replicate API Token in the sidebar!")
        elif canvas_result.image_data is not None:
            # 3. Process the mask
            mask_data = canvas_result.image_data[:, :, 3] # Get Alpha channel
            mask_image = Image.fromarray(mask_data.astype(np.uint8))
            
            with st.spinner("AI is working..."):
                # 4. Call Replicate (Using Stable Diffusion Inpainting)
                # We convert images to temporary files or bytes for the API
                output = replicate.run(
                    "stability-ai/stable-diffusion-inpainting:95b71c21",
                    input={
                        "image": uploaded_file,
                        "mask": mask_image,
                        "prompt": prompt,
                    }
                )
                st.image(output[0], caption="Result")
