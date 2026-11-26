import threading
# from gliner2 import GLiNER2
from gliner2.inference.engine import GLiNER2

class GLiNER2Runtime:

    MODEL_NAME = "fastino/GLiNER2-Guardrails-PII-Multi"

    def __init__(self, device="cpu"):

        self.device = device
        self.model = None

        self._lock = threading.RLock()

    def load(self):

        with self._lock:

            if self.model is not None:
                return self.model

            print(
                f"[GLiNER2Runtime] loading {self.MODEL_NAME}"
            )

            model = GLiNER2.from_pretrained(
                self.MODEL_NAME
            )

            model.to(self.device)

            self.model = model

            print(
                f"[GLiNER2Runtime] Model loaded on {self.device}"
            )

            return self.model

    def extract_entities(
            self,
            text,
            labels,
            threshold=0.5
    ):
        with self._lock:

            model = self.load()

            return model.extract_entities(
                text,
                labels,
                threshold=threshold,
                include_confidence=True,
                include_spans=True
            )

    def classify(
            self,
            text,
            task,
            threshold=0.5
    ):

        with self._lock:

            model = self.load()

            return model.classify_text(
                text,
                task,
                threshold=threshold
            )

_gliner2_runtime = None
_runtime_lock = threading.Lock()

def get_gliner2_runtime(device="cpu"):

    global _gliner2_runtime

    with _runtime_lock:

        if _gliner2_runtime is None:

            _gliner2_runtime = GLiNER2Runtime(
                device=device
            )

        elif _gliner2_runtime.device != device:

            raise RuntimeError(
                "GLiNER2 runtime already initialized "
                f"with device={_gliner2_runtime.device}"
            )

        return _gliner2_runtime