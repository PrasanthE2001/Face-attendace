# Face Recognition Attendance System

This project implements a Face Recognition Attendance System using Flask, OpenCV, and DeepFace. The system captures student images via a webcam, verifies their identity against pre-stored face images, and marks their attendance based on face recognition.

### Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

### Features

- **Real-time Face Recognition**: Uses webcam input to capture and verify student faces.
- **Attendance Tracking**: Records attendance in a CSV file.
- **Location Verification**: Ensures students are within a designated area before marking attendance.
- **Image Upload**: Allows for uploading student face images for initial setup.
- **User-Friendly Interface**: Simple HTML interface for interactions.

### Technologies Used

- **Flask**: Web framework for Python to handle web requests and serve content.
- **OpenCV**: Library for image processing and computer vision.
- **DeepFace**: Python library for face recognition and analysis.
- **Pandas**: For handling attendance records in CSV format.
- **Geopy**: For location verification based on GPS coordinates.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Face-Recognition-Attendance-System.git
   cd Face-Recognition-Attendance-System

2. Set Up a Virtual Environment (Optional but recommended) using bash #Command prompt:

**python -m venv venv
**source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install Required Packages using bash #Command prompt:

**pip install -r requirements.txt

4. Set Up Directories: Ensure that you have the following directory structure:

Face-Recognition-Attendance-System/
├── face/                # Directory to store student face images
├── CapturedImage/       # Directory to store captured images
├── attendance.csv       # Attendance records
├── app.py               # Main application file
├── static/              # Static files (CSS, JS)
│   ├── style.css
│   └── script.js
└── templates/           # HTML templates
    └── index.html

- **face/: Directory where student face images are stored.
- **CapturedImage/: Directory to store the captured images for attendance marking.
- **attendance.csv: CSV file that logs attendance with student names and timestamps.
- **app.py: The main application script where Flask server is defined.
- **static/: Contains static files such as stylesheets and JavaScript files.
- **templates/: Contains HTML files for rendering the user interface.


5. Ensure You Have a Webcam: This system uses a webcam for capturing student images.

### USAGE:

1. Run the Application in command prompt:
    python app.py

2. Access the Application: Open a web browser and go to http://127.0.0.1:5000/.

3. Upload Student Images: Use the provided input field to upload student face images.

4. Capture and Verify: Click the "Capture and Verify" button to start the webcam, capture an image, and verify the student's identity.

5. Shutdown: To stop the camera and release resources, use the "Shutdown Camera" button.

### CONTRIBUTIONS:

1. **Contributions are welcome! If you have suggestions or improvements, feel free to fork the repository and create a pull request.

### How to Use the README

1. **Clone or Copy**: You can clone this README file into your project directory.
2. **Update Links**: If you are using a version control system like GitHub, update the repository link in the "Clone the Repository" section with your actual repository URL.
3. **License**: If you have a license file, ensure you mention the correct license type or provide the license file as indicated.

Feel free to modify any sections as needed to better fit your project! Let me know if you need further assistance.