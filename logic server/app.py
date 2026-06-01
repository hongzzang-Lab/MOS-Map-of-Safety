import sys
import os
import threading
import time
import json
import cv2
from flask import Flask, render_template, jsonify, Response, request
from ultralytics import YOLO

# =========================================================
# [설정] 경로 및 모듈 설정
# =========================================================
# 현재 파일 위치 기준 (온보딩 지원)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)

# 사용자 모듈 임포트
from mapping_ui.map_engine import get_routes_from_osm
from path_planner import PathPlanner
from gemini_reasoner import GeminiReasoner
from ipm_transform import IPMTransformer

# ---------------------------------------------------------
# [모델 경로 설정] NCNN 우선 순위
# ---------------------------------------------------------
# 1. NCNN 모델 폴더 (가장 빠름)
NCNN_MODEL_DIR = os.path.join(BASE_DIR, "best_ncnn_model")
# 2. PyTorch 모델 파일 (백업용)
PT_MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
# 3. IPM 행렬 파일
IPM_MATRIX_PATH = os.path.join(BASE_DIR, "ipm_matrix.npy")

app = Flask(__name__, 
            template_folder=os.path.join(ROOT_DIR, 'mapping_ui', 'templates'),
            static_folder=os.path.join(ROOT_DIR, 'mapping_ui', 'static'))

# =========================================================
# [초기화] AI 및 알고리즘 엔진
# =========================================================
print("🧠 [System] M.O.S Logic Server Initializing...")

# 1. YOLO 모델 로드 (NCNN 우선)
model = None
using_ncnn = False
try:
    if os.path.exists(NCNN_MODEL_DIR):
        print(f"⚡ [Optimization] NCNN 모델 로드: {NCNN_MODEL_DIR}")
        # task='segment'를 명시해야 NCNN 포맷을 제대로 인식합니다.
        model = YOLO(NCNN_MODEL_DIR, task='segment')
        using_ncnn = True
    elif os.path.exists(PT_MODEL_PATH):
        print(f"⚠️ NCNN 모델 없음. PyTorch 모델 로드: {PT_MODEL_PATH}")
        model = YOLO(PT_MODEL_PATH)
    else:
        print("⚠️ 학습 모델 없음. 기본 모델(yolo11n-seg)을 다운로드하여 사용합니다.")
        model = YOLO("yolo11n-seg.pt")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")

# 2. 알고리즘 모듈 초기화
planner = PathPlanner()
ai_reasoner = GeminiReasoner()
ipm = IPMTransformer(IPM_MATRIX_PATH)

# 전역 변수
sensor_data = {'lat': 37.5447, 'lng': 126.9716, 'status': 'GPS Ready'}
persistent_objects = []
current_web_frame = None

# =========================================================
# [Vision Loop] NCNN 추론 + IPM 거리 계산
# =========================================================
def vision_loop():
    global current_web_frame, persistent_objects
    
    # 웹캠 연결 (0번) - 실패 시 시뮬레이션 모드(동영상) 고려 가능
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 웹캠 연결 실패. (카메라가 연결되어 있는지 확인하세요)")
        return

    print(f"📸 Vision 가동 (Engine: {'NCNN' if using_ncnn else 'PyTorch'}, IPM: {'ON' if ipm.matrix is not None else 'OFF'})")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
            
        if model:
            # 추론 (NCNN 사용 시 imgsz=640 권장)
            results = model.track(frame, persist=True, verbose=False, imgsz=640, conf=0.4)
            annotated_frame = results[0].plot()
            
            current_objects = []
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu()
                clss = results[0].boxes.cls.cpu().tolist()
                ids = results[0].boxes.id.int().cpu().tolist()
                
                for box, cls, uid in zip(boxes, clss, ids):
                    cls_name = model.names[int(cls)]
                    
                    # ---------------------------------------------------------
                    # [IPM 거리 계산]
                    # ---------------------------------------------------------
                    x1, y1, x2, y2 = box
                    cx = (x1 + x2) / 2
                    cy = y2  # 발바닥(지면 접촉점) 좌표
                    
                    # 픽셀 -> cm 변환
                    real_x_cm, real_y_cm = ipm.pixel_to_world(cx, cy)
                    
                    # m 단위 변환
                    dist_m = real_y_cm / 100.0
                    if dist_m < 0.1: dist_m = 0.1 
                    
                    current_objects.append({
                        "uid": uid,
                        "class": cls_name,
                        "dist": round(float(dist_m), 2),
                        "x_pos": round(float(real_x_cm), 2),
                        "last_seen": time.time()
                    })
                    
                    # 화면에 거리 표시
                    cv2.putText(annotated_frame, f"{dist_m:.1f}m", (int(x1), int(y1)-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            persistent_objects = current_objects
            
            # 웹 전송용 인코딩
            _, buf = cv2.imencode('.jpg', annotated_frame)
            current_web_frame = buf.tobytes()
            
            # NCNN 사용 여부 표시 (디버깅용)
            if using_ncnn:
                cv2.putText(annotated_frame, "Mode: NCNN Edge", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        else:
            _, buf = cv2.imencode('.jpg', frame)
            current_web_frame = buf.tobytes()
            
        time.sleep(0.03)

# =========================================================
# [API Endpoints]
# =========================================================
@app.route('/')
def index(): return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            if current_web_frame: 
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + current_web_frame + b'\r\n')
            time.sleep(0.05)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/get_routes', methods=['POST'])
def api_get_routes():
    d = request.json
    return jsonify({"routes": get_routes_from_osm((d['start']['lat'], d['start']['lng']), (d['end']['lat'], d['end']['lng']))})

@app.route('/api/check_passability')
def api_check_passability():
    return jsonify(planner.check_passability(persistent_objects))

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    # [수정 완료] 문법 오류 해결 및 안전한 문자열 포맷팅 적용
    # 리스트 컴프리헨션을 먼저 수행하고 문자열로 합침
    obj_list = [f"{o['class']}({o['dist']}m)" for o in persistent_objects]
    summary = f"탐지 객체: {obj_list}"
    
    return jsonify({"gemini": ai_reasoner.analyze_risk(request.json.get('width'), request.json.get('device'), summary)})

@app.route('/api/obstacles')
def api_obstacles(): return jsonify(persistent_objects)

@app.route('/api/status')
def api_status(): return jsonify(sensor_data)

@app.route('/api/start_nav', methods=['POST'])
def api_start_nav(): return jsonify({"status": "started"})

if __name__ == '__main__':
    t_vision = threading.Thread(target=vision_loop, daemon=True)
    t_vision.start()
    
    print(f"🚀 M.O.S Logic Server Started (http://localhost:5001)")
    print(f"📂 실행 위치: {BASE_DIR}")
    if using_ncnn:
        print("✅ [INFO] NCNN 최적화 모델이 활성화되었습니다.")
    
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)