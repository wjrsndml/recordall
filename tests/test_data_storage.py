import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.database import Database, Image, OCRText
from src.models.image_store import ImageStore
from src.models.ocr_result import OCRResult
from PIL import Image as PILImage
import io
from sqlalchemy.orm import Session

def test_database_storage():
    """测试数据库中的图片和OCR结果存储"""
    # 初始化数据库连接
    db = Database()
    
    with Session(db.engine) as session:
        try:
            # 使用ORM查询图片数据
            images = session.query(Image).all()
            print(f"找到 {len(images)} 张图片记录")

            for idx, img in enumerate(images):
                print(f"\n检查图片 #{idx + 1}:")
                print(f"时间戳: {img.timestamp}")
                
                # 验证图片数据
                if img.data:
                    try:
                        # 尝试从二进制数据加载图片
                        image = PILImage.open(io.BytesIO(img.data))
                        print(f"图片格式: {image.format}")
                        print(f"图片尺寸: {image.size}")
                    except Exception as e:
                        print(f"图片数据损坏: {e}")
                else:
                    print("警告: 图片数据为空")

                # 检查关联的OCR结果
                ocr_results = session.query(OCRText).filter(OCRText.image_id == img.id).all()
                print(f"OCR结果数量: {len(ocr_results)}")

                for ocr in ocr_results:
                    print(f"- 文本: {ocr.text}")
                    print(f"  位置: ({ocr.x}, {ocr.y}, {ocr.width}, {ocr.height})")
                    print(f"  置信度: {ocr.confidence}")

        except Exception as e:
            print(f"测试过程中出现错误: {e}")

if __name__ == '__main__':
    test_database_storage()