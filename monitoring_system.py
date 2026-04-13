import cv2
import face_recognition
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import tkinter as tk
from tkinter import Label, Button, Frame, ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import os
import traceback
import urllib.request
from tensorflow.keras.optimizers import Adam
import openpyxl

# Modern color scheme
COLORS = {
    'background': '#2D3748',
    'primary': '#4299E1',
    'secondary': '#ED8936',
    'success': '#48BB78',
    'danger': '#F56565',
    'text': '#E2E8F0',
    'card': '#4A5568',
    'header': '#1A202C'
}

class MonitoringSystem:
    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
        self.root.title("Classroom Monitoring System")
        
        # Configuration
        self.images_dir = "images"
        self.excel_file = "student_attendance.xlsx"
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        # Initialize components
        self.setup_ui()
        self.load_student_images()
        self.load_models()
        self.initialize_excel()
        
    def setup_ui(self):
        self.root.configure(bg=COLORS['background'])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS['background'])
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Video Feed Section
        video_container = tk.Frame(self.main_frame, bg=COLORS['header'], bd=0)
        video_container.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        video_header = tk.Label(video_container, 
                              text="🎥 Live Classroom Feed",
                              font=('Helvetica', 16, 'bold'),
                              bg=COLORS['header'],
                              fg=COLORS['text'],
                              pady=10)
        video_header.pack(fill='x')
        
        self.video_frame = tk.Label(video_container, 
                                   bg='black', 
                                   bd=2, 
                                   relief='groove')
        self.video_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(video_container, bg=COLORS['header'])
        button_frame.pack(fill='x', pady=(0, 10), padx=10)
        
        self.start_button = tk.Button(button_frame,
                                    text="▶ Start Monitoring",
                                    command=self.start_monitoring,
                                    font=('Helvetica', 12),
                                    bg=COLORS['success'],
                                    fg='white',
                                    relief='flat',
                                    padx=10,
                                    pady=8)
        self.start_button.pack(side='left', expand=True, fill='x', padx=5)
        
        self.stop_button = tk.Button(button_frame,
                                   text="⏹ Stop",
                                   command=self.stop_monitoring,
                                   font=('Helvetica', 12),
                                   bg=COLORS['danger'],
                                   fg='white',
                                   relief='flat',
                                   padx=10,
                                   pady=8)
        self.stop_button.pack(side='left', expand=True, fill='x', padx=5)
        
        self.status_indicator = tk.Label(video_container,
                                       text="● System Ready",
                                       font=('Helvetica', 12),
                                       bg=COLORS['header'],
                                       fg=COLORS['success'])
        self.status_indicator.pack(fill='x', pady=(0, 10))
        
        # Dashboard Section
        dashboard_container = tk.Frame(self.main_frame, bg=COLORS['card'], bd=0)
        dashboard_container.grid(row=0, column=1, sticky='nsew')
        
        dashboard_header = tk.Label(dashboard_container, 
                                 text="📊 Student Status Dashboard",
                                 font=('Helvetica', 16, 'bold'),
                                 bg=COLORS['header'],
                                 fg=COLORS['text'],
                                 pady=10)
        dashboard_header.pack(fill='x')
        
        # Stats cards
        stats_frame = tk.Frame(dashboard_container, bg=COLORS['card'])
        stats_frame.pack(fill='x', pady=(10, 5), padx=10)
        
        self.stats_cards = {
            'present': self.create_stat_card(stats_frame, "Present", "0", COLORS['success']),
            'stressed': self.create_stat_card(stats_frame, "Stressed", "0", COLORS['danger'])
        }
        
        # Student table
        table_frame = tk.Frame(dashboard_container, bg=COLORS['card'])
        table_frame.pack(expand=True, fill='both', pady=(5, 10), padx=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                      background=COLORS['card'],
                      foreground=COLORS['text'],
                      fieldbackground=COLORS['card'],
                      rowheight=28,
                      font=('Helvetica', 10))
        style.configure("Treeview.Heading",
                       background=COLORS['header'],
                       foreground=COLORS['text'],
                       font=('Helvetica', 11, 'bold'))
        
        self.tree = ttk.Treeview(table_frame,
                                columns=('ID', 'Name', 'Attendance', 'Stress Status'),
                                show='headings')
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Attendance', text='Attendance')
        self.tree.heading('Stress Status', text='Stress Status')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=COLORS['header'], padx=10, pady=5)
        card.pack(side='left', expand=True, fill='x', padx=5)
        
        tk.Label(card,
               text=title,
               font=('Helvetica', 10),
               bg=COLORS['header'],
               fg=COLORS['text']).pack(anchor='w')
        
        value_label = tk.Label(card,
                             text=value,
                             font=('Helvetica', 18, 'bold'),
                             bg=COLORS['header'],
                             fg=color)
        value_label.pack(anchor='w')
        
        return value_label
    
    def load_student_images(self):
        """Load all student images from the images folder"""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            messagebox.showinfo("Info", f"Created {self.images_dir} folder. Please add student images.")
            return
            
        for filename in os.listdir(self.images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Extract ID and Name from filename (format: ID_Name.jpg)
                    student_id, student_name = os.path.splitext(filename)[0].split('_', 1)
                    image_path = os.path.join(self.images_dir, filename)
                    
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(student_name)
                        self.known_face_ids.append(student_id)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def load_models(self):
        """Load emotion recognition model"""
        try:
            if not os.path.exists("emotion_model.h5"):
                self.download_model()
                
            self.emotion_model = load_model("emotion_model.h5", compile=False)
            optimizer = Adam(learning_rate=0.0001)
            self.emotion_model.compile(optimizer=optimizer, loss='categorical_crossentropy')
            print("✅ Models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.show_error("Failed to load models")
            traceback.print_exc()
            exit()

    def download_model(self):
        MODEL_URL = "https://github.com/oarriaga/face_classification/raw/master/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5"
        try:
            print("Downloading emotion model...")
            urllib.request.urlretrieve(MODEL_URL, "emotion_model.h5")
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Failed to download model: {e}")
            raise

    def initialize_excel(self):
        """Create empty Excel file with headers if it doesn't exist"""
        if not os.path.exists(self.excel_file):
            df = pd.DataFrame(columns=[
                'ID', 
                'Name', 
                'Attendance', 
                'Stress Status',
                'Timestamp'
            ])
            df.to_excel(self.excel_file, index=False, engine='openpyxl')

    def process_frame(self, frame):
        try:
            # Resize for processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Face detection
            face_locations = face_recognition.face_locations(rgb_small_frame)
            
            # Skip if no faces found
            if not face_locations:
                return frame
                
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up
                top *= 4; right *= 4; bottom *= 4; left *= 4
                
                # Face recognition
                try:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    if True in matches:
                        match_index = matches.index(True)
                        student_id = self.known_face_ids[match_index]
                        student_name = self.known_face_names[match_index]
                        
                        # Emotion detection
                        face_roi = frame[top:bottom, left:right]
                        if face_roi.size > 0:
                            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                            gray_face = cv2.resize(gray_face, (64, 64))
                            gray_face = gray_face / 255.0
                            gray_face = np.expand_dims(gray_face, axis=-1)
                            gray_face = np.expand_dims(gray_face, axis=0)
                            
                            emotion_pred = self.emotion_model.predict(gray_face, verbose=0)
                            emotion_index = np.argmax(emotion_pred)
                            
                            # Simplified stress detection
                            is_stressed = emotion_index in [0, 1, 4]  # Angry, Fear, Sad
                            stress_status = "Stressed" if is_stressed else "Not Stressed"
                            
                            # Update Excel only for recognized students
                            self.update_attendance(
                                student_id,
                                student_name,
                                "Present",
                                stress_status,
                                current_time
                            )
                            
                            # Draw visualization
                            color = (0, 0, 255) if is_stressed else (0, 255, 0)
                            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                            cv2.putText(frame, f"{student_name} - {stress_status}", (left, top-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                except Exception as e:
                    print(f"Error in face processing: {e}")
                    continue
            
            return frame
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame

    def update_attendance(self, student_id, name, attendance, stress_status, timestamp):
        """Update Excel with student data only if recognized"""
        try:
            # Read existing data or create new DataFrame
            try:
                df = pd.read_excel(self.excel_file, engine='openpyxl')
            except:
                df = pd.DataFrame(columns=['ID', 'Name', 'Attendance', 'Stress Status', 'Timestamp'])
            
            # Append new record
            new_data = {
                'ID': [student_id],
                'Name': [name],
                'Attendance': [attendance],
                'Stress Status': [stress_status],
                'Timestamp': [timestamp]
            }
            
            df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
            df.to_excel(self.excel_file, index=False, engine='openpyxl')
            
            # Update the table display
            self.update_table()
            
        except Exception as e:
            print(f"Error updating attendance: {e}")

    def update_display(self):
        if self.stop_flag or self.video_capture is None:
            return

        ret, frame = self.video_capture.read()
        if ret:
            frame = self.process_frame(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=img)
            self.video_frame.config(image=img)
            self.video_frame.image = img

        self.root.after(10, self.update_display)

    def update_table(self):
        try:
            df = pd.read_excel(self.excel_file, engine='openpyxl')
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get latest status for each student
            latest_status = df.sort_values('Timestamp').groupby('ID').last().reset_index()
            
            # Update stats cards
            present_count = len(latest_status[latest_status['Attendance'] == 'Present'])
            stressed_count = len(latest_status[latest_status['Stress Status'] == 'Stressed'])
            
            self.stats_cards['present'].config(text=str(present_count))
            self.stats_cards['stressed'].config(text=str(stressed_count))
            
            # Update table
            for idx, row in latest_status.iterrows():
                self.tree.insert('', 'end', values=(
                    row['ID'],
                    row['Name'],
                    row['Attendance'],
                    row['Stress Status']
                ))
            
            if self.tree.get_children():
                self.tree.see(self.tree.get_children()[-1])
            
        except Exception as e:
            print(f"Error updating table: {e}")

    def start_monitoring(self):
        try:
            self.stop_flag = False
            self.video_capture = cv2.VideoCapture(0)
            
            if self.video_capture.isOpened():
                self.status_indicator.config(text="● Monitoring Active", fg=COLORS['success'])
                self.update_display()
            else:
                self.show_error("Camera not available")
        except Exception as e:
            print(f"Error starting monitoring: {e}")
            self.show_error("System error")

    def stop_monitoring(self):
        self.stop_flag = True
        if self.video_capture:
            self.video_capture.release()
        self.status_indicator.config(text="● System Ready", fg=COLORS['success'])

    def show_error(self, message):
        self.status_indicator.config(text=f"● Error: {message}", fg=COLORS['danger'])

    def run(self):
        self.root.mainloop()

def create_monitoring_system(root_window=None):
    return MonitoringSystem(root_window)

if __name__ == "__main__":
    app = MonitoringSystem()
    app.run()