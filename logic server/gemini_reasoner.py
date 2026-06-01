import google.generativeai as genai
import json
import math

# [설정] API 키 (제출 시 빈칸으로 두거나, 환경 변수 사용 권장)
# 심사위원이 실행할 때는 본인의 키를 넣어야 할 수도 있음
DEFAULT_API_KEY = ""

class GeminiReasoner:
    def __init__(self, api_key=None):
        key = api_key if api_key else DEFAULT_API_KEY
        self.model = None
        self._configure_model(key)

    def _configure_model(self, api_key):
        try:
            genai.configure(api_key=api_key)
            # 1순위: Flash Lite (빠름)
            self.model = genai.GenerativeModel('gemini-1.5-flash') 
            print("✅ Gemini AI 모듈 로드 성공")
        except Exception as e:
            print(f"⚠️ Gemini 연결 실패: {e}")

    def analyze_risk(self, user_width, device_type, obstacles_summary):
        """
        [데모 코드 로직 이식]
        경로상의 장애물 정보를 바탕으로 Gemini에게 분석 요청
        """
        if not self.model:
            return {"analysis": "AI 모델이 연결되지 않았습니다.", "recommended_idx": 0}

        prompt = f"""
        보행 약자 네비게이션 AI로서 경로를 추천해줘.
        사용자: {device_type} (폭 {user_width}cm)
        
        [실시간 탐지 데이터 요약]
        {obstacles_summary}
        
        [규칙]
        1. 'truck', 'car', 'construction'이 있으면 위험 경로.
        2. 'manhole' 등은 안전.
        3. 장애물이 적은 곳을 추천.
        
        반드시 아래 JSON 형식으로만 응답해:
        {{
            "recommended_idx": 0 또는 1, 
            "analysis": "분석 내용 한줄 요약",
            "reason": "추천 이유 한줄 요약"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # JSON 파싱 (마크다운 제거)
            if "```json" in text:
                text = text.replace("```json", "").replace("```", "")
            if "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                return json.loads(text[start:end])
            
            return json.loads(text)
            
        except Exception as e:
            print(f"❌ Gemini 분석 에러: {e}")
            # 에러 시 기본값 반환 (시스템 다운 방지)
            return {
                "recommended_idx": 0,
                "analysis": "AI 분석 지연 (기본 경로 유지)",
                "reason": "네트워크 상태가 불안정합니다."
            }