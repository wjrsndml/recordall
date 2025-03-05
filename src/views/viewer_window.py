from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from datetime import datetime, timedelta
from models import ImageStore
import io

class ViewerWindow(QMainWindow):
    def __init__(self, image_store: ImageStore):
        super().__init__()
        self.image_store = image_store
        self.current_date = datetime.now().date()
        self.current_images = []
        self.current_index = 0
        
        self._init_ui()
        self._load_images()
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('RecordAll 图片浏览')
        self.setMinimumSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 图片显示标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)
        
        # 日期标签
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.date_label)
        
        # 滑块控制
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.valueChanged.connect(self._on_slider_change)
        layout.addWidget(self.slider)
    
    def _load_images(self):
        """加载指定日期的图片"""
        print(f'开始加载{self.current_date}的图片...')
        self.current_images = self.image_store.get_images_by_date(self.current_date)
        print(f'找到{len(self.current_images)}张图片')
        if self.current_images:
            print('设置滑块最大值并更新显示...')
            self.slider.setMaximum(len(self.current_images) - 1)
            self.current_index = 0
            self._update_display()
        else:
            print('没有找到图片，清除显示...')
            self.image_label.clear()
            self.date_label.setText('没有图片')
    
    def _update_display(self):
        """更新显示的图片和日期信息"""
        if not self.current_images:
            print('没有图片可显示')
            return
        
        try:
            # 获取当前图片
            print(f'正在获取图片ID {self.current_images[self.current_index]}...')
            image = self.image_store.get_image(self.current_images[self.current_index])
            if image:
                print('成功获取图片，开始转换格式...')
                # 将PIL Image转换为字节流
                buffer = io.BytesIO()
                image.save(buffer, format='WebP')
                image_data = buffer.getvalue()
                print('图片转换完成，创建QImage...')
                
                # 转换为QPixmap并适应窗口大小
                qimage = QImage.fromData(image_data)
                if qimage.isNull():
                    print('错误：QImage创建失败')
                    return
                
                print('创建QPixmap...')
                pixmap = QPixmap.fromImage(qimage)
                if pixmap.isNull():
                    print('错误：QPixmap创建失败')
                    return
                
                print('缩放图片以适应窗口大小...')
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                print('设置图片到标签...')
                self.image_label.setPixmap(scaled_pixmap)
                
                # 更新日期显示
                self.date_label.setText(self.current_date.strftime('%Y-%m-%d'))
                print('显示更新完成')
                
                # 预加载周边图片
                self._preload_images()
            else:
                print(f'错误：无法获取图片ID {self.current_images[self.current_index]}')
        except Exception as e:
            print(f'更新显示时发生错误: {e}')
            import traceback
            print(traceback.format_exc())
    
    def _preload_images(self):
        """预加载当前图片周边的图片"""
        preload_range = 5  # 前后各预加载5张
        start_idx = max(0, self.current_index - preload_range)
        end_idx = min(len(self.current_images), self.current_index + preload_range + 1)
        
        for idx in range(start_idx, end_idx):
            if idx != self.current_index:
                self.image_store.get_image(self.current_images[idx])
    
    def _on_slider_change(self, value):
        """处理滑块值变化"""
        if value == self.slider.minimum() and self.current_index == 0:
            # 切换到前一天
            self.current_date -= timedelta(days=1)
            self._load_images()
            if self.current_images:
                self.current_index = len(self.current_images) - 1
                self.slider.setValue(self.current_index)
        elif value == self.slider.maximum() and self.current_index == len(self.current_images) - 1:
            # 切换到后一天
            self.current_date += timedelta(days=1)
            self._load_images()
        else:
            self.current_index = value
            self._update_display()
    
    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        self._update_display()