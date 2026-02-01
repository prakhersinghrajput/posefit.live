import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import tempfile
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

st.set_page_config(page_title="AI Push-Up Counter", layout="centered")
st.title("💪 AI Push-Up Counter")
st.write("Use webcam OR upload a video")

# ---------------- Pose Setup ----------------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

# ---------------- Sidebar ----------------
mode = st.sidebar.radio("Choose Mode", ["Webcam (Live)", "Upload Video"])

# ================= WEBCAM MODE =================
class PushupCounter(VideoTransformerBase):
    def __init__(self):
        self.pose = mp_pose.Pose()
        self.counter = 0
        self.state = None
        self.last_rep_time = 0
        self.cooldown = 1.0

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image = cv2.resize(image, (640, 480))
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        try:
            landmarks = results.pose_landmarks.landmark

            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            if angle < 90:
                new_state = "DOWN"
            elif angle > 160:
                new_state = "UP"
            else:
                new_state = self.state

            current_time = time.time()
            if self.state == "DOWN" and new_state == "UP":
                if current_time - self.last_rep_time > self.cooldown:
                    self.counter += 1
                    self.last_rep_time = current_time

            self.state = new_state

            cv2.putText(image, f"Push-Ups: {self.counter}",
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 255, 0), 3)

        except:
            pass

        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        return image

if mode == "Webcam (Live)":
    st.subheader("📷 Live Webcam Push-Up Counter")
    webrtc_streamer(
        key="pushup",
        video_transformer_factory=PushupCounter,
        media_stream_constraints={"video": True, "audio": False}
    )

# ================= VIDEO UPLOAD MODE =================
if mode == "Upload Video":
    uploaded_video = st.file_uploader("📤 Upload Push-Up Video", type=["mp4", "avi", "mov"])

    if uploaded_video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        cap = cv2.VideoCapture(tfile.name)

        pose = mp_pose.Pose()
        counter = 0
        state = None
        last_rep_time = 0
        cooldown = 1.0

        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            try:
                landmarks = results.pose_landmarks.landmark

                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

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

                cv2.putText(frame, f"Push-Ups: {counter}",
                            (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 255, 0), 3)

            except:
                pass

        cap.release()
        st.success(f"✅ Total Push-Ups: {counter}")


