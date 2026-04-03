import streamlit as st
import replicate
from PIL import Image

st.title("AI Object Replacer")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
prompt = st.text_input("What should replace the object?", "A cute robot")

if uploaded_file and st.button("Replace Object"):
    # This calls a hosted model on Replicate (SAM + Inpainting)
    output = replicate.run(
        "stability-ai/stable-diffusion-inpainting",
        input={
            "image": uploaded_file,
            "prompt": prompt,
            "mask": YOUR_MASK_LOGIC_HERE # You'd send a mask image here
        }
    )
    st.image(output)
