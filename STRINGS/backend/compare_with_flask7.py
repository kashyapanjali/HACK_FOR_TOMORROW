from flask import Flask, request, render_template, jsonify, send_file
import cv2
import numpy as np
import mediapipe as mp
import os
import time
from scipy.spatial.distance import cosine
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Initialize MediaPipe Pose with higher confidence thresholds
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Define important keypoints for pose comparison
IMPORTANT_KEYPOINTS = [
    11, 12,  # shoulders
    13, 14,  # elbows
    15, 16,  # wrists
    23, 24,  # hips
    25, 26,  # knees
    27, 28   # ankles
]

# Define body parts for more intuitive feedback
BODY_PARTS = {
    0: "Right Arm",
    1: "Left Arm",
    2: "Right Leg",
    3: "Left Leg"
}

# Function to extract pose keypoints with normalized coordinates
def extract_keypoints(frame):
    results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if not results.pose_landmarks:
        return None
    
    keypoints = np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                          for lm in results.pose_landmarks.landmark])
    
    hip_center = (keypoints[23][:3] + keypoints[24][:3]) / 2
    normalized_keypoints = keypoints.copy()
    
    for i in range(len(normalized_keypoints)):
        normalized_keypoints[i][:3] = normalized_keypoints[i][:3] - hip_center
    
    return normalized_keypoints

# Function to calculate joint angles
def calculate_angles(keypoints):
    if keypoints is None:
        return None
    
    angles = []
    
    v1 = keypoints[11][:3] - keypoints[13][:3]
    v2 = keypoints[15][:3] - keypoints[13][:3]
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    angles.append(angle)
    
    v1 = keypoints[12][:3] - keypoints[14][:3]
    v2 = keypoints[16][:3] - keypoints[14][:3]
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    angles.append(angle)
    
    v1 = keypoints[23][:3] - keypoints[25][:3]
    v2 = keypoints[27][:3] - keypoints[25][:3]
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    angles.append(angle)
    
    v1 = keypoints[24][:3] - keypoints[26][:3]
    v2 = keypoints[28][:3] - keypoints[26][:3]
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    angles.append(angle)
    
    return np.array(angles)

# Function to calculate multi-metric similarity
def calculate_similarity(kp1, kp2):
    if kp1 is None or kp2 is None:
        return 0
    
    position_similarity = 0
    visible_count = 0
    
    for idx in IMPORTANT_KEYPOINTS:
        if kp1[idx][3] > 0.5 and kp2[idx][3] > 0.5:
            dist = np.linalg.norm(kp1[idx][:3] - kp2[idx][:3])
            position_similarity += np.exp(-dist * 5)
            visible_count += 1
    
    if visible_count == 0:
        return 0
    
    position_similarity /= visible_count
    
    angles1 = calculate_angles(kp1)
    angles2 = calculate_angles(kp2)
    
    if angles1 is None or angles2 is None:
        angle_similarity = 0
    else:
        angle_similarity = 1 - cosine(angles1, angles2)
        if np.isnan(angle_similarity):
            angle_similarity = 0
    
    vec1 = np.concatenate([kp1[idx][:3] for idx in IMPORTANT_KEYPOINTS])
    vec2 = np.concatenate([kp2[idx][:3] for idx in IMPORTANT_KEYPOINTS])
    
    vector_similarity = 1 - cosine(vec1, vec2) if not np.isnan(vec1).any() and not np.isnan(vec2).any() else 0
    if np.isnan(vector_similarity):
        vector_similarity = 0
    
    final_similarity = (0.5 * position_similarity + 
                        0.3 * angle_similarity + 
                        0.2 * vector_similarity)
    
    return final_similarity

# Simplified graph function showing bar chart with timestamps
def generate_comparison_graphs(aligned_similarities, angle_diffs_over_time, path, fps2):
    plt.figure(figsize=(15, 5))
    
    low_similarity_data = [(i, j, sim) for (i, j), sim in zip(path, aligned_similarities) if sim < 0.7]
    if not low_similarity_data:
        plt.text(0.5, 0.5, "No significant differences found!", 
                 ha='center', va='center', fontsize=14, color='green')
        plt.axis('off')
    else:
        timestamps = [f"{int(j / fps2 // 60)}:{int(j / fps2 % 60):02d}" for _, j, _ in low_similarity_data]
        similarities = [sim for _, _, sim in low_similarity_data]
        
        bars = plt.bar(range(len(similarities)), similarities, color=[
            '#f39c12' if s >= 0.4 else '#e74c3c' for s in similarities
        ])
        
        plt.xticks(range(len(timestamps)), timestamps, rotation=45)
        plt.xlabel('Time (minutes:seconds)', fontsize=12)
        plt.ylabel('Match Score (0-1)', fontsize=12)
        plt.title('Where Your Dance Needs Work', fontsize=14)
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3)
        
        plt.legend(handles=[
            plt.Rectangle((0,0),1,1, color='#f39c12', label='Needs Work (0.4-0.7)'),
            plt.Rectangle((0,0),1,1, color='#e74c3c', label='Big Difference (<0.4)')
        ], loc='upper right')
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

@app.route('/')
def index():
    return render_template('index7.html')

@app.route('/compare', methods=['POST'])
def compare_videos():
    if 'video1' not in request.files or 'video2' not in request.files:
        return jsonify({"error": "Both video files are required"}), 400

    video1 = request.files['video1']  # Reference video
    video2 = request.files['video2']  # User video

    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    timestamp = int(time.time())
    video1_path = os.path.join('uploads', f"{timestamp}_1_{video1.filename}")
    video2_path = os.path.join('uploads', f"{timestamp}_2_{video2.filename}")
    
    try:
        video1.save(video1_path)
        video2.save(video2_path)
    except Exception as e:
        return jsonify({"error": f"File saving error: {str(e)}"}), 500

    try:
        cap1 = cv2.VideoCapture(video1_path)
        cap2 = cv2.VideoCapture(video2_path)

        if not cap1.isOpened() or not cap2.isOpened():
            return jsonify({"error": "Could not open video files"}), 400

        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        
        seq1 = []
        seq2 = []
        
        while True:
            ret, frame = cap1.read()
            if not ret:
                break
            frame = cv2.resize(frame, (640, 480))
            keypoints = extract_keypoints(frame)
            if keypoints is not None:
                seq1.append(keypoints)
        
        while True:
            ret, frame = cap2.read()
            if not ret:
                break
            frame = cv2.resize(frame, (640, 480))
            keypoints = extract_keypoints(frame)
            if keypoints is not None:
                seq2.append(keypoints)
        
        if len(seq1) < 5 or len(seq2) < 5:
            return jsonify({"error": "Videos too short or no poses detected"}), 400
        
        def pose_distance(pose1, pose2):
            if pose1 is None or pose2 is None:
                return 1
            similarity = calculate_similarity(pose1, pose2)
            return 1 - similarity

        distance, path = fastdtw(seq1, seq2, dist=pose_distance)
        
        aligned_similarities = []
        angle_diffs_over_time = []

        for i, j in path:
            sim = calculate_similarity(seq1[i], seq2[j])
            aligned_similarities.append(sim)

            angles1 = calculate_angles(seq1[i])
            angles2 = calculate_angles(seq2[j])
            if angles1 is not None and angles2 is not None:
                angle_diffs = np.abs(angles1 - angles2)
                angle_diffs_over_time.append(angle_diffs)
            else:
                angle_diffs_over_time.append(np.zeros(4))

        angle_diffs_over_time = np.array(angle_diffs_over_time)
        
        overall_accuracy = np.mean(aligned_similarities) * 100
        
        # Generate concise, point-wise feedback without duplicates
        low_similarity_pairs = [(i, j, sim) for (i, j), sim in zip(path, aligned_similarities) if sim < 0.7]
        feedback_dict = {}  # Dictionary to store unique feedback per timestamp
        
        for i, j, sim in low_similarity_pairs:
            angles1 = calculate_angles(seq1[i])
            angles2 = calculate_angles(seq2[j])
            if angles1 is None or angles2 is None:
                continue

            angle_diffs = angles2 - angles1
            timestamp = f"{int(j / fps2 // 60)}:{int(j / fps2 % 60):02d}"
            if timestamp not in feedback_dict:
                feedback_dict[timestamp] = []
            
            for k in range(4):
                diff = angle_diffs[k]
                if abs(diff) > 0.35:
                    body_part = BODY_PARTS[k].lower()
                    if diff > 0:
                        advice = f"Bend {body_part}"
                    else:
                        advice = f"Lift {body_part}"
                    # Only add if not already present for this timestamp
                    if advice not in [item[1] for item in feedback_dict[timestamp]]:
                        feedback_dict[timestamp].append((abs(diff), advice))

        # Build detailed feedback, keeping highest magnitude per unique advice
        detailed_feedback = []
        for ts in sorted(feedback_dict.keys()):
            # Sort by magnitude and take unique advice
            items = sorted(feedback_dict[ts], reverse=True)  # Largest diff first
            seen_advice = set()
            for _, advice in items:
                if advice not in seen_advice:
                    seen_advice.add(advice)
                    detailed_feedback.append(f"{ts}: {advice}")
        
        # Simplified improvement areas
        avg_angle_diffs = np.mean(angle_diffs_over_time, axis=0)
        worst_body_part_idx = np.argmax(avg_angle_diffs)
        
        angle_diffs_for_worst = [angles2[k] - angles1[k] for i, j in path 
                                 if (angles1 := calculate_angles(seq1[i])) is not None 
                                 and (angles2 := calculate_angles(seq2[j])) is not None 
                                 for k in [worst_body_part_idx]]
        avg_diff_worst = np.mean(angle_diffs_for_worst) if angle_diffs_for_worst else 0

        worst_body_part = BODY_PARTS[worst_body_part_idx]
        if avg_diff_worst > 0:
            body_part_advice = f"Keep your {worst_body_part.lower()} straighter"
        else:
            body_part_advice = f"Bend your {worst_body_part.lower()} more"

        consistency_std = np.std(aligned_similarities)
        if consistency_std > 0.15:
            consistency_advice = "Your timing needs slight improvement"
        else:
            consistency_advice = "Your movements are mostly consistent"

        improvement_areas = [body_part_advice, consistency_advice]
        
        # Generate simplified graph
        graph_buffer = generate_comparison_graphs(aligned_similarities, angle_diffs_over_time, path, fps2)
        
        graph_path = os.path.join('uploads', f"comparison_graph_{timestamp}.png")
        with open(graph_path, 'wb') as f:
            f.write(graph_buffer.getbuffer())
        
        result = {
            "accuracy": f"{overall_accuracy:.2f}%",
            "improvement_areas": improvement_areas,
            "detailed_feedback": detailed_feedback,
            "graph_url": f"/get_graph/{timestamp}"
        }

    except Exception as e:
        result = {"error": f"Processing error: {str(e)}"}
    
    finally:
        if 'cap1' in locals() and cap1.isOpened():
            cap1.release()
        if 'cap2' in locals() and cap2.isOpened():
            cap2.release()

        try:
            if os.path.exists(video1_path):
                os.remove(video1_path)
            if os.path.exists(video2_path):
                os.remove(video2_path)
        except Exception as e:
            print(f"Error removing temporary files: {str(e)}")

    return jsonify(result)

@app.route('/get_graph/<timestamp>')
def get_graph(timestamp):
    graph_path = os.path.join('uploads', f"comparison_graph_{timestamp}.png")
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    else:
        return "Graph not found", 404

def cleanup_old_files():
    current_time = time.time()
    for filename in os.listdir('uploads'):
        file_path = os.path.join('uploads', filename)
        if os.path.isfile(file_path):
            if current_time - os.path.getmtime(file_path) > 3600:
                os.remove(file_path)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)