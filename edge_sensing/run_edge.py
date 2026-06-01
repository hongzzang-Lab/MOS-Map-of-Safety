import os
import sys
import time
import cv2
from ultralytics import YOLO
from shared_mem_manager import SharedMemoryWriter

# =========================================================
# [설정] 경로 및 환경
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. NCNN 모델 경로 (최적화 모델 우선)
NCNN_MODEL_DIR = os.path.join(BASE_DIR, "best_ncnn_model")
PT_MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

def run_edge_inference():
    print("=================================================")
    print("🚀 M.O.S Edge Sensing Module (Real Hardware)")
    print("=================================================")

    # 1. 모델 로드 (NCNN > PT > Base)
    model = None
    using_ncnn = False
    
    try:
        if os.path.exists(NCNN_MODEL_DIR):
            print(f"⚡ [Optimization] NCNN 모델 로드: {NCNN_MODEL_DIR}")
            model = YOLO(NCNN_MODEL_DIR, task='segment')
            using_ncnn = True
        elif os.path.exists(PT_MODEL_PATH):
            print(f"ℹ️ PyTorch 모델 로드: {PT_MODEL_PATH}")
            model = YOLO(PT_MODEL_PATH)
        else:
            print("⚠️ 학습 모델 없음. 기본 모델(yolo11n-seg) 사용")
            model = YOLO("yolo11n-seg.pt")
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return

    # 2. 통신 모듈 초기화
    writer = SharedMemoryWriter()

    # 3. 실제 카메라 연결 (웹캠/CSI 카메라)
    # 라즈베리 파이에서는 보통 0번 인덱스가 연결된 카메라입니다.
    cap = cv2.VideoCapture(0)
    
    # 카메라 연결 실패 시 즉시 종료 (하드웨어 문제 알림)
    if not cap.isOpened():
        print("❌ [Error] 카메라를 찾을 수 없습니다.")
        print("   >> 라즈베리 파이 카메라 연결 상태를 확인하세요.")
        print("   >> 'libcamera-hello' 등으로 카메라가 켜지는지 확인하세요.")
        return

    print(f"📸 실시간 탐지 시작 (Engine: {'NCNN' if using_ncnn else 'PyTorch'})")
    print("   >> Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ 프레임 읽기 실패 (카메라 연결 끊김?)")
            break

        # 4. 추론 (Inference)
        # 엣지에서는 추적만 수행, 무거운 후처리는 최소화
        results = model.track(frame, persist=True, verbose=False, imgsz=640, conf=0.4)
        
        # 5. 데이터 패킹 (서버 전송용 경량 데이터)
        detected_data = []
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu()
            clss = results[0].boxes.cls.cpu().tolist()
            ids = results[0].boxes.id.int().cpu().tolist()

            for box, cls, uid in zip(boxes, clss, ids):
                detected_data.append({
                    "id": uid,
                    "cls": model.names[int(cls)],
                    "bbox": [int(x) for x in box] # [x1, y1, x2, y2]
                })

        # 6. Shared Memory로 전송 (IPC)
        writer.write(detected_data)

        # 7. 디버깅용 화면 출력 (Headless 환경이면 try-except로 무시)
        try:
            annotated_frame = results[0].plot()
            if using_ncnn:
                cv2.putText(annotated_frame, "Mode: NCNN Real", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("M.O.S Edge View", annotated_frame)
            if cv2.waitKey(1) == ord('q'):
                break
        except:
            pass # GUI가 없는 환경에서는 에러 무시하고 백그라운드 실행

    cap.release()
    cv2.destroyAllWindows()
    writer.close()
    print("🛑 시스템 종료")

if __name__ == "__main__":
    run_edge_inference()