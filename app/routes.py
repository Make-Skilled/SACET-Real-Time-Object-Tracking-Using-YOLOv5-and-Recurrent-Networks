from flask import Flask, request, jsonify, render_template, session, redirect, url_for,Response,send_file,send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from dbmodels import User, DetectionHistory
from datetime import datetime

import cv2
import torch
import numpy as np
import os
from collections import defaultdict


if not os.path.exists("yolov5"):
    os.system("git clone https://github.com/ultralytics/yolov5.git")

# ✅ Change directory to YOLOv5 and load model correctly
yolo_path = os.path.join(os.getcwd(), "yolov5")
model = torch.hub.load(yolo_path, 'custom', path=yolo_path + '/yolov5s.pt', source='local')

CORS(app)  # Allow frontend API requests

def extract_detected_objects(results, confidence_threshold=0.5):
    """Extract object names from YOLOv5 detection results with a confidence threshold."""
    object_names = set()
    for det in results.xyxy[0]:  # Bounding box detections
        confidence = float(det[4])  # Confidence score is in the 5th column
        if confidence >= confidence_threshold:
            class_id = int(det[-1])  # Last column is class ID
            object_name = model.names[class_id]  # Get object name
            object_names.add(object_name)
    return ", ".join(object_names)


# Serve Frontend Pages
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup')
def signup_page():
    return render_template("signup.html")

@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))  # Redirect if not logged in
    user = User.query.get(session['user_id'])  # Fetch user details
    return render_template("dashboard.html", username=user.username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create new user
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id  # Store user ID in session
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/live_feed')
def live_feed():
    """Live feed page for browser-based camera streaming."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))  # Redirect if not logged in
    return render_template("live_feed.html")

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Receives video frames from the browser, processes them with YOLOv5, stores, and returns the detected frame."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    file = request.files['video_frame']
    if file:
        user_id = session['user_id']
        
        # Convert frame to OpenCV format
        np_img = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Process frame with YOLOv5
        results = model(frame)
        detected_objects = extract_detected_objects(results, confidence_threshold=0.5)
        detected_frame = results.render()[0]

        # Save files
        frame_filename = f"frame_{user_id}_{int(datetime.utcnow().timestamp())}.jpg"
        detected_filename = f"detected_{frame_filename}"

        frame_path = os.path.join(app.config['UPLOAD_FOLDER'], frame_filename)
        detected_path = os.path.join(app.config['UPLOAD_FOLDER'], detected_filename)

        cv2.imwrite(frame_path, frame)
        cv2.imwrite(detected_path, detected_frame)

        # Store in database
        if detected_objects:  # Only save if objects were detected
            detection = DetectionHistory(
                user_id=user_id,
                image_filename=frame_filename,
                detected_filename=detected_filename,
                detected_objects=detected_objects
            )
            db.session.add(detection)
            db.session.commit()

        # Send detected frame
        _, buffer = cv2.imencode('.jpg', detected_frame)
        return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/image_upload')
def image_upload():
    """Render Image Upload Page."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template("image_upload.html")

@app.route('/process_image', methods=['POST'])
def process_image():
    """Receives an image, processes it using YOLOv5, stores, and returns the detected image."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    file = request.files['image']
    if file:
        user_id = session['user_id']
        original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        detected_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "detected_" + file.filename)

        # Save original image
        file.save(original_filepath)

        # Process image with YOLOv5
        img = cv2.imread(original_filepath)
        results = model(img)
        detected_objects = extract_detected_objects(results, confidence_threshold=0.5)
        detected_img = results.render()[0]

        # Save detected image
        cv2.imwrite(detected_filepath, detected_img)

        # Store detection in database
        if detected_objects:  # Only save if objects were detected
            detection = DetectionHistory(
                user_id=user_id,
                image_filename=file.filename,
                detected_filename="detected_" + file.filename,
                detected_objects=detected_objects
            )
            db.session.add(detection)
            db.session.commit()

        return send_file(detected_filepath, mimetype='image/jpeg')

@app.route('/history', methods=['GET'])
def history():
    """Render History Page with Date Filter, Object Search, and Pagination."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Get filter values
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    search_object = request.args.get('search_object', '')

    # Base query
    query = DetectionHistory.query.filter_by(user_id=user_id)

    # Apply date filter
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(DetectionHistory.timestamp >= start, DetectionHistory.timestamp <= end)
        except ValueError:
            pass

    # Apply object search
    if search_object:
        query = query.filter(DetectionHistory.detected_objects.ilike(f"%{search_object}%"))

    detections = query.order_by(DetectionHistory.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # Fetch all unique detected object names
    unique_objects = set()
    all_detections = DetectionHistory.query.filter_by(user_id=user_id).all()
    for detection in all_detections:
        if detection.detected_objects:
            unique_objects.update(detection.detected_objects.split(', '))  # Convert comma-separated values to set

    return render_template("history.html", detections=detections, start_date=start_date, end_date=end_date, search_object=search_object, unique_objects=sorted(unique_objects))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve files from the 'uploads' folder."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/detection_summary')
def detection_summary():
    """API to return total detections and total objects detected."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    
    # Count total detections
    total_detections = DetectionHistory.query.filter_by(user_id=user_id).count()
    
    # Count total detected objects
    total_objects = 0
    all_detections = DetectionHistory.query.filter_by(user_id=user_id).all()
    for detection in all_detections:
        if detection.detected_objects:
            total_objects += len(detection.detected_objects.split(', '))  # Count individual object names
    
    return jsonify({
        "total_detections": total_detections,
        "total_objects": total_objects
    })

@app.route('/detection_trend')
def detection_trend():
    """API to return daily detection count."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    
    # Count detections per day
    detections_per_day = defaultdict(int)
    all_detections = DetectionHistory.query.filter_by(user_id=user_id).all()
    
    for detection in all_detections:
        date = detection.timestamp.strftime('%Y-%m-%d')  # Extract date only
        detections_per_day[date] += 1
    
    return jsonify({
        "dates": list(detections_per_day.keys()),
        "counts": list(detections_per_day.values())
    })

@app.route('/object_breakdown')
def object_breakdown():
    """API to return counts of each detected object type."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    
    # Count occurrences of each detected object
    object_counts = defaultdict(int)
    all_detections = DetectionHistory.query.filter_by(user_id=user_id).all()
    
    for detection in all_detections:
        if detection.detected_objects:
            objects = detection.detected_objects.split(', ')  # Convert to list
            for obj in objects:
                object_counts[obj] += 1  # Count object occurrences
    
    return jsonify({
        "objects": list(object_counts.keys()),
        "counts": list(object_counts.values())
    })