import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

class CamWindow(QWidget):
    def __init__(self, camera):
        super().__init__()
        self.setWindowTitle("Camera Display")
        self.camera = camera

        # 設置界面
        self.layout = QVBoxLayout(self)
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # 設定定時器，抓取攝影機畫面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 每30毫秒更新一幀

    def update_frame(self):
        """
        從攝影機中抓取一幀畫面，並顯示到介面。
        """
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 轉換為RGB格式
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)
        else:
            print("無法從攝影機讀取畫面")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    camera_window = CamWindow()
    camera_window.show()
    sys.exit(app.exec_())
