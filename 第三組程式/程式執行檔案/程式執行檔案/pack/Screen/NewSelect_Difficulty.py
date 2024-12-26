import os
import threading
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl, QTimer
from KL_MP_Mix import detect_hand_gestures

class Ui_NewSelectDifficulty(QtWidgets.QWidget):
    difficulty_selected = QtCore.pyqtSignal(str)
    prevButton_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.custom_font = self.load_custom_font('Font\\NaikaiFont-Bold.ttf')  
        self.setupUi()
        self.hand_gestures_thread = None
        self.stop_signal = threading.Event()  
        self.timer = None  
        self.audio_player = QtMultimedia.QMediaPlayer(self)  

    def setupUi(self):
        self.setObjectName("MainWindow")
        screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
        self.setGeometry(screen_geometry)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)

        # 標題
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont(self.custom_font, 48)  
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.label)

        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)

        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setStyleSheet("QGroupBox { border: none; }")
        self.groupBox.setTitle("")

        self.verticalLayoutGroupBox = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayoutGroupBox.setObjectName("verticalLayoutGroupBox")

        # 難易度按鈕
        self.button1 = self.add_button_with_icon("簡單", "icon1.png")
        self.button2 = self.add_button_with_icon("普通", "icon2.png")
        self.button3 = self.add_button_with_icon("困難", "icon3.png")
        self.button4 = self.add_button_with_icon("隨機挑戰", "icon4.png")

        self.verticalLayout.addWidget(self.groupBox)

        # 建立一個水平佈局
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 上一步 按鈕
        self.prevButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont(self.custom_font, 18)  
        self.prevButton.setFont(font)
        self.prevButton.setMinimumHeight(100)
        self.prevButton.setFixedWidth(400)
        self.prevButton.setText("上一步")
        self.prevButton.clicked.connect(self.on_prev_clicked)

        # 上一步的圖片
        self.prev_img_label = QtWidgets.QLabel(self.centralwidget)
        img_path_prev = os.path.join(os.path.dirname(__file__), 'img', 'icon5.png')  
        self.prev_img_pixmap = QtGui.QPixmap(img_path_prev)
        self.prev_img_label.setPixmap(self.prev_img_pixmap)
        self.prev_img_label.setFixedSize(300, 300)  
        self.prev_img_label.setScaledContents(True) 

        # 將按鈕和圖片添加到水平佈局
        self.horizontalLayout.addWidget(self.prevButton)
        self.horizontalLayout.addWidget(self.prev_img_label)

        # 將水平佈局添加到主佈局
        self.verticalLayout.addLayout(self.horizontalLayout)

        # 調整水平佈局的對齊方式，放在左下角
        self.horizontalLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.setLayout(self.verticalLayout)
        self.retranslateUi()

    # 設定聲音播放計畫
    def schedule_sound_playback(self):
        QTimer.singleShot(2000, self.play_sound)  # 2秒後執行 play_sound

    # 播放聲音的方法
    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(__file__), 'sound', 'Select_Difficulty_sound.mp3')  
        if not os.path.exists(mp3_path):
            print(f"MP3 檔案不存在: {mp3_path}")
            return
        
        url = QUrl.fromLocalFile(mp3_path)
        content = QMediaContent(url)
        self.audio_player.setMedia(content)
        self.audio_player.setVolume(80)
        self.audio_player.play()

    # 到這個頁面才會撥放影片
    def showEvent(self, event):
        super().showEvent(event)
        self.play_sound()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.audio_player.stop()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "難易度選擇"))
        self.prevButton.setText(_translate("MainWindow", "上一步"))

    # 按鈕+圖片
    def add_button_with_icon(self, text, icon_filename):
        button = QtWidgets.QPushButton(self.groupBox)
        button.setFont(QtGui.QFont(self.custom_font, 30))  
        button.setMinimumHeight(200)
        button.setFixedWidth(600)
        button.setText(text)

        img_path = os.path.join(os.path.dirname(__file__), 'img', icon_filename)
        pixmap = QtGui.QPixmap(img_path)
        icon_label = QtWidgets.QLabel(self.groupBox)
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(200, 200)
        icon_label.setScaledContents(True)

        button.clicked.connect(lambda: self.on_difficulty_selected(text))

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(button, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(icon_label, alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)
        self.verticalLayoutGroupBox.addLayout(layout)
        button.clicked.connect(lambda: self.difficulty_selected.emit(text))  
        return button

    # 上一步
    def on_prev_clicked(self):
        self.prevButton_clicked.emit()

    # 字體
    def load_custom_font(self, font_path):
        if not os.path.exists(font_path):
            print(f"字體文件不存在: {font_path}")
            return "標楷體"  # 如果字體文件不存在，返回標楷體作為後備字體
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("字體加載失敗！")
            return "標楷體"  # 如果加載失敗，返回標楷體
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]
            print(f"成功加載字體-3: {font_family}")
            return font_family  # 成功加載字體
        else:
            print("未找到字體名稱")
            return "標楷體"  # 未找到字體名稱時，返回標楷體

    # 手勢開始
    def start_hand_gestures_detection(self):
        self.stop_signal.clear()  # 清除資料
        self.hand_gestures_thread = threading.Thread(target=self.hand_gestures_detection, daemon=True)
        self.hand_gestures_thread.start()

    # 手勢停止
    def stop_hand_gestures_detection(self):
        if self.hand_gestures_thread is not None:
            self.stop_signal.set()
            self.hand_gestures_thread.join()  
        self.cancel_timer()  # 在這裡取消計時器

    def hand_gestures_detection(self):
        for gesture in detect_hand_gestures():
            if self.stop_signal.is_set():  # 檢查要不要停止
                break
            self.handle_gesture(gesture)

    # 按鈕手勢對比
    def handle_gesture(self, gesture):
        print(f"Detected-2 gesture: {gesture}") 
        if gesture == 'back':
            self.highlight_button(self.prevButton)
            threading.Timer(3, self.on_prev_clicked).start()
            self.stop_signal.set()
        elif gesture == '1':
            self.highlight_button(self.button1)
            threading.Timer(3, self.difficulty_selected.emit, args=(self.button1.text(),)).start()
            self.stop_signal.set()
        elif gesture == '2':
            self.highlight_button(self.button2)
            threading.Timer(3, self.difficulty_selected.emit, args=(self.button2.text(),)).start()
            self.stop_signal.set()
        elif gesture == '3':
            self.highlight_button(self.button3)
            threading.Timer(3, self.difficulty_selected.emit, args=(self.button3.text(),)).start()
            self.stop_signal.set()
        elif gesture == '4':
            self.highlight_button(self.button4)
            threading.Timer(3, self.difficulty_selected.emit, args=(self.button4.text(),)).start()
            self.stop_signal.set()

    # 計時器開始
    def start_timer(self, button_text):
        self.cancel_timer()  
        self.timer = threading.Timer(3, self.execute_button_action, args=(button_text,))
        self.timer.start()

    # 取消計時器
    def cancel_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None 

    # 按鈕的紅框
    def highlight_button(self, button):
        self.reset_button_styles()  
        button.setStyleSheet("border: 5px solid red;")  

    # 點選到其他的按鈕會切換紅框
    def reset_button_styles(self):
        self.prevButton.setStyleSheet("")
        self.button1.setStyleSheet("")  
        self.button2.setStyleSheet("")
        self.button3.setStyleSheet("")
        self.button4.setStyleSheet("")

    # 關閉資訊
    def closeEvent(self, event):
        self.stop_hand_gestures_detection()  
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_NewSelectDifficulty()
    MainWindow.setCentralWidget(ui)

    window_rect = MainWindow.frameGeometry()
    center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
    window_rect.moveCenter(center_point)
    MainWindow.move(window_rect.topLeft())

    MainWindow.show()
    sys.exit(app.exec_())
