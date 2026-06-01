import os
import json
import networkx as nx
import osmnx as ox
from itertools import islice

# =========================================================
# [설정] 포터블(Portable) 경로 설정 (핵심 수정 사항)
# =========================================================
# 현재 이 파일(map_engine.py)이 있는 위치를 기준으로 경로를 잡습니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 캐시 파일명 (같은 폴더 내에 저장/로드)
CACHE_FILENAME = "routes_cache.json"
CACHE_FILE = os.path.join(BASE_DIR, CACHE_FILENAME)

# 기본 좌표 (건국대/서울 예시)
DEFAULT_START = (37.5447285, 126.9716774)
DEFAULT_END   = (37.5469626, 126.9756664)

def get_routes_from_osm(start, end):
    """
    OSMnx를 사용하여 도보 경로를 계산하거나 캐시된 경로를 반환합니다.
    """
    s_lat, s_lng = start if start else DEFAULT_START
    e_lat, e_lng = end if end else DEFAULT_END

    # 1. 캐시 확인 (상대 경로 사용)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
                print(f"📂 [System] 캐시 파일 로드 성공: {CACHE_FILENAME}")
                
                # 캐시 구조에 따른 반환 처리
                if isinstance(cached_data, list):
                    return cached_data
                elif isinstance(cached_data, dict):
                    return cached_data.get('routes', [])
        except Exception as e:
            print(f"⚠️ 캐시 읽기 실패 (새로 계산합니다): {e}")

    # 2. OSMnx로 경로 계산 (인터넷 연결 필요)
    print(f"📍 [OSM] 새 경로 계산 중... (Start -> End)")
    print(f"   ㄴ 위치: {CACHE_FILE} 에 저장됩니다.")
    
    try:
        # 두 지점의 중간을 중심으로 2km 반경 도로망 로드
        mid_lat, mid_lng = (s_lat + e_lat) / 2, (s_lng + e_lng) / 2
        
        # network_type='walk' : 휠체어/보행자용
        G = ox.graph_from_point((mid_lat, mid_lng), dist=2000, network_type='walk')
        
        # 가장 가까운 노드 찾기
        orig = ox.distance.nearest_nodes(G, s_lng, s_lat)
        dest = ox.distance.nearest_nodes(G, e_lng, e_lat)
        
        # 최단 경로 2개 탐색 (weight='length': 거리 우선)
        routes = list(islice(nx.shortest_simple_paths(G, orig, dest, weight='length'), 2))
        
        # UI 전송용 좌표 변환 (노드 ID -> 위도/경도)
        result_paths = [[{'lat': G.nodes[n]['y'], 'lng': G.nodes[n]['x']} for n in r] for r in routes]

        # 3. 캐시 저장 (다음 실행 시 인터넷 없이 되도록)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(result_paths, f, ensure_ascii=False, indent=4)
            
        print("✅ 경로 계산 및 캐싱 완료.")
        return result_paths
        
    except Exception as e:
        print(f"❌ OSM 경로 계산 실패 (인터넷 연결을 확인하세요): {e}")
        return []

# 테스트 실행용 (직접 실행 시 동작 확인)
if __name__ == "__main__":
    print(f"🔧 현재 실행 경로: {BASE_DIR}")
    print(f"📂 캐시 파일 경로: {CACHE_FILE}")
    # routes = get_routes_from_osm(None, None)
    # print(f"확인된 경로 수: {len(routes)}")