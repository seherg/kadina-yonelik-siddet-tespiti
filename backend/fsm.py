# backend/fsm.py

import time

class HelpSignalFSM:
    """
    El hareketlerini sıralı olarak takip eder:
    open_hand → thumb_in → closed_fingers
    Eğer bu sırayla yapılırsa True döner ve alarm tetiklenmelidir.
    """

    def __init__(self, max_interval=4.0, min_interval=0.3, tolerance=1):
        self.sequence = ['open_hand', 'thumb_in', 'closed_fingers']
        self.class_mapping = {
            'open_hand': ['open_hand', 'open', 'hand', 'palm', 'five'],
            'thumb_in': ['thumb_in', 'thumb', 'four', 'four_fingers'],
            'closed_fingers': ['closed_fingers', 'closed', 'fist', 'zero', 'none']
        }
        self.state_index = 0
        self.last_timestamp = None
        self.max_interval = max_interval
        self.min_interval = min_interval
        self.tolerance = tolerance
        self.tolerance_used = 0

    @property
    def current_step(self):
        return self.state_index

    @property
    def is_complete(self):
        return self.state_index >= len(self.sequence)

    def reset(self):
        print("🔁 FSM sıfırlandı")
        self.state_index = 0
        self.last_timestamp = None
        self.tolerance_used = 0

    def _matches_class(self, detected_class: str, expected_class: str) -> bool:
        if detected_class == expected_class:
            return True
        if expected_class in self.class_mapping:
            for alt in self.class_mapping[expected_class]:
                if alt.lower() in detected_class.lower() or detected_class.lower() in alt.lower():
                    return True
        return False

    def update(self, detected_class: str) -> bool:
        now = time.time()

        if self.state_index == 0:
            if self._matches_class(detected_class, self.sequence[0]):
                self.state_index = 1
                self.last_timestamp = now
                print(f"🟢 İlk adım tamamlandı: {detected_class}")
            else:
                print(f"⚪ İlk adım bekleniyor: {self.sequence[0]}, algılanan: {detected_class}")
            return False

        if self.last_timestamp is not None:
            delta = now - self.last_timestamp
            if delta > self.max_interval:
                print(f"⏰ Zaman aşımı ({delta:.2f}s > {self.max_interval}s)")
                self.reset()
                return False
            elif delta < self.min_interval:
                print(f"⏰ Çok hızlı geçiş ({delta:.2f}s < {self.min_interval}s)")
                return False

        if self.state_index < len(self.sequence):
            expected_class = self.sequence[self.state_index]
            if self._matches_class(detected_class, expected_class):
                self.state_index += 1
                self.last_timestamp = now
                self.tolerance_used = 0
                print(f"🟢 Adım {self.state_index} tamamlandı: {detected_class}")
                if self.state_index == len(self.sequence):
                    print("🚨 TÜM ADIMLAR TAMAMLANDI - ALARM!")
                    self.reset()
                    return True
            else:
                self.tolerance_used += 1
                print(f"❌ Beklenen: {expected_class}, ama algılanan: {detected_class} (tolerans: {self.tolerance_used}/{self.tolerance})")

                if self._matches_class(detected_class, self.sequence[0]):
                    print(f"🔄 Yeniden başlatıldı: {detected_class}")
                    self.state_index = 1
                    self.last_timestamp = now
                    self.tolerance_used = 0
                elif self.tolerance_used > self.tolerance:
                    self.reset()

        return False
