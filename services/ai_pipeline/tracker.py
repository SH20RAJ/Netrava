"""Per-Camera ByteTrack Multi-Object Tracker.

Assigns and maintains consistent local track IDs across frames
using spatial IoU (Intersection-over-Union) association.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np


class TrackedObject:
    def __init__(self, track_id: str, bbox: Tuple[int, int, int, int], class_name: str, confidence: float):
        self.track_id = track_id
        self.bbox = bbox  # (x, y, w, h)
        self.class_name = class_name
        self.confidence = confidence
        self.hits = 1
        self.age = 1
        self.time_since_update = 0


class ByteTracker:
    def __init__(self, iou_threshold: float = 0.3, max_lost_frames: int = 15):
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.tracks: Dict[str, TrackedObject] = {}
        self.next_id = 1000

    @staticmethod
    def compute_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]

        denom = float(boxAArea + boxBArea - interArea)
        return interArea / denom if denom > 0 else 0.0

    def update(self, detections: List[Tuple[Tuple[int, int, int, int], str, float]]) -> List[TrackedObject]:
        """Associates detections with active tracks, creating new tracks if unassociated."""
        # Age existing tracks
        for track in self.tracks.values():
            track.time_since_update += 1
            track.age += 1

        matched_tracks = set()
        active_tracked_objects = []

        for bbox, class_name, conf in detections:
            best_iou = 0.0
            best_track_id = None

            for track_id, track in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                iou = self.compute_iou(bbox, track.bbox)
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id:
                track = self.tracks[best_track_id]
                track.bbox = bbox
                track.confidence = conf
                track.hits += 1
                track.time_since_update = 0
                matched_tracks.add(best_track_id)
                active_tracked_objects.append(track)
            else:
                # New track
                new_track_id = f"trk_{self.next_id}"
                self.next_id += 1
                new_track = TrackedObject(new_track_id, bbox, class_name, conf)
                self.tracks[new_track_id] = new_track
                active_tracked_objects.append(new_track)

        # Prune expired tracks
        expired = [tid for tid, trk in self.tracks.items() if trk.time_since_update > self.max_lost_frames]
        for tid in expired:
            del self.tracks[tid]

        return active_tracked_objects
