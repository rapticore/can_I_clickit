import base64
import io

import structlog

logger = structlog.get_logger()


class QRScanner:
    """Decode QR codes and extract URLs for analysis."""

    async def decode(self, image_base64: str) -> str:
        try:
            image_bytes = base64.b64decode(image_base64)
            return await self._decode_qr(image_bytes)
        except Exception as exc:
            logger.error("qr_decode_failed", error=str(exc))
            return ""

    async def _decode_qr(self, image_bytes: bytes) -> str:
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes))
            decoded = pyzbar_decode(image)

            if decoded:
                return decoded[0].data.decode("utf-8")
            return ""
        except ImportError:
            logger.warning("pyzbar_not_available")
            return self._fallback_decode(image_bytes)
        except Exception as exc:
            logger.error("pyzbar_decode_failed", error=str(exc))
            return ""

    @staticmethod
    def _fallback_decode(image_bytes: bytes) -> str:
        """Fallback using OpenCV if pyzbar is unavailable."""
        try:
            import cv2
            import numpy as np

            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(img)
            return data or ""
        except Exception:
            return ""
