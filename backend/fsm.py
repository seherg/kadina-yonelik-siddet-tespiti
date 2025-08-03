# backend/fsm.py
import time

class HelpSignalFSM:
    """
    El hareketlerini sıralı olarak takip eder:
    open_hand → thumb_in → closed_fingers
    Doğru sırayla yapılırsa True döner ve alarm tetiklenir.
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
        """FSM'i başlangıç durumuna sıfırla"""
        print("🔁 FSM sıfırlandı")
        self.state_index = 0
        self.last_timestamp = None
        self.tolerance_used = 0

    def _matches_class(self, detected_class: str, expected_class: str) -> bool:
        """Algılanan sınıfın beklenen sınıfla eşleşip eşleşmediğini kontrol et"""
        if not detected_class or not expected_class:
            return False

        detected_class = detected_class.lower()

        # Tam eşleşme
        if detected_class == expected_class.lower():
            return True

        # Alternatif isimlerle tam eşleşme
        if expected_class in self.class_mapping:
            for alt in self.class_mapping[expected_class]:
                if detected_class == alt.lower():
                    return True

        return False

    def _check_timing(self, current_time: float) -> bool:
        """Zamanlama kontrolü yap"""
        if self.last_timestamp is None:
            return True

        delta = current_time - self.last_timestamp

        if delta > self.max_interval:
            print(f"⏰ Zaman aşımı ({delta:.2f}s > {self.max_interval}s)")
            self.reset()
            return False

        if delta < self.min_interval:
            print(f"⏰ Çok hızlı geçiş ({delta:.2f}s < {self.min_interval}s)")
            return False

        return True

    def _handle_wrong_input(self, detected_class: str):
        """Yanlış input geldiğinde tolerans kontrolü"""
        expected_class = self.sequence[self.state_index] if self.state_index < len(self.sequence) else None
        print(f"❌ Beklenen: {expected_class}, algılanan: {detected_class} "
              f"(tolerans: {self.tolerance_used}/{self.tolerance})")

        self.tolerance_used += 1

        # Tolerans hakkı bitince sıfırla
        if self.tolerance_used > self.tolerance:
            print("🔄 Tolerans aşıldı, FSM sıfırlanıyor")
            self.reset()

    def update(self, detected_class: str) -> bool:
        """
        FSM güncelleme fonksiyonu
        Returns True: Sekans tamamlandı (alarm tetiklenmeli)
        """
        if not detected_class:
            return False

        current_time = time.time()

        # İlk adım
        if self.state_index == 0:
            if self._matches_class(detected_class, self.sequence[0]):
                self.state_index = 1
                self.last_timestamp = current_time
                self.tolerance_used = 0
                print(f"🟢 İlk adım tamamlandı: {detected_class}")
            else:
                self._handle_wrong_input(detected_class)
            return False

        # Zaman kontrolü
        if not self._check_timing(current_time):
            return False

        # Mevcut adım kontrolü
        expected_class = self.sequence[self.state_index]
        if self._matches_class(detected_class, expected_class):
            self.state_index += 1
            self.last_timestamp = current_time
            self.tolerance_used = 0
            print(f"🟢 Adım {self.state_index} tamamlandı: {detected_class}")

            if self.state_index >= len(self.sequence):
                print("🚨 TÜM ADIMLAR TAMAMLANDI - ALARM TETIKLENDI!")
                self.reset()
                return True
        else:
            # Yanlış hareket → asla adım atlamaz, sadece tolerans sayar
            self._handle_wrong_input(detected_class)

        return False

    def get_status(self) -> dict:
        """FSM mevcut durum bilgisi"""
        expected_next = None
        if self.state_index < len(self.sequence):
            expected_next = self.sequence[self.state_index]

        return {
            'current_step': self.state_index,
            'total_steps': len(self.sequence),
            'expected_next': expected_next,
            'tolerance_used': self.tolerance_used,
            'tolerance_max': self.tolerance,
            'last_timestamp': self.last_timestamp,
            'is_complete': self.is_complete
        }
