

---
## MOS-Map-of-Safety

```md
# M.O.S: Map of Safety

교통약자와 보행자를 위한 실시간 위험 감지 기반 안전 경로 추천 시스템입니다.

## Project Overview

M.O.S는 Map of Safety의 약자로, 보행자 또는 교통약자가 이동 중 마주칠 수 있는 위험 요소를 실시간으로 감지하고, 지도 기반으로 안전 경로를 추천하는 프로젝트입니다.

본 프로젝트는 OSMnx 기반 도보 경로 계산, YOLO 기반 객체 탐지, IPM 기반 거리 추정, Gemini 기반 위험 분석, Flask 기반 웹 서버를 결합하여 안전한 이동 판단을 지원하는 것을 목표로 합니다.

## Features

- OSMnx 기반 도보 경로 계산
- 경로 캐싱을 통한 반복 실행 최적화
- Flask 기반 로직 서버
- YOLO 기반 실시간 객체 탐지
- NCNN 모델 기반 Edge 추론 지원
- IPM 기반 픽셀 좌표 → 실제 거리 변환
- PathPlanner 기반 통과 가능성 판단
- Gemini 기반 위험 분석 및 경로 추천
- 웹 UI 연동을 위한 API 제공

## Tech Stack

- Python
- Flask
- OpenCV
- YOLO / Ultralytics
- NCNN
- OSMnx
- NetworkX
- Gemini API
- HTML / CSS / JavaScript
- Jupyter Notebook

## Directory Structure

```text
MOS-Map-of-Safety/
│
├─ Data_Processing/
│   └─ data preprocessing codes
│
├─ edge_sensing/
│   └─ edge sensing and runtime codes
│
├─ logic server/
│   ├─ app.py
│   ├─ path_planner.py
│   ├─ gemini_reasoner.py
│   ├─ ipm_transform.py
│   ├─ id_lock_tracker.py
│   └─ shared_mem_manager.py
│
├─ mapping_ui/
│   ├─ map_engine.py
│   ├─ templates/
│   └─ static/
│
├─ requirement.txt
└─ README.md
