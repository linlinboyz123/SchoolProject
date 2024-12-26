import os
import sys
import subprocess
import threading
from PyQt5 import QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QScrollArea, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap

from KL_MP_Mix import detect_hand_gestures

class RankWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MainWindow")
        self.audio_player = QtMultimedia.QMediaPlayer(self)  
        self.resize(400, 600)
        self.is_closing = False
        self.setupUi()

    def setupUi(self): 
        # 設置手勢辨識計時器
        self.gesture_timer = QTimer(self)
        self.gesture_timer.timeout.connect(self.update_gesture)
        self.gesture_timer.start(50)  # 每 50 毫秒檢測一次手勢

        # 字體路徑
        font_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "Font", "NaikaiFont-Bold.ttf")
        print(f"字體路徑：{font_path}")

        # 載入字體
        if not os.path.exists(font_path):
            print(f"錯誤：無法找到字體檔案 {font_path}")
            self.custom_font_family = "Arial"  # 後備字體
        else:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print(f"錯誤：無法載入字體檔案 {font_path}")
                self.custom_font_family = "Arial"
            else:
                custom_fonts = QFontDatabase.applicationFontFamilies(font_id)
                self.custom_font_family = custom_fonts[0] if custom_fonts else "Arial"
        self.layout = QVBoxLayout()

        # 標題
        self.title_label = QLabel("🏆 排行榜 🏆")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # 排行榜內容
        scores, self.last_entry_index = self.get_ranked_scores()
        self.score_labels = []
        if not scores:
            self.no_data_label = QLabel("目前沒有任何紀錄！")
            self.no_data_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.no_data_label)
        else:
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)

            self.scroll_content = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_content)

            # 顯示5筆資料（根據last_entry_index的排名進行判斷）
            total_scores = len(scores)
            if total_scores < 5:
                # 如果總資料不足5筆，顯示所有資料
                selected_scores = scores
            else:
                # 確保顯示5筆資料，優先以last_entry_index為中心
                if self.last_entry_index - 2 < 0:
                    # 如果last_entry_index在靠前的位置
                    start_index = 0
                    end_index = 5
                elif self.last_entry_index + 3 > total_scores:
                    # 如果last_entry_index在靠後的位置
                    start_index = total_scores - 5
                    end_index = total_scores
                else:
                    # 如果last_entry_index在中間的位置
                    start_index = self.last_entry_index - 2
                    end_index = self.last_entry_index + 3

                selected_scores = scores[start_index:end_index]

            for idx, (team_name, score) in enumerate(selected_scores, start=start_index + 1):
                score_label = QLabel(f"{idx}. {team_name} - {score}")
                score_label.setAlignment(Qt.AlignCenter)
                # 如果是最後一行新增的資料，顯示為紅色
                if idx - 1 == self.last_entry_index:
                    score_label.setStyleSheet("color: red; font-weight: bold; margin: 5px;")
                else:
                    score_label.setStyleSheet("margin: 5px;")
                self.scroll_layout.addWidget(score_label)
                self.score_labels.append(score_label)

            self.scroll_area.setWidget(self.scroll_content)
            self.layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()
        # 關閉按鈕及其圖片
        self.close_button = QPushButton("關閉遊戲")
        self.close_button.setFixedSize(400, 100)  
        self.close_button.clicked.connect(self.close)

        close_button_layout = QHBoxLayout()
        close_button_layout.addWidget(self.close_button)

        # 載入 icon5 圖片
        icon5_path = os.path.join(os.path.dirname(__file__), "img", "icon5.png")
        icon5_label = QLabel()
        icon5_label.setPixmap(QPixmap(icon5_path).scaled(200, 200, Qt.KeepAspectRatio))
        close_button_layout.addWidget(icon5_label)

        self.button_layout.addLayout(close_button_layout)

        # 新增按鈕及其圖片
        self.new_button = QPushButton("再玩一次")
        self.new_button.setFixedSize(400, 100)  
        self.new_button.clicked.connect(self.restart_game)

        new_button_layout = QHBoxLayout()
        new_button_layout.addWidget(self.new_button)

        # 載入 icon6 圖片
        icon6_path = os.path.join(os.path.dirname(__file__), "img", "icon6.png")
        icon6_label = QLabel()
        icon6_label.setPixmap(QPixmap(icon6_path).scaled(200, 520, Qt.KeepAspectRatio))
        new_button_layout.addWidget(icon6_label)

        self.button_layout.addLayout(new_button_layout)

        self.layout.addLayout(self.button_layout)

        # 在按鈕下方插入空白占位符
        spacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)
        self.setLayout(self.layout)
        self.update_font_sizes()

    # 調整視窗
    def resizeEvent(self, event):
        self.update_font_sizes()
        super().resizeEvent(event)

    # 調整字體大小
    def update_font_sizes(self):
        width = self.width()

        # 動態計算字體大小
        title_font_size = max(width // 45, 12)  # 標題字體大小
        content_font_size = max(width // 70, 10)  # 內容字體大小
        button_font_size = max(width // 65, 10)  # 按鈕字體大小

        # 更新標題字體
        self.title_label.setFont(QFont(self.custom_font_family, title_font_size))

        # 更新內容字體
        if hasattr(self, "no_data_label"):
            self.no_data_label.setFont(QFont(self.custom_font_family, content_font_size))
        else:
            for label in self.score_labels:
                label.setFont(QFont(self.custom_font_family, content_font_size))

        # 更新按鈕字體
        self.close_button.setFont(QFont(self.custom_font_family, button_font_size))
        self.new_button.setFont(QFont(self.custom_font_family, button_font_size))

    # 讀取 score.txt
    def get_ranked_scores(self):
        scores = []
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "Data", "score.txt")
        print(f"讀取文字檔路徑：{file_path}")

        # 檢查文字檔是否存在
        if not os.path.exists(file_path):
            print(f"錯誤：檔案不存在 {file_path}")
            return [], -1

        last_entry = None  # 用來記錄最後一行新增的資料
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    team_name, score = line.strip().split(",")
                    scores.append((team_name, int(score)))
                if lines:
                    # 記錄最後一行的內容
                    last_entry = lines[-1].strip()
        except Exception as e:
            print(f"讀取檔案時發生錯誤：{e}")
            return [], -1

        # 按分數排序，並找出最後新增資料的索引
        scores.sort(key=lambda x: x[1], reverse=True)
        last_entry_index = -1
        if last_entry:
            try:
                last_team_name, last_score = last_entry.split(",")
                last_entry_index = scores.index((last_team_name, int(last_score)))
            except ValueError:
                print("警告：最後一筆資料可能不在排序結果中")

        return scores, last_entry_index
    
    # 設定聲音播放計畫
    def schedule_sound_playback(self):
        QTimer.singleShot(2000, self.play_sound)  

    # 播放聲音的方法
    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(__file__), 'sound', 'rank_sound.mp3')  
        if not os.path.exists(mp3_path):
            print(f"MP3 檔案不存在: {mp3_path}")
            return
        
        url = QUrl.fromLocalFile(mp3_path)
        content = QMediaContent(url)
        self.audio_player.setMedia(content)
        self.audio_player.setVolume(80)  
        self.audio_player.play()

    # 到這個頁面才會撥放聲音
    def showEvent(self, event):
        super().showEvent(event)
        self.play_sound()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.audio_player.stop()

    # 再玩一次
    def restart_game(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
        script_path = os.path.join(current_dir, '..', 'NewStack_Manager.py') 

        # 檢查檔案是否存在
        if not os.path.exists(script_path):
            print(f"錯誤：找不到 NewStack_Manager.py 檔案，路徑: {script_path}")
            return

        print(f"啟動新頁面: {script_path}")

        try:
            # 啟動新程式，將 stdout 和 stderr 定向到子進程
            subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 延遲退出，讓新進程有時間啟動
            QTimer.singleShot(100, lambda: sys.exit())
        except Exception as e:
            print(f"錯誤：無法啟動 NewStack_Manager.py，原因: {e}")

    # 關閉
    def close(self):
        if self.is_closing:  # 如果已經在執行，直接返回
            return
        self.is_closing = True
        try:
            app = QtWidgets.QApplication.instance()
            if app:
                app.quit()  # 確保退出 QApplication 主迴圈
                sys.exit()
        finally:
            self.is_closing = False

    # 手勢辨識功能
    def update_gesture(self):
        gestures = detect_hand_gestures()  
        try:
            gesture = next(gestures)
            print(f"偵測到的手勢: '{gesture}' 類型: {type(gesture)}")
            
            if not gesture:  # 如果手勢值為空，直接返回
                print("手勢值無效或為空:", gesture)
                return
        except (StopIteration, ValueError):
            print("沒有偵測到任何手勢或手勢值無效")
            return
        
        # 手勢與動作對應
        if gesture == "back":
            self.close_button.click()
            print("back")
        elif gesture == "ok":
            self.new_button.click()
            print("ok")
        else:
            print("未匹配的手勢:", gesture)

    # 停止手勢辨識功能
    def stop_gesture_detection(self):
        print("停止手勢辨識功能")
        # 釋放攝影機或其他資源
        if hasattr(self, 'gesture_thread') and self.gesture_thread.isRunning():
            self.gesture_thread.quit()
            self.gesture_thread.wait()
        if hasattr(self, 'camera'):
            self.camera.release()  # 停止攝影機

# 主程式
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RankWindow()
    window.show()
    sys.exit(app.exec_())
