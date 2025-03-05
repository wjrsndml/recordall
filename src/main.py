import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from models import Database, ImageStore
from models.ocr_result import OCRStore
from services.ocr_service import OCRService
from views.main_window import MainWindow

async def main():
    # 初始化数据库和存储
    database = Database()
    image_store = ImageStore(database)
    ocr_store = OCRStore(database)
    ocr_service = OCRService(ocr_store)
    
    # 启动OCR服务
    asyncio.create_task(ocr_service.start_processing())
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow(image_store, ocr_service)
    window.show()
    
    # 运行事件循环
    try:
        await app.exec()
    finally:
        # 清理资源
        ocr_service.stop_processing()
        image_store.clear_cache()

if __name__ == '__main__':
    asyncio.run(main())