import cv2
import mediapipe as mp
import math
import os
import sys

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

PWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(PWD, '..'))

SCPU_FW_PATH = os.path.join(PWD, '/res/firmware/KL520/fw_scpu.bin')
NCPU_FW_PATH = os.path.join(PWD, '/res/firmware/KL520/fw_ncpu.bin')
MODEL_FILE_PATH = os.path.join(PWD, '/res/models/KL520/tiny_yolo_v3/models_520.nef')


# 根據兩點的座標，計算角度
def vector_2d_angle(v1, v2):
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_ = math.degrees(math.acos((v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle_ = 180
    return angle_

# 根據傳入的 21 個節點座標，得到該手指的角度
def hand_angle(hand_):
    angle_list = []
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[2][0])), (int(hand_[0][1]) - int(hand_[2][1]))),
        ((int(hand_[3][0]) - int(hand_[4][0])), (int(hand_[3][1]) - int(hand_[4][1])))
    )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
        ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
    )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
        ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
    )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
        ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
    )
    angle_list.append(angle_)
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
        ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
    )
    angle_list.append(angle_)
    return angle_list

# 根據手指角度的串列內容，返回對應的手勢名稱
def hand_pos(finger_angle):
    f1 = finger_angle[0]   # 大拇指角度
    f2 = finger_angle[1]   # 食指角度
    f3 = finger_angle[2]   # 中指角度
    f4 = finger_angle[3]   # 無名指角度
    f5 = finger_angle[4]   # 小拇指角度

    # <50度=伸直 >50度=彎曲
    if f1 < 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50: 
        return 'PASS'
    elif f1 >= 50 and f2 >= 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
        return 'no!!!'
    elif f1 >= 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 < 50:
        return 'no'
    elif f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
        return '1'
    elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
        return '2'
    elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 > 50:
        return '3'
    elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50:
        return '4'
    elif f1 <50 and f2 <50 and f3 <50 and f4 <50 and f5<50:
        return '5'
    elif f1 <50 and f2 >=50 and f3 >=50 and f4 >=50 and f5<50:
        return '6'
    elif f1 >= 50 and f2 >= 50 and f3 < 50 and f4 < 50 and f5 < 50:
        return 'ok'
    elif f1 < 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
        return 'back'  
    else:
        return ''

def detect_hand_gestures():
    cap = None
    backends = [cv2.CAP_DSHOW,  cv2.CAP_FFMPEG]  # 優先選擇的後端
    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened successfully with backend: {backend}")
            break
        else:
            print(f"Failed to open camera with backend: {backend}")

    if not cap or not cap.isOpened():
        print("Cannot open camera with any backend")
        exit()

    # 嘗試設定解析度
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    with mp_hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        # 檢查攝影機是否開啟
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        
        w, h = 540, 310  # 設定圖像縮小的尺寸

        while True:
            ret, img = cap.read()  # 嘗試讀取攝影機幀
            if not ret:
                print("Cannot receive frame")  # 如果未能成功讀取，顯示錯誤訊息
                break  # 退出循環，停止手勢偵測
            
            # 確保 img 不是 None 再進行 resize
            try:
                img = cv2.resize(img, (w, h))  # 縮小圖像，加快處理速度
            except cv2.error as e:
                print(f"Error resizing image: {e}")  # 捕獲可能的 resize 錯誤
                continue  # 跳過這一幀

            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 轉換成 RGB 色彩
            results = hands.process(img2)  # 使用 MediaPipe 偵測手勢
            
            # 偵測手勢後處理
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    finger_points = []  # 記錄手指節點座標
                    for i in hand_landmarks.landmark:
                        x = i.x * w
                        y = i.y * h
                        finger_points.append((x, y))
                    
                    if finger_points:
                        finger_angle = hand_angle(finger_points)  # 計算手指角度
                        text = hand_pos(finger_angle)  # 根據手指角度判斷手勢
                        yield text  # 返回手勢名稱

            # 按下 'q' 鍵退出
            if cv2.waitKey(5) == ord('q'):
                break

    # 確保退出時釋放攝影機資源
    cap.release()
    cv2.destroyAllWindows()
