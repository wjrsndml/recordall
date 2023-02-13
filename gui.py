import sys
import time
import os
import threading
#from multiprocessing import Process, Value, Array
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QDesktopWidget,QLabel, QLineEdit,  QVBoxLayout, QHBoxLayout, QWidget, QProgressBar,QSlider
from PyQt5.QtGui import QScreen,QPixmap,QImage
import sys
from PIL import Image
from PyQt5.QtCore import Qt
import recordutils
import numpy as np
#主窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.resize(500,500)

    def initUI(self):
        self.start_btn = QPushButton("开始录制", self)
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.resize(self.start_btn.sizeHint())
        self.start_btn.move(50, 50)

        self.pause_btn = QPushButton("暂停录制", self)
        self.pause_btn.clicked.connect(self.pause_recording)
        self.pause_btn.resize(self.pause_btn.sizeHint())
        self.pause_btn.move(150, 50)

        self.play_btn = QPushButton("播放", self)
        self.play_btn.clicked.connect(self.play)
        self.play_btn.resize(self.play_btn.sizeHint())
        self.play_btn.move(250, 50)

        self.exit_btn = QPushButton("退出", self)
        self.exit_btn.clicked.connect(self.exit)
        self.exit_btn.resize(self.exit_btn.sizeHint())
        self.exit_btn.move(350, 50)

        self.recording = False
        self.show()

    def start_recording(self):
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def pause_recording(self):
        self.recording = False

    def play(self):
        self.p = Playmain()
        self.p.show()
    
    def exit(self):
        sys.exit()

    def record(self):
        piclost=0
        while self.recording:    
            starttime=time.time()
            if recordutils.pic_capture() == False:
                piclost=piclost+1
                print("记录失败！")
            if piclost>=10:
                self.recording=False
            if self.recording == False:
                print('录制停止！')
                break
            timesleep=2+starttime-time.time()
            if timesleep>0:
                time.sleep(timesleep)
#记录浏览窗口
class Playmain(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle('图片浏览')

        # 设置主窗口布局
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # 创建文字输入框
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText('请输入文字')

        # 创建搜索按钮
        self.search_button = QPushButton('搜索')

        # 创建水平布局，将文字输入框和搜索按钮添加进去
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.input_text)
        self.input_layout.addWidget(self.search_button)

        # 创建图片显示框
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # 创建进度条
        self.slider = QSlider(Qt.Horizontal)


        # 将文字输入框、图片显示框和进度条添加到主窗口布局中
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.slider)
        self.search_button.clicked.connect(self.search_handler)
        self.slider.valueChanged.connect(self.progress_handler)
        self.filenames=recordutils.get_all_filenames()
        if len(self.filenames)==0:
            self.close()
        for i in reversed(self.filenames):
            self.nowdataread=i
            self.datanames=recordutils.get_datanames(self.nowdataread)
            if len(self.datanames)>0:
                break
        self.slider.setRange(-1,len(self.datanames))
        self.slider.setValue(len(self.datanames)-1)
        self.nowpicname=self.datanames[-1]
        self.nowpic=recordutils.get_pic(self.nowdataread,self.nowpicname)
        self.set_image(self.nowpic)
        
    def progress_handler(self):
    # 在这里处理进度条的值改变事件
        slivalue=self.slider.value()
        #print(len(self.datanames))
        if (slivalue>=0)and(slivalue<len(self.datanames)):
            self.nowpicname=self.datanames[slivalue]
            self.nowpic=recordutils.get_pic(self.nowdataread,self.nowpicname)
            self.set_image(self.nowpic)
        elif slivalue==-1:
            if(self.filenames.index(self.nowdataread)>0):
                self.nowdataread=self.filenames[self.filenames.index(self.nowdataread)-1]
                self.datanames=recordutils.get_datanames(self.nowdataread)
                self.slider.setRange(-1,len(self.datanames))
                self.slider.setValue(len(self.datanames)-1)
                self.nowpicname=self.datanames[len(self.datanames)-1]
                self.nowpic=recordutils.get_pic(self.nowdataread,self.nowpicname)
                self.set_image(self.nowpic)
        elif slivalue==len(self.datanames):
            if(self.filenames.index(self.nowdataread)+1<len(self.filenames)):
                self.nowdataread=self.filenames[self.filenames.index(self.nowdataread)+1]
                self.datanames=recordutils.get_datanames(self.nowdataread)
                self.slider.setRange(-1,len(self.datanames))
                self.slider.setValue(0)
                self.nowpicname=self.datanames[0]
                self.nowpic=recordutils.get_pic(self.nowdataread,self.nowpicname)
                self.set_image(self.nowpic)
        recordutils.refresh_cache(self.nowdataread,self.nowpicname,self.datanames)
#鼠标滚轮事件
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.slider.setValue(self.slider.value()+1)
        else:
            self.slider.setValue(self.slider.value()-1)
        
    def search_handler():
    # 在这里处理搜索事件
        pass
    
    def set_image(self, image):
        # 加载图片
        x,y=image.size
        x1=y1=self.image_label.size().width()
        y1=self.image_label.size().height()
        scale=min(x1/x,y1/y)
        image=image.resize((int(scale*x),int(scale*y)),Image.ANTIALIAS)
        image_np = np.array(image)
        h, w, c = image_np.shape
        q_img = QImage(image_np, w, h, c * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        # 设置图片大小与窗口大小一致
        #print(self.image_label.size())
        #self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
        self.image_label.setPixmap(pixmap)
    def resizeEvent(self, event):
        # 在窗口大小改变时，更新图片大小
        if self.image_label.pixmap():
            self.set_image(self.nowpic)

#按照文件名进行排序的函数
def sort_files_by_date(folder_path):
    file_list = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_list.append((filename, os.path.getmtime(file_path)))

    file_list.sort(key=lambda x: x[1])
    return [f[0] for f in file_list]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())



