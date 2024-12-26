import os
import random
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from KL_MP_Mix import detect_hand_gestures

class Ui_NewSelectName(QtWidgets.QWidget):
    role_selected = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hand_gestures_thread = None
        self.stop_signal = threading.Event()  
        self.timer = None
        self.button_texts = self.load_button_texts('Data/camp.txt')  # 團隊名稱txt檔
        self.custom_font = self.load_custom_font('Font\\NaikaiFont-Bold.ttf') # 字體位置
        self.media_player = QMediaPlayer()  
        self.setupUi()
        self.schedule_sound_playback()  

    def setupUi(self):
        self.setObjectName("MainWindow")
        screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
        self.setGeometry(screen_geometry)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # 使用垂直布局並讓其填滿空間
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)
        self.verticalLayout.setContentsMargins(20, 50, 10, 10) 

        # 請選擇團隊名稱 標題
        self.label = QtWidgets.QLabel(self.centralwidget)
        if self.custom_font: 
            font = QtGui.QFont(self.custom_font, 48)
            self.label.setFont(font)
        else:
            self.label.setFont(QtGui.QFont("標楷體", 48))  
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.label)

        # 簡單文字+圖片 說明
        self.gesture_label = QtWidgets.QLabel(self.centralwidget)
        if self.custom_font:
            font = QtGui.QFont(self.custom_font, 24)
            self.gesture_label.setFont(font)
        else:
            self.gesture_label.setFont(QtGui.QFont("標楷體", 24))
        self.gesture_label.setAlignment(QtCore.Qt.AlignCenter)
        gesture_text = '請比出手勢來進行選擇團隊名稱!'
        self.gesture_label.setText(gesture_text)
        self.verticalLayout.addWidget(self.gesture_label)

        # GroupBox
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setStyleSheet("QGroupBox { border: none; }")
        self.groupBox.setTitle("")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(10)
        self.verticalLayout.addWidget(self.groupBox)

        # 團隊按鈕與圖片
        if len(self.button_texts) >= 6:
            selected_images = ["icon1.png", "icon2.png", "icon3.png", "icon4.png", "icon8.png", "icon9.png"]
            selected_texts = random.sample(self.button_texts, 6)

            # 上排
            self.button1 = self.add_button_with_icon(selected_texts[0], selected_images[0], 0, 0)
            self.button2 = self.add_button_with_icon(selected_texts[1], selected_images[1], 0, 1)
            self.button3 = self.add_button_with_icon(selected_texts[2], selected_images[2], 0, 2)

            # 下排
            self.button4 = self.add_button_with_icon(selected_texts[3], selected_images[3], 1, 0)
            self.button5 = self.add_button_with_icon(selected_texts[4], selected_images[4], 1, 1)
            self.button6 = self.add_button_with_icon(selected_texts[5], selected_images[5], 1, 2)
        else:
            print("camp.txt 文件中需要至少有 6 行文字")

        self.setLayout(self.verticalLayout)

        self.retranslateUi()

    # 設定聲音播放計畫
    def schedule_sound_playback(self):
        QTimer.singleShot(2000, self.play_sound)  # 2秒後執行 play_sound

    # 播放聲音的方法
    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(__file__), 'sound', 'Select_Name_sound.mp3')  
        if not os.path.exists(mp3_path):
            print(f"MP3 檔案不存在: {mp3_path}")
            return
        
        url = QUrl.fromLocalFile(mp3_path)
        content = QMediaContent(url)
        self.media_player.setMedia(content)
        self.media_player.setVolume(80) 
        self.media_player.play()

    # 標題
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "請選擇團隊名稱"))

    # 按鈕+圖片
    def add_button_with_icon(self, text, icon_filename, row, column):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignCenter)

        # 左側圖片
        left_icon_label = QtWidgets.QLabel()
        left_img_path = os.path.join(os.path.dirname(__file__), 'imgrole', icon_filename)
        left_pixmap = QtGui.QPixmap(left_img_path)
        left_icon_label.setPixmap(left_pixmap)
        left_icon_label.setFixedSize(200, 200)
        left_icon_label.setScaledContents(True)

        # 按鈕
        button = QtWidgets.QPushButton(text, self.groupBox)
        if self.custom_font:
            font = QtGui.QFont(self.custom_font, 30)
            button.setFont(font)
        else:
            button.setFont(QtGui.QFont("標楷體", 30))
        button.setMinimumHeight(200)
        button.setFixedWidth(400)
        
        # 添加到按鈕布局
        button_layout.addWidget(left_icon_label)
        button_layout.addWidget(button)

        # 將按鈕布局添加到主布局
        self.gridLayout.addLayout(button_layout, row, column)
        button.clicked.connect(lambda: self.role_selected.emit(text))  
        return button

    # 讀取txt的內容
    def load_button_texts(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return [line.strip() for line in lines if line.strip()]
    
    # 字體
    def load_custom_font(self, font_path):
        if not os.path.exists(font_path):
            print(f"字體文件不存在: {font_path}")
            return None
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("字體加載失敗！")
            return None
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]
            print(f"成功加載字體-1: {font_family}")
            return font_family  
        else:
            print("未找到字體名稱")
            return None

    # 手勢開始
    def start_hand_gestures_detection(self):
        self.stop_signal.clear()  
        self.hand_gestures_thread = threading.Thread(target=self.hand_gestures_detection, daemon=True)
        self.hand_gestures_thread.start()

    # 手勢停止
    def stop_hand_gestures_detection(self):
        if self.hand_gestures_thread is not None:
            self.stop_signal.set()
            self.hand_gestures_thread.join() 
        self.cancel_timer()  

    def hand_gestures_detection(self):
        for gesture in detect_hand_gestures():
            if self.stop_signal.is_set():  
                break
            self.handle_gesture(gesture)

    # 按鈕手勢對比
    def handle_gesture(self, gesture):
        print(f"Detected gesture: {gesture}")  
        if gesture == '1':
            self.highlight_button(self.button1)
            threading.Timer(3, self.execute_button_action, args=(self.button1.text(),)).start()
            self.stop_signal.set()  
        elif gesture == '2':
            self.highlight_button(self.button2)
            threading.Timer(3, self.execute_button_action, args=(self.button2.text(),)).start()
            self.stop_signal.set() 
        elif gesture == '3':
            self.highlight_button(self.button3)
            threading.Timer(3, self.execute_button_action, args=(self.button3.text(),)).start()
            self.stop_signal.set()  
        elif gesture == '4':
            self.highlight_button(self.button4)
            threading.Timer(3, self.execute_button_action, args=(self.button4.text(),)).start()
            self.stop_signal.set()  
        elif gesture == '5':
            self.highlight_button(self.button5)
            threading.Timer(5, self.execute_button_action, args=(self.button5.text(),)).start()
            self.stop_signal.set()  
        elif gesture == '6':
            self.highlight_button(self.button6)
            threading.Timer(3, self.execute_button_action, args=(self.button6.text(),)).start()
            self.stop_signal.set()  

    def execute_button_action(self, button_text):
        print(f"執行按鈕的動作: {button_text}")
        self.role_selected.emit(button_text)

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
        self.button1.setStyleSheet("")  
        self.button2.setStyleSheet("")
        self.button3.setStyleSheet("")
        self.button4.setStyleSheet("")
        self.button5.setStyleSheet("")
        self.button6.setStyleSheet("")    

    # 關閉資訊
    def closeEvent(self, event):
        self.stop_hand_gestures_detection()  
        event.accept()  

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_NewSelectName()
    MainWindow.setCentralWidget(ui)

    window_rect = MainWindow.frameGeometry()
    center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
    window_rect.moveCenter(center_point)
    MainWindow.move(window_rect.topLeft())

    MainWindow.show()
    sys.exit(app.exec_())