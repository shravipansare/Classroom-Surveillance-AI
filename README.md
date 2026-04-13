# 🧠 Intelligent Classroom Surveillance System (ICSS) 🎓📹🤖

The **Intelligent Classroom Surveillance System (ICSS)** is an AI-powered real-time classroom monitoring solution designed to enhance **attendance tracking, classroom discipline, and student well-being**.

ICSS uses **Computer Vision + Deep Learning** to:

✅ Detect & recognize students from a live camera/CCTV feed  
✅ Analyze student **stress levels** using facial expressions  
✅ Detect **prohibited activities** such as mobile phone usage  
✅ Display results in a clean GUI dashboard and maintain logs in Excel

---

## 🎯 Project Objective

Traditional classroom monitoring is manual and cannot continuously track:
- Student presence/attendance
- Student discipline (mobile usage)
- Student emotional state/stress level

✅ **ICSS automates these tasks using AI** and provides real-time monitoring support for teachers and institutions.

---

## ✨ Key Features

### 👁️ Face Detection
- Real-time face detection using **OpenCV**
- Supports multiple faces simultaneously

### 🧑‍🎓 Face Recognition
- Recognizes students using a pre-generated dataset
- Displays **Name + Roll Number**
- Reads student data from `student_monitoring.xlsx`

### 😟 Stress Detection
- Uses CNN deep learning model `emotion_model.h5`
- Classifies students as:
  - **Stressed**
  - **Not Stressed**
- Logs stress status in the monitoring sheet

### 📱 Mobile Phone Detection
- Identifies mobile usage inside classroom environment
- Raises an alert with student identity
- Logs activity in monitoring records

### 🖥️ Student Monitoring Dashboard (GUI)
- Tkinter-based UI
- Live camera feed display
- Student list with:
  - Attendance
  - Stress Status
  - Mobile Status
- Present & stressed count summary

---

## 🧠 Core Working Concept (System Workflow)

ICSS works in real time using the following pipeline:

1. **Live Camera Feed Input**
2. **Frame Processing using OpenCV**
3. **Face Detection** → locate faces in frame
4. **Face Recognition** → identify student (name + roll no.)
5. **Stress Detection** → CNN model predicts stress
6. **Mobile Detection** → checks restricted object usage
7. **Dashboard Output + Excel Logging**

### ✅ High Level Flow

```text
Camera Feed → Face Detection → Face Recognition → Stress Detection → Mobile Detection
                        ↓                 ↓                 ↓              ↓
                    Student ID        Attendance        Stress Status   Alert/Log
                        ↓________________________________________________________
                                         Dashboard + Excel Records
```

🗂️ Project Structure
```bash
ICSS/
│── images/                            # Student images dataset
│── emotion_model.h5                   # Pretrained stress detection model
│── main.py                            # Main UI / system launcher
│── monitoring_system.py               # Core monitoring logic
│── student_attendance.xlsx            # Attendance records
│── student_attendance1.xlsx           # Additional monitoring logs
│── student_monitoring.xlsx            # Student database (Name + Roll No)
│── requirements.txt                   # Python dependencies
│── Screenshot (47).png                # Project UI screenshots
│── Screenshot (50).png
│── Screenshot 2025-04-23 104636.png
│── README.md
```
🛠️ Tech Stack

| Component            | Technology               |
| -------------------- | ------------------------ |
| **Language**         | Python                   |
| **Computer Vision**  | OpenCV                   |
| **Face Recognition** | face-recognition Library |
| **Deep Learning**    | TensorFlow, Keras        |
| **UI Framework**     | Tkinter                  |
| **Data Handling**    | Pandas                   |
| **Image Processing** | Pillow                   |

📦 Installation

1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ICSS.git
cd ICSS
```

2️⃣ Create Virtual Environment (optional)
```bash
python -m venv venv
venv/Scripts/activate   # Windows
```

3️⃣ Install Dependencies

Make sure your requirements.txt contains:
```bash
tensorflow==2.12.0
keras==2.12.0
opencv-python==4.7.0.72
face-recognition==1.3.0
numpy==1.24.3
pandas==1.5.3
pillow==9.5.0

```
Install all packages:
```bash
pip install -r requirements.txt
```

▶️ How to Run

Start the Classroom Monitoring System:
```bash
python main.py
```
Make sure to:

✔ Add student images inside the images/ folder

✔ Ensure the Excel files contain correct student names & roll numbers

✔ Keep emotion_model.h5 in the root directory
## Screenshots

![ICSS Dashboard](Screenshot%20(47).png)

![ICSS Live Monitoring Output](Screenshot%20(50).png)




