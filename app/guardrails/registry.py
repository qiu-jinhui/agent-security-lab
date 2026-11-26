from app.guardrails.detectors.base import BaseDetector

class DetectorRegistry:

    def __init__(self):
        self._detectors = {}
        self._modes = {}

    def register(
        self,
        detector: BaseDetector,
        mode: str = "blocking"
    ):

        if mode not in ("blocking", "audit"):
            raise ValueError(
                f"Unsupported detector mode: {mode}"
            )

        if detector.name in self._detectors:
            raise ValueError(
                f"Detector already registered: {detector.name}"
            )

        self._detectors[detector.name] = detector
        self._modes[detector.name] = mode

    def get(self, name):
        return self._detectors.get(name)

    def get_mode(self, name):
        return self._modes.get(name)

    def get_by_mode(self, mode):
        return [
            detector
            for name, detector in self._detectors.items()
            if self._modes[name] == mode
        ]

    def list_detectors(self):
        return [
            {
                "name": name,
                "mode": self._modes[name],
                "version": detector.version
            }
            for name, detector in self._detectors.items()
        ]