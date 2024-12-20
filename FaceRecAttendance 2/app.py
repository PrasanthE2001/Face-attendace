from flask import Flask, render_template, request, jsonify, Response
import cv2
import os
import numpy as np
from deepface import DeepFace
from datetime import datetime
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
# Path to store attendance records
attendance_file = "attendance.csv"
# Directory where student face images are stored
face_directory = "face/"
# Set a proper threshold for verification
THRESHOLD = 0.7
# Fixed location (latitude, longitude) for Thiruparankundram, Madurai
FIXED_LOCATION = (9.8815991, 78.0722379)

# Create an empty DataFrame with the required columns if not exists
if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name", "Time"])
    df.to_csv(attendance_file, index=False)
    logging.info(f"{attendance_file} created successfully!")

# Create CapturedImage directory if it doesn't exist
if not os.path.exists("CapturedImage"):
    os.makedirs("CapturedImage")
    logging.info("CapturedImage directory created successfully!")

app = Flask(__name__)

# Initialize video capture globally
camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def get_live_location():
    geolocator = Nominatim(user_agent="attendance_system")
    location = geolocator.geocode("Thiruparankundram, Madurai")  
    if location:
        return (location.latitude, location.longitude)
    return None

def is_within_location_range(live_location, fixed_location, threshold_km=0.5):
    if live_location is None:
        return False
    distance = geodesic(live_location, fixed_location).kilometers
    return distance <= threshold_km

def detect_glare(frame):
    # Convert frame to LAB color space to better analyze brightness
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # Threshold to find bright areas in the L channel (lightness)
    _, bright_areas = cv2.threshold(l_channel, 180, 255, cv2.THRESH_BINARY)
    
    # Find contours in the bright areas
    contours, _ = cv2.findContours(bright_areas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Check for significant contour areas
    significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 300]
    
    return significant_contours

def verify_against_student_images(captured_image_path, student_folder_path):
    best_match = None
    best_distance = float('inf')
    
    for image_name in os.listdir(student_folder_path):
        image_path = os.path.join(student_folder_path, image_name)
        try:
            match_result = DeepFace.verify(image_path, captured_image_path, enforce_detection=False)
            distance = match_result['distance']
            logging.info(f"Checking {image_name}: verified={match_result['verified']}, distance={distance}")
            
            if match_result['verified'] and distance < best_distance:
                best_distance = distance
                best_match = image_name
        except Exception as e:
            logging.error(f"Error verifying {image_name}: {str(e)}")

    logging.info(f"Best match: {best_match}, Best distance: {best_distance}")
    return best_match, best_distance

def capture_image():
    ret, frame = camera.read()
    if not ret:
        logging.error("Failed to grab frame")
        return None
    captured_image_path = os.path.join("CapturedImage", "captured_image.png")
    
    # Check for glare before saving the image
    if detect_glare(frame):
        logging.warning("Glare detected in the captured image.")
        return None

    cv2.imwrite(captured_image_path, frame)
    return captured_image_path

def mark_attendance(best_student_name):
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        if 'Name' not in df.columns or 'Time' not in df.columns:
            df = pd.DataFrame(columns=["Name", "Time"])
    else:
        df = pd.DataFrame(columns=["Name", "Time"])

    if not ((df['Name'] == best_student_name) & (df['Time'].str.contains(datetime.now().strftime("%Y-%m-%d")))).any():
        df = pd.concat([df, pd.DataFrame({"Name": [best_student_name], "Time": [current_time]})], ignore_index=True)
        df.to_csv(attendance_file, index=False)
        logging.info(f"Attendance marked for {best_student_name} at {current_time}")
        return f"Attendance marked for {best_student_name} at {current_time}."
    else:
        return f"{best_student_name}'s attendance is already marked today."

@app.route('/capture', methods=['POST'])
def capture():
    roll_number = request.json.get("rollNumber")  # Get the roll number from the request
    if not roll_number:
        return jsonify({"message": "Roll number not provided."}), 400

    captured_image_path = capture_image()
    if captured_image_path is not None:
        live_location = get_live_location()
        if is_within_location_range(live_location, FIXED_LOCATION):
            best_student_name = None
            best_distance = float('inf')

            # Check the respective roll number directory
            student_folder_path = os.path.join(face_directory, roll_number)
            if os.path.isdir(student_folder_path):
                best_match, distance = verify_against_student_images(captured_image_path, student_folder_path)
                if best_match and distance < THRESHOLD:
                    best_distance = distance
                    best_student_name = roll_number  # Set the student name as roll number

            if best_student_name:
                final_image_path = os.path.join("CapturedImage", f"{best_student_name}_captured_image.png")
                os.rename(captured_image_path, final_image_path)
                message = mark_attendance(best_student_name)
                return jsonify({"message": message})
            else:
                return jsonify({"message": "No match found. Attendance not marked."})
        else:
            return jsonify({"message": "Location verification failed. You are not in the allowed location."})
    return jsonify({"message": "Failed to capture image or glare detected."})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    # Extract the student's name from the filename
    student_name = os.path.splitext(file.filename)[0]
    student_folder_path = os.path.join(face_directory, student_name)

    # Create the student's folder if it doesn't exist
    if not os.path.exists(student_folder_path):
        os.makedirs(student_folder_path)

    # Save the file in the student's folder
    file_path = os.path.join(student_folder_path, file.filename)
    file.save(file_path)

    return jsonify({"message": f"File '{file.filename}' uploaded successfully to '{student_name}/'!"}), 200

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global camera
    if camera.isOpened():
        camera.release()  # Release the camera
        cv2.destroyAllWindows()  # Close any OpenCV windows
        logging.info("Camera and windows successfully released and closed.")
    else:
        logging.warning("Camera is not open.")
    return "Camera released and windows closed.", 200

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        logging.error(f"Error running the app: {e}")
        camera.release()
        cv2.destroyAllWindows()
