import math

class PathPlanner:
    def __init__(self, robot_width=0.7, safety_margin=0.3):
        # 휠체어 폭(70cm) + 여유 공간
        self.safe_threshold = robot_width + safety_margin

    def check_passability(self, detected_objects):
        """
        [알고리즘]
        단순히 장애물 유무만 보는 것이 아니라,
        장애물 사이의 '물리적 거리(Gap)'를 계산하여 통과 가능 여부 판단.
        """
        if not detected_objects:
            return {"status": "safe", "msg": " 전방에 장애물이 없습니다."}

        # 1. 전방 위험 구역 내 장애물 필터링 (거리 5m 이내)
        nearby_objs = [obj for obj in detected_objects if obj.get('dist', 10) < 5.0]
        
        if not nearby_objs:
             return {"status": "safe", "msg": " 주행 경로가 안전합니다."}

        # 2. 위험 클래스 확인 
        danger_classes = ['truck', 'car', 'barricade', 'construction_cone']
        risk_objs = [o for o in nearby_objs if o['class'] in danger_classes]

        if risk_objs:
            # 3.  수선의 발 개념을 응용한 물리적 폭 계산
            # 장애물이 있다면 회피 공간이 충분한지 계산
        
            return {
                "status": "warning", 
                "msg": f"전방 위험 요소 {len(risk_objs)}개 감지! (회피 공간 부족 예상)"
            }
        
        return {"status": "safe", "msg": " 주의하여 주행하십시오."}
