from PIL import Image as PILImage
from io import BytesIO
import cv2
import numpy as np
from collections import OrderedDict
from datetime import datetime
from sqlalchemy.orm import Session
from .database import Image, Database

class ImageStore:
    def __init__(self, database: Database, cache_size=100):
        self.database = database
        self.cache_size = cache_size
        self.cache = OrderedDict()
    
    def capture_screen(self):
        """捕获屏幕截图并返回PIL Image对象"""
        # 使用OpenCV捕获屏幕
        screen = cv2.cvtColor(np.array(cv2.getWindowCapture(0)), cv2.COLOR_BGR2RGB)
        return PILImage.fromarray(screen)
    
    def save_image(self, pil_image: PILImage) -> int:
        """将PIL Image保存为WebP格式并存入数据库"""
        # 转换为WebP格式
        buffer = BytesIO()
        pil_image.save(buffer, format='WebP', quality=80, optimize=True)
        image_data = buffer.getvalue()
        
        # 保存到数据库
        with Session(self.database.engine) as session:
            image = Image(timestamp=datetime.now(), data=image_data)
            session.add(image)
            session.commit()
            return image.id
    
    def get_image(self, image_id: int) -> PILImage:
        """从缓存或数据库获取图片"""
        # 检查缓存
        if image_id in self.cache:
            self.cache.move_to_end(image_id)
            return self.cache[image_id]
        
        # 从数据库加载
        with Session(self.database.engine) as session:
            image = session.query(Image).filter(Image.id == image_id).first()
            if image:
                pil_image = PILImage.open(BytesIO(image.data))
                # 更新缓存
                self.cache[image_id] = pil_image
                if len(self.cache) > self.cache_size:
                    self.cache.popitem(last=False)
                return pil_image
            return None
    
    def get_images_by_date(self, date):
        """获取指定日期的所有图片ID"""
        with Session(self.database.engine) as session:
            from sqlalchemy import func
            return [img.id for img in session.query(Image)
                    .filter(func.date(Image.timestamp) == date)
                    .order_by(Image.timestamp).all()]
    
    def clear_cache(self):
        """清空图片缓存"""
        self.cache.clear()