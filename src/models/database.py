from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    data = Column(LargeBinary, nullable=False)  # WebP格式的图片数据
    ocr_results = relationship('OCRText', back_populates='image', cascade='all, delete-orphan')

class OCRText(Base):
    __tablename__ = 'ocr_texts'
    
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    text = Column(String, nullable=False)
    confidence = Column(Integer)  # OCR识别置信度
    x = Column(Integer)  # 文本框左上角x坐标
    y = Column(Integer)  # 文本框左上角y坐标
    width = Column(Integer)  # 文本框宽度
    height = Column(Integer)  # 文本框高度
    image = relationship('Image', back_populates='ocr_results')

class Database:
    def __init__(self, db_path='data/recordall.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)