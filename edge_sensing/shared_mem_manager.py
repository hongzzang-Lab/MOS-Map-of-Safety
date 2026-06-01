from multiprocessing import shared_memory
import json
import struct
import time

# 공유 메모리 설정 
SHM_NAME = "mos_shared_memory"
SHM_SIZE = 4096  # 4KB

class SharedMemoryWriter:
    def __init__(self):
        try:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)
            print(f"✅ 공유 메모리 생성 완료: {SHM_NAME}")
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME)
            print(f"✅ 공유 메모리 연결 완료: {SHM_NAME}")
        except Exception as e:
            print(f"❌ 공유 메모리 오류: {e}")
            self.shm = None

    def write(self, data):
        if self.shm is None: return

        try:
            json_str = json.dumps(data)
            encoded_data = json_str.encode('utf-8')
            
            if len(encoded_data) > SHM_SIZE - 4:
                print("⚠️ 데이터가 너무 커서 공유 메모리에 쓸 수 없습니다.")
                return

            self.shm.buf[:4] = struct.pack('I', len(encoded_data))
            self.shm.buf[4:4+len(encoded_data)] = encoded_data
            
        except Exception as e:
            print(f"⚠️ 데이터 쓰기 실패: {e}")

    def close(self):
        if self.shm:
            self.shm.close()
            # unlink는 보통 서버 쪽이나 종료 시 한 번만 호출
