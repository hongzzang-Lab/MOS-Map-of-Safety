import math

class IDLockTracker:
    def __init__(self, distance_threshold=50, max_disappeared=5):
        """
        [Layer 1] 거리 기반 ID-Lock 추적 알고리즘
        """
        self.next_object_id = 0
        self.objects = {}  # ID: Centroid (cx, cy)
        self.disappeared = {} # ID: Disappeared Count
        self.distance_threshold = distance_threshold
        self.max_disappeared = max_disappeared

    def update(self, rects):
        # rects: [(x, y, w, h, class_id), ...]
        if len(rects) == 0:
            for oid in list(self.disappeared.keys()):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self.deregister(oid)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (x, y, w, h, _)) in enumerate(rects):
            cx = int(x + w / 2.0)
            cy = int(y + h) # 발바닥 기준
            input_centroids[i] = (cx, cy)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = [] 
            for sublist in object_centroids:
                row = []
                for (cx, cy) in input_centroids:
                    dist = math.hypot(sublist[0]-cx, sublist[1]-cy)
                    row.append(dist)
                D.append(row)
            
            pass 

        return self.objects

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
