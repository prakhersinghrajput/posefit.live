import streamlit as st
import mediapipe as mp
import numpy as np
from PIL import Image
import imageio.v2 as imageio
import tempfile
import time

# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="PoseFit – Push-Up Counter",
    layout="centered"
)

st.title("💪 PoseFit – AI Push-Up Counter")
st.caption("Upload a workout video. Cloud-safe version (no webcam).")

# ---------------- MediaPipe Setup ----------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# ---------------- Helper Function ----------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180 / np.pi)
    return 360 - angle if angle > 180 else angle

# ---------------- Video Upload ----------------
uploaded_video = st.file_uploader(
    "📤 Upload Push-Up Video",
    type=["mp4", "mov", "avi"]
)

if uploaded_video:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_video.read())

    reader = imageio.get_reader(temp_file.name)

    counter = 0
    state = None
    last_rep_time = 0
    cooldown = 1.0  # seconds

    frame_box = st.empty()

    for frame in reader:
        image = Image.fromarray(frame)
        img_rgb = np.array(image)

        results = pose.process(img_rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                        lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
            elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                     lm[mp_pose.PoseLandmark.LEFT_ELBOW].y]
            wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST].x,
                     lm[mp_pose.PoseLandmark.LEFT_WRIST].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            if angle < 90:
                new_state = "DOWN"
            elif angle > 160:
                new_state = "UP"
            else:
                new_state = state

            if state == "DOWN" and new_state == "UP":
                if time.time() - last_rep_time > cooldown:
                    counter += 1
                    last_rep_time = time.time()

            state = new_state

        frame_box.image(
            img_rgb,
            caption=f"Push-Ups Counted: {counter}",
            use_column_width=True
        )

    st.success(f"✅ Total Push-Ups: {counter}")


