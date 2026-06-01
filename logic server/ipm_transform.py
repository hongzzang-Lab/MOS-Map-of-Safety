import numpy as np
import cv2
import os

class IPMTransformer:
    def __init__(self, matrix_path='ipm_matrix.npy'):
        """
        [Layer 2] 기하학적 분석을 위한 IPM 변환 클래스
        - 보고서 참조: 3.2.3 거리 추정 알고리즘
        """
        self.matrix_path = matrix_path
        self.matrix = None
        self.load_matrix()

    def load_matrix(self):
        """저장된 호모그래피 행렬(.npy) 로드"""
        if os.path.exists(self.matrix_path):
            try:
                self.matrix = np.load(self.matrix_path)
                print(f"✅ IPM Matrix 로드 완료: {os.path.basename(self.matrix_path)}")
            except Exception as e:
                print(f"❌ Matrix 파일 손상: {e}")
                self.matrix = None
        else:
            print(f"⚠️ 경고: '{self.matrix_path}' 파일이 없습니다. (더미 모드로 동작)")
            self.matrix = None

    def pixel_to_world(self, u, v):
        """
        [핵심 알고리즘] 2D 픽셀 좌표 -> 3D 실측 거리 변환
        :param u: 이미지 내 x좌표 (가로)
        :param v: 이미지 내 y좌표 (세로, 바닥 접점)
        :return: (real_x_cm, real_y_cm)
        """
        # 1. 행렬이 없으면 데모용 근사치 반환 (비상용)
        if self.matrix is None:
            # 화면 하단일수록 가깝다고 가정 (단순 비례)
            # 가정: 640x480 해상도
            fake_dist = (480 - v) * 1.5  # 픽셀당 1.5cm 가정
            fake_x = (u - 320) * 0.5     # 중앙에서의 편차
            return fake_x, fake_dist

        # 2. OpenCV Perspective Transform 적용
        # 입력 형태: (N, 1, 2)
        pixel_point = np.array([[[float(u), float(v)]]], dtype=np.float32)
        
        try:
            world_point = cv2.perspectiveTransform(pixel_point, self.matrix)
            real_x = world_point[0][0][0]
            real_y = world_point[0][0][1]
            return real_x, real_y
        except Exception as e:
            print(f"변환 오류: {e}")
            return 0.0, 0.0