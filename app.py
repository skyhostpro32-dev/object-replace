import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io

# ... (your API/Title code above) ...

if uploaded_file:
    # --- FIX START ---
    # Load and force convert image to RGB (prevents URL conversion errors)
    img = Image.open(uploaded_file).convert("RGB")
    
    # Resize image if it's too huge (prevents the canvas from crashing)
    MAX_WIDTH = 600
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (MAX_WIDTH, int(img.height * ratio))
        img = img.resize(new_size)
    # --- FIX END ---

    st.write("Step 2: Paint over the object you want to replace")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1.0)",
        stroke_width=20,
        stroke_color="#FFFFFF",
        background_image=img,  # Now passing the cleaned/resized image
        update_streamlit=True,
        height=img.height,
        width=img.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    prompt = st.text_input("Step 3: What should the new object be?", "a rubber duck")

    if st.button("Replace Object"):
        if canvas_result.image_data is not None:
            # Get the mask from the alpha channel of the canvas
            mask_data = canvas_result.image_data[:, :, 3] 
            mask_image = Image.fromarray(mask_data.astype(np.uint8))
            
            # Convert images to Bytes for Replicate API
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            mask_byte_arr = io.BytesIO()
            mask_image.save(mask_byte_arr, format='PNG')

            with st.spinner("AI is working..."):
                try:
                    output = replicate.run(
                        "stability-ai/stable-diffusion-inpainting:95b71c21",
                        input={
                            "image": img_byte_arr,
                            "mask": mask_byte_arr,
                            "prompt": prompt,
                        }
                    )
                    st.image(output[0], caption="Result")
                except Exception as e:
                    st.error(f"AI Error: {e}")
