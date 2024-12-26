from PyQt5 import QtCore, QtGui, QtWidgets
import os
import pygame 

# 回答正確頁面
class Ui_Correct(QtWidgets.QWidget):
    def setupUi(self):
        self.setObjectName("CorrectWindow")

        # 設定視窗大小為螢幕大小
        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.resize(screen_geometry.width(), screen_geometry.height())

        # 使用 QVBoxLayout 將文字置中顯示
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # 設定背景圖片
        self.background_path = os.path.abspath('./Screen/img/win.png')
        self.palette = QtGui.QPalette()

        # 加載自定義字體
        font_path = os.path.join(os.path.dirname(__file__), "../Font/NaikaiFont-Bold.ttf")
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Sans Serif"

        # 設置文字 Label 3
        self.label_3 = QtWidgets.QLabel(self)
        font = QtGui.QFont(font_family, 36)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        # 設置文字 Label 4
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        # 將文字 Label 添加到主佈局
        layout.addWidget(self.label_3)
        layout.addWidget(self.label_4)

        # 設置音效檔案路徑
        self.sound_path = os.path.abspath('win2.wav')

        # 初始化 pygame 音效模組
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CorrectWindow", "Correct"))
        self.label_3.setText(_translate("CorrectWindow", "答對了！"))
        self.label_4.setText(_translate("CorrectWindow", "請繼續下一題！"))

    def play_sound(self):
        if os.path.exists(self.sound_path):
            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(loops=0, start=0.0)

    def resizeEvent(self, event):
        # 動態調整背景圖片大小
        pixmap = QtGui.QPixmap(self.background_path).scaled(
            self.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        # 根據視窗寬度動態調整字體大小
        font_size = self.width() // 50  # 根據寬度調整字體大小
        self.label_3.setFont(QtGui.QFont(self.label_3.font().family(), font_size))
        self.label_4.setFont(QtGui.QFont(self.label_4.font().family(), font_size))

        super().resizeEvent(event)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    correct_window = Ui_Correct()
    correct_window.setupUi()
    correct_window.show()
    sys.exit(app.exec_())