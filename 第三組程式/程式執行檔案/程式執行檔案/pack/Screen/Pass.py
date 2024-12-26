from PyQt5 import QtCore, QtGui, QtWidgets
import os
import pygame

# 跳過頁面
class Ui_Pass(QtWidgets.QWidget):
    def setupUi(self):
        self.setObjectName("PassWindow")

        # 設定視窗大小為螢幕大小
        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.resize(screen_geometry.width(), screen_geometry.height())

        # 使用 QVBoxLayout 將文字置中顯示
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # 設定背景圖片
        self.background_path = os.path.abspath('./Screen/img/pass.png')
        self.palette = QtGui.QPalette()

        # 設置音效檔案路徑
        self.sound_path = os.path.abspath('fail2.wav')

        # 初始化 pygame 音效模組
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

        QtCore.QMetaObject.connectSlotsByName(self)

    def play_sound(self):
        if os.path.exists(self.sound_path):
            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(loops=0, start=0.0)

    # 動態調整背景圖片大小
    def resizeEvent(self, event):
        pixmap = QtGui.QPixmap(self.background_path).scaled(
            self.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        super().resizeEvent(event)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    error_window = Ui_Pass()
    error_window.setupUi()
    error_window.show()
    sys.exit(app.exec_())
