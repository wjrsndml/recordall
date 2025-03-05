from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from models import ImageStore
from services.ocr_service import OCRService
from views.viewer_window import ViewerWindow

class MainWindow(QMainWindow):
    def __init__(self, image_store: ImageStore, ocr_service: OCRService):
        super().__init__()
        self.image_store = image_store
        self.ocr_service = ocr_service
        self.recording = False
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self._capture_screen)
        self.failed_count = 0
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('RecordAll 屏幕录制工具')
        self.setMinimumSize(300, 200)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 状态标签
        self.status_label = QLabel('就绪')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 控制按钮
        self.record_button = QPushButton('开始录制')
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)
        
        self.view_button = QPushButton('播放')
        self.view_button.clicked.connect(self.open_viewer)
        layout.addWidget(self.view_button)
        
        self.quit_button = QPushButton('退出')
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)
    
    def toggle_recording(self):
        """切换录制状态"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """开始录制"""
        self.recording = True
        self.failed_count = 0
        self.record_button.setText('暂停录制')
        self.status_label.setText('正在录制...')
        self.record_timer.start(2000)  # 每2秒截图一次
    
    def stop_recording(self):
        """停止录制"""
        self.recording = False
        self.record_button.setText('开始录制')
        self.status_label.setText('已暂停')
        self.record_timer.stop()
    
    async def _capture_screen(self):
        """捕获屏幕截图"""
        try:
            image = self.image_store.capture_screen()
            image_id = self.image_store.save_image(image)
            await self.ocr_service.add_image(image_id, image)
            self.failed_count = 0
        except Exception as e:
            print(f'截图失败: {e}')
            self.failed_count += 1
            if self.failed_count >= 10:
                self.stop_recording()
                self.status_label.setText('连续截图失败，已停止录制')
    
    def open_viewer(self):
        """打开图片浏览窗口"""
        viewer = ViewerWindow(self.image_store)
        viewer.show()