from dataclasses import dataclass
from typing import List
from sqlalchemy.orm import Session
from .database import OCRText, Image, Database

@dataclass
class OCRResult:
    text: str
    confidence: int
    x: int
    y: int
    width: int
    height: int
    
    @classmethod
    def from_db(cls, ocr_text: OCRText):
        """从数据库记录创建OCR结果对象"""
        return cls(
            text=ocr_text.text,
            confidence=ocr_text.confidence,
            x=ocr_text.x,
            y=ocr_text.y,
            width=ocr_text.width,
            height=ocr_text.height
        )
    
    def to_db(self, image_id: int) -> OCRText:
        """转换为数据库记录对象"""
        return OCRText(
            image_id=image_id,
            text=self.text,
            confidence=self.confidence,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height
        )

class OCRStore:
    def __init__(self, database: Database):
        self.database = database
    
    def save_results(self, image_id: int, results: List[OCRResult]):
        """保存OCR识别结果到数据库"""
        with Session(self.database.engine) as session:
            for result in results:
                session.add(result.to_db(image_id))
            session.commit()
    
    def get_results(self, image_id: int) -> List[OCRResult]:
        """获取指定图片的OCR识别结果"""
        with Session(self.database.engine) as session:
            ocr_texts = session.query(OCRText).filter(OCRText.image_id == image_id).all()
            return [OCRResult.from_db(text) for text in ocr_texts]
    
    def search_text(self, keyword: str) -> List[int]:
        """搜索包含指定文本的图片ID列表"""
        with Session(self.database.engine) as session:
            results = session.query(Image.id).join(OCRText)\
                .filter(OCRText.text.contains(keyword))\
                .distinct().all()
            return [r[0] for r in results]