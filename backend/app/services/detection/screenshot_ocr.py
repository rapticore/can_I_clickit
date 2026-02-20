import base64
import io
import re

import structlog

logger = structlog.get_logger()


class ScreenshotOCR:
    """Extract text and URLs from screenshots using OCR.

    Uses Tesseract for on-premise OCR. Can be swapped for
    AWS Textract in production for higher accuracy.
    """

    async def extract(self, image_base64: str) -> tuple[str, list[str]]:
        try:
            image_bytes = base64.b64decode(image_base64)
            text = await self._ocr(image_bytes)
            urls = self._extract_urls(text)
            return text, urls
        except Exception as exc:
            logger.error("ocr_extraction_failed", error=str(exc))
            return "", []

    async def _ocr(self, image_bytes: bytes) -> str:
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(image_bytes))

            if image.mode != "RGB":
                image = image.convert("RGB")

            text = pytesseract.image_to_string(image)
            return text.strip()
        except ImportError:
            logger.warning("tesseract_not_available", detail="Falling back to empty text")
            return ""
        except Exception as exc:
            logger.error("tesseract_ocr_failed", error=str(exc))
            return ""

    @staticmethod
    def _extract_urls(text: str) -> list[str]:
        url_pattern = re.compile(
            r'https?://[^\s<>"\')\]]+',
            re.IGNORECASE,
        )
        return url_pattern.findall(text)
