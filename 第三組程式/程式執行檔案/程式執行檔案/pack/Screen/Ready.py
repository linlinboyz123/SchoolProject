import sys
import os
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QStackedWidget, QSizePolicy
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, pyqtSignal, QTimer

class Ui_Ready(QWidget):
    video_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MainWidow")

        # 媒體播放器
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        self.video_widget.setMinimumSize(1920, 1080)   
        
        # 影片置中
        layout = QVBoxLayout(self)
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self.play_video) 
        
    def play_video(self):
        video_path = os.path.abspath('Screen/start.mp4') 
        if os.path.exists(video_path):
            url = QUrl.fromLocalFile(video_path)
            self.media_player.setMedia(QMediaContent(url))
            self.media_player.play()
        else:
            print(f"影片文件不存在: {video_path}")

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print("影片播放完成")
            self.release_resources()

    # 釋放資源並退出程式
    def release_resources(self):
        self.media_player.stop()
        self.media_player.deleteLater()
        self.video_widget.deleteLater()

    # 到這個頁面時，影片才會播放
    def showEvent(self, event):
        self.play_video()
        super().showEvent(event)

    # 當頁面隱藏時暫停影片播放及聲音
    def hideEvent(self, event):
        self.media_player.pause()  
        super().hideEvent(event)

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print("影片播放完成")
            self.release_resources()
            self.video_finished.emit()  

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MainWindow")
        
        self.stacked_widget = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.ui_ready = Ui_Ready()
        self.stacked_widget.addWidget(self.ui_ready)

        self.stacked_widget.setCurrentWidget(self.ui_ready)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
