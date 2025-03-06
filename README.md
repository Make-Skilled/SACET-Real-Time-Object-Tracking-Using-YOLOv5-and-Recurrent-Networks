# 🏆 Real-Time Object Tracking Dashboard

A **Flask-based web application** that uses **YOLOv5 and Recurrent Networks** for real-time object detection and tracking. This dashboard provides **live object detection, image-based detection, detection history, and analytics**.

---

## 📌 Features
✔ **User Authentication** - Signup & Login  
✔ **Live Camera Feed** - Real-time object tracking using YOLOv5  
✔ **Image Upload Detection** - Detect objects from uploaded images  
✔ **Detection History** - View previously detected objects with date filters  
✔ **Analytics Dashboard** - Charts for detections over time & object breakdown  

---

## 🚀 Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/yourusername/real-time-object-tracking.git
cd real-time-object-tracking
```

### 2️⃣ **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Set Up YOLOv5**
```bash
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt
```

### 5️⃣ **Configure Database**
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 6️⃣ **Run the Flask App**
```bash
python backend/app.py
```
The app will be available at **http://127.0.0.1:9001/**.

---

## 📊 **Dashboard Overview**

### **Home Page**
- Project introduction
- Signup & Login buttons

### **Live Camera Feed**
- Uses **browser webcam** for real-time object detection.
- Implements **YOLOv5 & RNN for tracking**.

### **Image Upload Detection**
- Upload images for **object detection**.
- Uses trained **YOLOv5 model**.

### **Detection History**
- View all past detections.
- **Filter by date & object name**.
- **Pagination for browsing history**.

### **Analytics Dashboard**
- **Line Chart:** Detections over time.
- **Pie Chart:** Breakdown of detected objects.

---

## 📌 **API Endpoints**
| Endpoint              | Method | Description |
|----------------------|--------|-------------|
| `/signup`           | POST   | User signup |
| `/login`            | POST   | User login  |
| `/live_feed`        | GET    | Real-time camera feed |
| `/image_upload`     | POST   | Upload image for detection |
| `/history`          | GET    | View past detections |
| `/detection_summary`| GET    | Get total detections count |
| `/detection_trend`  | GET    | Detections per day |
| `/object_breakdown` | GET    | Object detection breakdown |

---

## 👨‍💻 **Contributing**
Pull requests are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`feature-new-feature`).
3. Commit your changes (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-new-feature`).
5. Open a Pull Request.

---

## 📜 **License**
This project is licensed under the **MIT License**.

---

## 📞 **Contact**
For questions, feel free to contact:
- 📧 Email: maddy@makeskilled.com
- 🔗 LinkedIn: [Your LinkedIn](https://linkedin.com/in/MadhuPIoT)
- 🌐 GitHub: [Your GitHub](https://github.com/maddydevgits)

---

### 🚀 **Happy Tracking!**
