import random
import os
import sys
import threading
import datetime
import mysql.connector as db
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGridLayout, QWidget, QHBoxLayout, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from KL_MP_Mix import detect_hand_gestures

class Ui_Game_Start(QtWidgets.QWidget):
    delay = 50  # 文字動畫延遲
    question_number = 1  # 題號
    countdown_seconds = 364  # 倒數初始秒數
    question_updated = False
    max_space_count = 3  # 空白鍵跳題限制次數
    pass_count = 0  # 跳過次數
    total_score = 0  # 總分
    error_count = 0  # 錯誤次數 
    game_over_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)  
        self.is_active_page = True
        self.stop_signal = threading.Event()
        self.setParent(parent) 
        self.enable_text_effects = True  # 預設啟用文字特效
        self.current_question_displayed = False  # 用來標記當前題目是否已顯示

        self.animation_finished = False
        self.animation_in_progress = True
        self.question_updated = False
        self.gesture_enabled = True
        self.total_score = 0
        self.buttons = []
        self.is_first_question = True
        self.setupUi()

    def setupUi(self): 
        # 設置手勢辨識計時器
        self.gesture_timer = QTimer(self)
        self.gesture_timer.timeout.connect(self.update_gesture)
        self.gesture_timer.start(50)  # 每 50 毫秒檢測一次手勢

        # 初始化時讀取難度並根據難度設定 score
        self.team_name, self.difficulty = self.read_save_file() 
        self.score = self.get_score_for_difficulty(self.difficulty)

        # 設置主佈局
        self.layout = QVBoxLayout()
        self.setLayout(self.layout) 

        # 設定視窗
        self.setWindowTitle("MainWindow")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # 背景圖片
        self.label = QLabel(self)
        self.background = QPixmap("Font/game.jpg")
        self.update_background()
        self.label.setGeometry(0, 0, self.width(), self.height())

        # 加載字體
        font_path = os.path.join(os.path.dirname(__file__), "Font", "NaikaiFont-Bold.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(family, 20)
        self.letter_spacing = 150
        font.setLetterSpacing(QFont.PercentageSpacing, self.letter_spacing)

        # 創建頂部橫向布局
        top_layout = QHBoxLayout()

        # 題號顯示區域
        self.question_label = QLabel(f"第{self.question_number}題", self)
        self.question_label.setFont(font)
        self.question_label.setStyleSheet("background-color: transparent; color: black;")
        
        # 倒數時間顯示區域
        self.timer_label = QLabel(f"倒數時間: {self.countdown_seconds} 秒", self)
        self.timer_label.setFont(font)
        self.timer_label.setStyleSheet("background-color: transparent; color: black;")
        
        # 添加題號和倒數時間到頂部橫向佈局
        top_layout.addWidget(self.question_label, alignment=Qt.AlignLeft)
        top_layout.addStretch()  # 用於分隔題號和倒數時間
        top_layout.addWidget(self.timer_label, alignment=Qt.AlignRight)
        
        # 將頂部橫向佈局添加到主佈局頂部
        self.layout.addLayout(top_layout)

        # 設定倒數計時器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 每秒觸發一次

        # 文字顯示區域
        self.text_label = QLabel(self)
        self.text_label.setFont(font)
        self.text_label.setStyleSheet("background-color: transparent; color: black;")
        self.text_label.setAlignment(Qt.AlignCenter)
        
        # 將文字顯示區域添加到主佈局
        self.layout.addWidget(self.text_label, alignment=Qt.AlignTop | Qt.AlignCenter)

        # 選項和圖示布局容器
        self.option_widget = QWidget(self)
        self.option_layout = QGridLayout(self.option_widget)
        self.option_widget.setVisible(False)
        
        # 將選項容器添加到主佈局
        self.layout.addWidget(self.option_widget, alignment=Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 200)
        self.layout.setSpacing(0)

    # 讀取設定檔進行資料庫連線
    def get_config(self):
        config = {}
        config_path = os.path.join(os.path.dirname(__file__), 'Data', 'config.txt')
        with open(config_path, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
        return config
    
    # 連接資料庫
    def display_random_topic(self, difficulty):
        try:
            config = self.get_config()
            connection = db.connect(
                host=config['host'],
                user=config['user'],
                password=config.get('password', ''),
                database=config['database']
            )
            cursor = connection.cursor()

            # 根據難易度選擇分數
            if self.difficulty == "隨機挑戰":
                random_score = random.choice([2, 4, 6])
                cursor.execute("""
                                SELECT 題目編號, 題目, 錯字, 錯字位置 
                                FROM topic
                                WHERE 分數 = %s;
                                ORDER BY 題目編號
                                LIMIT 1;
                                """, (random_score,))
            else:
                cursor.execute("""
                                SELECT 題目編號, 題目, 錯字, 錯字位置 
                                FROM topic 
                                WHERE 分數 = %s;
                                ORDER BY 題目編號
                                LIMIT 1;
                                """, (self.score,))

            rows = cursor.fetchall()
            if rows:
                topic_id, topic, typo, typo_position = random.choice(rows)
                typo = typo[:5] if len(typo) > 5 else typo
                
                # 打印題目編號
                print(f"題目編號: {topic_id}")
                self.current_question_id = topic_id
                
                return topic or "", typo, typo_position or ""
            return "", "", ""
        except db.Error as e:
            print("資料庫錯誤:", e)
            return "", "", ""
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    # 讀取 save.txt
    def read_save_file(self):
        try:
            with open("Data/save.txt", "r", encoding="big5") as file:  
                lines = file.readlines()
                global team_name
                global difficulty
                self.team_name = lines[0].strip()
                self.difficulty = lines[1].strip()
                print(f"隊名: {self.team_name}, 難易度: {self.difficulty}")  
                return self.team_name, self.difficulty
        except FileNotFoundError:
            print("save.txt not found.")
            return None, None
        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}")
            return None, None   
     
    # 區分難易度
    def get_score_for_difficulty(self, difficulty):
        if difficulty == "簡單":
            print("簡單")
            return 2
        elif difficulty == "普通":
            print("普通")
            return 4
        elif difficulty == "困難":
            print("困難")
            return 6
        else:
            print(f"未知難易度: {difficulty}")
            return None 

    # 倒數時間判斷
    def update_timer(self):
        self.countdown_seconds -= 1
        self.timer_label.setText(f"時間: {self.countdown_seconds} 秒")

        # 檢查倒數時間是否為零
        if self.countdown_seconds <= 0:
            self.close_all_windows()

    # 關閉所有視窗
    def close_all_windows(self):
        self.write_score_to_file()
        print("關閉所有視窗")
        # self.stop_gesture_detection()
        self.game_over_signal.emit()  # 發送遊戲結束信號
        self.close()  # 關閉當前遊戲窗口
        self.is_active_page = False

    # 鍵盤事件
    def keyPressEvent(self, event):
        if self.animation_in_progress:
            print("Animation in progress. Key press ignored.")
            return

        # 處理不同按鍵
        if event.key() == Qt.Key_Space:  # 空白鍵跳題
            print("Space")
            if self.pass_count < self.max_space_count:
                self.pass_count += 1
                self.question_number += 1 
                self.clear_page()
                self.show_next_question()
                self.parent().show_pass_popup()
            else:
                self.close_all_windows()  
        elif event.key() == Qt.Key_Escape:  # Esc 顯示下一題
            print("ESC")
            self.question_number += 1
            self.clear_page()
            self.show_next_question()
        elif event.key() == Qt.Key_Q:  # Q 結束遊戲
            print("Q")
            self.close_all_windows()

    # 更新題號
    def update_question_number(self):
        self.question_number += 1
        self.question_label.setText(f"第{self.question_number}題")
        self.clear_page()  # 清除頁面
        self.show_next_question()  # 顯示下一題
        self.animation_in_progress = True  # 新一題動畫開始
        self.question_updated = True

    # 調整視窗、文字、圖片大小
    def resizeEvent(self, event):
        base_font_size = self.width() // 50 
        font = self.text_label.font()
        font.setPointSize(base_font_size)
        self.text_label.setFont(font)
        self.question_label.setFont(font)
        self.timer_label.setFont(font)

        # 縮放背景圖
        scaled_background = self.background.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_background)
        self.label.setGeometry(0, 0, self.width(), self.height())

        # 動態調整選項的字體大小
        for i in range(self.option_layout.count()):
            widget = self.option_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text():  # 檢查是否為文字的 QLabel
                widget.setFont(font)  # 設置與題目相同的字體大小

        # 動態調整圖示大小
        icon_size = min(self.width(), self.height()) // 50  # 調整圖示大小比例因子
        for i in range(self.option_layout.count()):
            widget = self.option_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.pixmap():  # 檢查是否為圖示的 QLabel
                scaled_icon = widget.pixmap().scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                widget.setPixmap(scaled_icon)

        super().resizeEvent(event)

    # 縮放背景圖
    def update_background(self):
        # 按照視窗大小縮放背景圖並設置
        scaled_background = self.background.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_background)
        self.label.setGeometry(0, 0, self.width(), self.height())

    # 清除頁面中的所有文字和選項
    def clear_page(self):
        self.text_label.clear()
        self.option_widget.setVisible(False)  # 隱藏選項和圖示
        self.question_label.setText(f"第{self.question_number}題")  # 確保題號更新
        for i in reversed(range(self.option_layout.count())):
            widget = self.option_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # 刪除現有的選項和圖示
        self.option_layout.update()  # 強制刷新佈局

        # 調整字體大小
        font = self.text_label.font()
        base_size = self.width() // 50  
        font.setPointSize(base_size)
        self.text_label.setFont(font)

    # 顯示成語題目
    def show_question_and_options(self, difficulty):
        self.clear_page()  # 確保清除舊題目和選項
        self.option_widget.setVisible(False)  # 隱藏選項，直到題目顯示完成

        while True:
            if self.difficulty == "隨機挑戰":
                self.score = random.choice([2, 4, 6])  # 設置隨機分數為 self.score
                topic, typo, typo_position = self.display_random_topic(self.score)
                print(f"題目分數: {self.score}")
            else:
                topic, typo, typo_position = self.display_random_topic(self.score)

            if not topic or not typo or not typo_position:
                print("跳過不完整的題目...")
                continue

            result = self.generate_unique_options(typo, typo_position)
            if result is None:
                print("跳過無效選項...")
                continue

            replacement_char, options = result
            topic_with_typo = list(topic)
            try:
                topic_with_typo[int(typo_position)] = replacement_char
            except (IndexError, ValueError):
                print("跳過無效替換...")
                continue

            self.current_topic = topic
            highlighted_text = ''.join(topic_with_typo)
            self.text_label.setTextFormat(Qt.RichText)

            # 顯示題目特效
            self.animation_in_progress = True
            self.show_text_with_random_effect(highlighted_text, typo, options)
            
            # 等待動畫完成後顯示選項
            QTimer.singleShot(1000, lambda: self.display_options_and_icons(options))  # 設定動畫完成延遲
            break

    def start_game(self):
        # 清空界面，等待第一題的顯示
        self.clear_page()
        self.text_label.clear()  # 確保初始時無題目顯示
        self.option_widget.setVisible(False)  # 隱藏選項
        print("遊戲開始，等待顯示第一題...")
        self.show_next_question()

    # 錯字排除，隨機選取一個錯字，排除第一個字元
    def get_random_typo(self, typo):
        # correct_answer = typo[0]
        typo_options = list(typo[1:])  # 排除第一個字元
        return random.choice(typo_options)

    # 錯字選項
    def generate_unique_options(self, typo, typo_position):
        try:
            typo_position = int(typo_position)
        except ValueError:
            print("錯誤：無效的 typo_position 值，無法轉換為整數")
            return None  # 當無法轉換時，直接返回 None，這樣可以跳過這一題

        # 確保 typo_position 在 typo 範圍內
        if typo_position < 0 or typo_position >= len(typo):
            print(f"錯誤：錯字位置 '{typo_position}' 無效，應在 0 到 {len(typo)-1} 之間")
            return None  # 如果位置錯誤，返回 None，繼續下一題

        try:
            self.correct_answer = typo[0]
            typo_options = list(typo[1:])
            
            # 確保有足夠的錯誤選項
            if len(typo_options) < 3:
                print(f"警告：錯誤選項數量不足，跳過此題")
                return None  # 如果選項不足，跳過這一題

            replacement_char = random.choice(typo_options)

            # 為題目中的錯字加上紅色標記
            highlighted_replacement_char = f"<span style='color:red'>{replacement_char}</span>"
            
            # 生成錯字選項
            unique_options = [self.correct_answer]
            typo_options = [char for char in typo_options if char != replacement_char]
            
            # 隨機選擇 3 個錯誤選項並打亂
            if len(typo_options) >= 3:
                unique_options.extend(random.sample(typo_options, 3))
            random.shuffle(unique_options)

            if len(unique_options) != 4:
                print(f"警告：生成的選項數量為 {len(unique_options)}，跳過此題")
                return None

            return highlighted_replacement_char, unique_options
        
        except Exception as e:
            print(f"錯誤：生成選項時發生錯誤，錯誤訊息：{e}")
            return None  # 若有任何錯誤，返回 None，繼續下一題

    # 選項擺放
    def display_options_and_icons(self, options):
        # 清空現有布局中的內容
        for i in reversed(range(self.option_layout.count())):
            widget = self.option_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # 刪除按鈕

        self.buttons = []  # 清空按鈕列表

        # 安排並樣式化選項和圖示
        for i, option in enumerate(options):
            button = QPushButton(option, self)  # 使用 QPushButton 替換 QLabel
            button.setFont(self.text_label.font())
            
            # 按鈕樣式
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    border: none;
                    text-align: center;
                }
            """)
            
            button.setFixedSize(250, 250)  # 設定按鈕大小
            button.setFocusPolicy(Qt.StrongFocus)
            
            # 當按鈕被點擊時，修改字體顏色為紅色
            button.clicked.connect(lambda _, btn=button: self.check_answer(btn))  

            self.buttons.append(button)

            row, col = divmod(i, 2)  # 計算行列位置
            self.option_layout.addWidget(button, row * 2, col)  # 每行放2個選項

        # 顯示圖示，並按照順序放置
        icon_paths = [f'Pic/icon{i}.png' for i in range(1, 5)]
        icons = [QPixmap(icon).scaled(150, 150, Qt.KeepAspectRatio) for icon in icon_paths if os.path.exists(icon)]
        
        # 確保圖示有4個，並將它們安排到對應位置
        icon_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  
        for pixmap, (row, col) in zip(icons, icon_positions):
            icon_label = QLabel(self)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            self.option_layout.addWidget(icon_label, row * 2 + 1, col) 

    # 圖示擺放
    def show_icons(self):
        icon_paths = [f'Pic/icon{i}.png' for i in range(1, 5)]
        icons = [QPixmap(icon).scaled(100, 100, Qt.KeepAspectRatio) for icon in icon_paths if os.path.exists(icon)]
        icon_positions = [(270, 350), (270, 450), (430, 350), (430, 450)]

        for pixmap, (x, y) in zip(icons, icon_positions):
            icon_label = QLabel(self)
            icon_label.setPixmap(pixmap)
            icon_label.setGeometry(x, y, 100, 100)
            self.option_layout.addWidget(icon_label)

    # 比出答案是變成紅色
    def check_answer(self, selected_option):
        selected_text = selected_option.text()  
        selected_option.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: red;
            }
        """)
        QTimer.singleShot(100, lambda: self.compare_answer(selected_text))  

    # 比較答案，更新資料庫記錄
    def compare_answer(self, selected_text):
        is_correct = selected_text == self.correct_answer
        question_id = self.current_question_id  # 從 display_random_topic 方法獲得
        team_name = self.team_name  # 從 `read_save_file` 中已獲取
        topic = self.current_topic  # 保存目前顯示的題目

        # 將答題記錄寫入資料庫
        self.insert_answer_record(question_id, team_name, topic, is_correct)

        # 後續答題邏輯
        if is_correct:
            print("答對了!")
            if self.score is not None and isinstance(self.score, (int, float)):
                self.total_score += self.score
            else:
                print("警告：分數未定義或類型不正確，無法加分")
            print(f"分數: {self.total_score}")
            self.parent().show_correct_popup()
        else:
            self.error_count += 1
            print(f"答錯了! 錯誤次數: {self.error_count}")
            if self.error_count == 1:
                self.parent().show_error_popup()
            elif self.error_count == 2:
                self.parent().show_error2_popup()
            elif self.error_count == 3:
                self.parent().show_error3_popup()
                QTimer.singleShot(2000, self.close_all_windows)
                return

        QTimer.singleShot(2000, self.show_next_question)
        self.update_question_number()

    # 插入答題記錄到資料庫
    def insert_answer_record(self, question_id, team_name, topic, is_correct):
        try:
            config = self.get_config()
            connection = db.connect(
                host=config['host'],
                user=config['user'],
                password=config.get('password', ''),
                database=config['database']
            )
            cursor = connection.cursor()

            # 準備插入資料
            query = """
                INSERT INTO person (題目編號, 日期, 營隊名稱, 題目, 答案)
                VALUES (%s, %s, %s, %s, %s);
            """
            current_time = datetime.datetime.now()
            answer = 0 if is_correct else 1  # 答對為 0，答錯為 1
            data = (question_id, current_time, team_name, topic, answer)

            cursor.execute(query, data)
            connection.commit()
            print("答題記錄已成功存入資料庫")
        except db.Error as e:
            print("資料庫錯誤:", e)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    # 新增方法：將團隊名稱及總分寫入 score.txt
    def write_score_to_file(self):
        try:
            # 定義檔案路徑
            file_path = os.path.join(os.getcwd(), "Data/score.txt")
            print(f"正在寫入 score.txt，檔案路徑: {file_path}") 

            # 確認要寫入的內容
            print(f"團隊名稱: {self.team_name}, 總分: {self.total_score}")

            # 檔案寫入
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(f"{self.team_name},{self.total_score}\n")

            print("團隊名稱及總分已成功追加至 score.txt")
        except Exception as e:
            print(f"寫入 score.txt 時發生錯誤: {e}")

    # 顯示下一題
    def show_next_question(self):
        self.clear_page()
        self.show_question_and_options(self.difficulty)
        self.question_label.setText(f"第{self.question_number}題")

        # 啟用文字特效，確保不直接設置文字
        if not self.enable_text_effects:
            print("文字特效已停用，直接顯示題目")
            self.text_label.setText(self.current_topic)
            self.display_options_and_icons(self.current_options)
            return

        # 初始化動畫狀態
        self.animation_finished = True
        self.animation_in_progress = True
        self.gesture_enabled = True

    # 題目動畫完成顯示選項
    def on_animation_finished(self):
        self.animation_in_progress = False
        self.option_widget.setVisible(True)  # 顯示選項

    # 文字特效方法
    def show_text_with_random_effect(self, text1, typo, options):
        if not self.enable_text_effects:
            print("文字特效已停用，直接顯示題目")
            self.text_label.setText(text1)  # 直接設置文字
            self.animation_in_progress = False
            self.animation_finished = True
            self.display_options_and_icons(options)  # 顯示選項
            return

        # 初始化動畫狀態
        self.animation_in_progress = True
        self.animation_finished = False

        # 設置字體間距
        font = self.text_label.font()
        font.setLetterSpacing(QFont.PercentageSpacing, 200)
        self.text_label.setFont(font)

        # 判斷是否是第一次顯示
        if self.is_first_question:
            print("第一次顯示，使用淡入效果 (Fade-in Effect)")
            selected_effect = self.make_text_fade_in_effect
            self.is_first_question = False  # 將狀態設置為 False
        else:
            # 隨機選擇特效
            effects = [self.make_text_typewriter_effect,
                    self.make_text_fade_in_effect, self.make_text_slide_in_effect]
            selected_effect = random.choice(effects)

        # 顯示所選特效的訊息
        effect_name = {
            self.make_text_typewriter_effect: "使用的是打字機效果 (Typewriter Effect)",
            self.make_text_fade_in_effect: "使用的是淡入效果 (Fade-in Effect)",
            self.make_text_slide_in_effect: "使用的是滑動進入效果 (Slide-in Effect)"
        }
        print(effect_name[selected_effect])

        try:
            selected_effect(text1, typo, lambda: self.on_effect_finished(options))
        except Exception as e:
            print(f"文字特效失敗：{e}")
            self.enable_text_effects = False  # 停用文字特效
            self.text_label.setText(text1)  # 直接顯示文字
            self.animation_in_progress = False
            self.animation_finished = True
            self.display_options_and_icons(options)  # 顯示選項
 
    def on_effect_finished(self, options):
        self.animation_in_progress = False  # 動畫結束，允許鍵盤事件
        self.animation_finished = True  # 動畫完成
        self.option_widget.setVisible(True)
        self.display_options_and_icons(options)

    # 文字特效1-打字機
    def make_text_typewriter_effect(self, text1, text2, on_finished):
        full_text = f"{text1}"  # 完整文字
        step = 0

        def update_text():
            nonlocal step
            if step < len(full_text):
                # 只更新新增的部分
                self.text_label.setText(full_text[:step + 1])
                step += 1
            else:
                timer.stop()
                on_finished()  # 完成後調用回調函數

        timer = QTimer(self)
        timer.timeout.connect(update_text)
        timer.start(30)

    # 文字特效2 - 淡入
    def make_text_fade_in_effect(self, text1, text2, on_finished):
        self.text_label.setText(text1)
        effect = QGraphicsOpacityEffect(self.text_label)
        self.text_label.setGraphicsEffect(effect)
        opacity = 0.0

        def update_opacity():
            nonlocal opacity
            if opacity < 1.0:
                opacity += 0.2
                effect.setOpacity(opacity)  # 直接設置透明度
            else:
                timer.stop()
                on_finished()

        timer = QTimer(self)
        timer.timeout.connect(update_opacity)
        timer.start(50)

    # 文字特效3 - 滑入
    def make_text_slide_in_effect(self, text1, text2, on_finished):
        self.text_label.setText(text1)  # 設置文字
        self.text_label.adjustSize()  # 只執行一次

        # 起始和結束位置
        start_x = self.width()
        end_x = (self.width() - self.text_label.width()) // 2
        current_x = start_x

        def update_position():
            nonlocal current_x
            if current_x > end_x:
                current_x -= 20  # 固定每次移動距離
                self.text_label.move(current_x, self.text_label.y())
            else:
                self.text_label.move(end_x, self.text_label.y())  # 確保停留在正確位置
                timer.stop()
                on_finished()

        timer = QTimer(self)
        timer.timeout.connect(update_position)
        timer.start(16)  # 每次更新時間間隔

    # 開始手勢辨識
    def start_gesture_detection(self):
        self.stop_signal.clear() 

        # 創建新的手勢辨識執行緒
        self.gesture_thread = threading.Thread(target=self.update_gesture, daemon=True)
        self.gesture_thread.start()

    # 手勢辨識功能
    def update_gesture(self):
        if not self.gesture_enabled: 
            print("手勢辨識已禁用，等待下一題")
            return
        
        if self.animation_in_progress:
            print("動畫進行中，忽略手勢檢測")
            return
        
        if not self.is_active_page:  # 如果頁面未啟動，忽略手勢
            return
        
        gestures = detect_hand_gestures()  # 確保這裡返回的是一個生成器
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
        if gesture == "PASS":
            print("偵測到手勢 8，模擬空白鍵行為")
            if self.pass_count < self.max_space_count:
                self.pass_count += 1
                self.question_number += 1  # 題號增加
                self.gesture_enabled = False
                self.clear_page()
                self.show_next_question()
                self.parent().show_pass_popup()
            else:
                self.close_all_windows()  # 超過次數，結束遊戲
        elif gesture == "1":
            self.gesture_enabled = False
            print("選擇選項 1")
            self.select_option(0)
        elif gesture == "2":
            self.gesture_enabled = False
            print("選擇選項 2")
            self.select_option(1)
        elif gesture == "3":
            self.gesture_enabled = False
            print("選擇選項 3")
            self.select_option(2)
        elif gesture == "4":
            self.gesture_enabled = False
            print("選擇選項 4")
            self.select_option(3)
        else:
            print("未匹配的手勢:", gesture)

    # 手勢選擇的選項
    def select_option(self, option_index):
        if 0 <= option_index < len(self.buttons):
            button = self.buttons[option_index]  
            self.check_answer(button) 

    # 停止手勢辨識功能
    def stop_gesture_detection(self):
        print("停止手勢辨識功能")
        # 釋放攝影機或其他資源
        if hasattr(self, 'gesture_thread') and self.gesture_thread.isRunning():
            self.gesture_thread.quit()
            self.gesture_thread.wait()
        if hasattr(self, 'camera'):
            self.camera.release()  # 停止攝影機

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    game_start = Ui_Game_Start()
    game_start.show()
    sys.exit(app.exec_())