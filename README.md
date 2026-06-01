<<<<<<< HEAD
# M.O.S (Map Of Safety) - 프로젝트 README

##  프로젝트 개요
**M.O.S (Map Of Safety)**는 보행 약자(휠체어 사용자, 고령자 등)를 위한 **AI 기반 능동형 안전 내비게이션 시스템**입니다.
엣지 디바이스(Raspberry Pi 5)에서의 실시간 위험 탐지와 생성형 AI(Gemini)를 활용한 지능형 경로 추천 기술이 결합되어 있습니다.

---

## 📂 프로젝트 디렉토리 구조

본 프로젝트는 기능별로 4개의 주요 모듈로 구성되어 있습니다.

Project_Root/
│
├── edge_sensing/              # [Layer 1] 엣지 디바이스 (Raspberry Pi 5)
│   ├── run_edge.py            # 엣지 메인 실행 파일 (NCNN 최적화 적용)
│   ├── id_lock_tracker.py     # 거리 기반 객체 추적 알고리즘
│   ├── shared_mem_manager.py  # IPC (프로세스 간 통신) 모듈
│   └── best_ncnn_model/       # NCNN 변환된 모델 폴더
│
├── logic server/              # [Layer 2 & 3] 로직 분석 및 AI 서버
│   ├── app.py                 # Flask 메인 서버 (UI, AI, Vision 통합)
│   ├── path_planner.py        # 기하학적 통과 가능성 분석 (수선의 발 공식)
│   ├── gemini_reasoner.py     # 생성형 AI (LLM) 위험 분석 모듈
│   ├── ipm_transform.py       # IPM 좌표 변환 (2D 픽셀 -> 3D 실측 거리)
│   └── ipm_matrix.npy         # 호모그래피 행렬 파일
│
├── mapping_ui/                # [Layer 4] 사용자 인터페이스 & 매핑
│   ├── map_engine.py          # OSMnx 기반 경로 탐색 엔진
│   ├── templates/             # HTML 프론트엔드 (index.html)
│   ├── static/                # CSS 스타일시트
│   └── routes_cache.json      # 경로 데이터 캐시 파일
│
└── Data_Processing/           # [DataOps] 데이터셋 전처리 및 분석
    ├── data_analysis_processing.json # 클래스 불균형 분석 도구 + 전처리 
     
=======
# M.O.S-Map-of-Safety
>>>>>>> 62e91f27744f01b73c0941846ac3b6e2bb208ad0
