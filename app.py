import streamlit as st
import numpy as np
from PIL import Image
import imageio.v2 as imageio
import tempfile

st.set_page_config(page_title="PoseFit – Push-Up Counter", layout="centered")
st.title("💪 PoseFit – Push-Up Counter")
st.caption("Video-based motion analysis (Streamlit-safe version)")

uploaded_video = st.file_uploader(
    "📤 Upload a push-up video",
    type=["mp4", "mov", "avi"]
)

if uploaded_video:
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(uploaded_video.read())

    reader = imageio.get_reader(temp.name)

    prev_mean = None
    counter = 0
    direction = None

    frame_box = st.empty()

    for frame in reader:
        img = Image.fromarray(frame).resize((320, 240))
        gray = np.array(img.convert("L"))

        current_mean = gray.mean()

        if prev_mean is not None:
            diff = current_mean - prev_mean

            if diff < -2:
                new_dir = "DOWN"
            elif diff > 2:
                new_dir = "UP"
            else:
                new_dir = direction

            if direction == "DOWN" and new_dir == "UP":
                counter += 1

            direction = new_dir

        prev_mean = current_mean

        frame_box.image(
            img,
            caption=f"Push-Ups Counted: {counter}",
            use_column_width=True
        )

    st.success(f"✅ Total Push-Ups: {counter}")


