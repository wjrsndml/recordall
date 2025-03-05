import easyocr
import asyncio
from typing import List
from PIL import Image as PILImage
from models.ocr_result import OCRResult, OCRStore

class OCRService:
    def __init__(self, ocr_store: OCRStore):
        self.reader = easyocr.Reader(['ch_sim', 'en'])
        self.ocr_store = ocr_store
        self._processing = False
        self._queue = asyncio.Queue()
    
    async def start_processing(self):
        """启动OCR处理循环"""
        self._processing = True
        while self._processing:
            try:
                image_id, image = await self._queue.get()
                results = await self._process_image(image)
                self.ocr_store.save_results(image_id, results)
            except Exception as e:
                print(f'OCR处理错误: {e}')
            finally:
                self._queue.task_done()
    
    def stop_processing(self):
        """停止OCR处理循环"""
        self._processing = False
    
    async def add_image(self, image_id: int, image: PILImage):
        """添加图片到OCR处理队列"""
        await self._queue.put((image_id, image))
    
    async def _process_image(self, image: PILImage) -> List[OCRResult]:
        """处理单张图片的OCR识别"""
        # 转换为OpenCV格式
        image_array = image.convert('RGB')
        # 执行OCR识别
        results = self.reader.readtext(image_array)
        # 转换为OCRResult对象
        return [
            OCRResult(
                text=text,
                confidence=int(confidence * 100),
                x=int(box[0][0]),
                y=int(box[0][1]),
                width=int(box[2][0] - box[0][0]),
                height=int(box[2][1] - box[0][1])
            )
            for box, text, confidence in results
        ]