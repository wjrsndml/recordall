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
        print('OCR服务启动，等待处理图片...')
        while self._processing:
            try:
                image_id, image = await self._queue.get()
                print(f'开始处理图片 ID: {image_id}, 图片尺寸: {image.size}')
                results = await self._process_image(image)
                print(f'OCR识别完成，找到 {len(results)} 个文本区域')
                self.ocr_store.save_results(image_id, results)
                print(f'OCR结果已保存到数据库')
            except Exception as e:
                print(f'OCR处理错误: {e}')
            finally:
                self._queue.task_done()
    
    def stop_processing(self):
        """停止OCR处理循环"""
        print('正在停止OCR服务...')
        self._processing = False
    
    async def add_image(self, image_id: int, image: PILImage):
        """添加图片到OCR处理队列"""
        print(f'添加图片到OCR队列: ID {image_id}')
        await self._queue.put((image_id, image))
    
    async def _process_image(self, image: PILImage) -> List[OCRResult]:
        """处理单张图片的OCR识别"""
        print('转换图片格式为RGB...')
        try:
            # 转换为RGB格式并获取numpy数组
            image_array = image.convert('RGB')
            print(f'图片转换完成，当前格式: {image_array.mode}, 尺寸: {image_array.size}')
            
            print('开始OCR识别...')
            # 执行OCR识别
            results = self.reader.readtext(image_array)
            print(f'OCR识别完成，原始结果数量: {len(results)}')
            
            if not results:
                print('警告: OCR未识别到任何文本')
                return []
            
            # 转换为OCRResult对象
            ocr_results = [
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
            
            print('OCR结果转换完成，详细信息：')
            for result in ocr_results:
                print(f'- 文本: {result.text}')
                print(f'  位置: ({result.x}, {result.y}, {result.width}, {result.height})')
                print(f'  置信度: {result.confidence}%')
            
            return ocr_results
        except Exception as e:
            print(f'OCR处理过程中出现错误: {e}')
            raise