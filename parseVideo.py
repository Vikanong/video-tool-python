import cv2
import os
from skimage.metrics import structural_similarity as ssim
import tkinter as tk
from tkinter import filedialog
import threading
import requests


send_webhook = ""


def sendMessage(txt):
    headers = {
        "Content-Type": "application/json",
    }
    param = {"msgtype": "text", "text": {"content": "叮：" + txt}}
    response = requests.post(url=send_webhook, headers=headers, json=param)
    result = response.json()

class ParseVideo:
    def __init__(self, frame, sendMessage):
        self.frame = frame
        self.video_path = ""  # 选择原视频地址
        self.images_output_path = ""  # 选择生成图片文件夹
        self.sendMessage = sendMessage

    def create_ui(self):
        # 功能标题 Title
        video_cover_title = tk.Label(self.frame, text="解析视频图片", font=["微软雅黑", 14])
        video_cover_title.grid(row=0, column=0, sticky="w")

        # 选择视频
        original_select_button = tk.Button(
            self.frame,
            text="选择原视频",
            command=self.select_original_video,
            width=22,
        )
        original_select_button.grid(row=1, column=0, sticky="w", pady=10)

        self.original_video_path_label = tk.Label(self.frame, text="")
        self.original_video_path_label.grid(row=1, column=1, sticky="w")

        output_select_button = tk.Button(
            self.frame,
            text="选择解析后图片存放路径",
            command=self.select_images_output_path,
            width=22,
        )
        output_select_button.grid(row=2, column=0, sticky="w", pady=10)

        self.images_output_path_label = tk.Label(self.frame, text="")
        self.images_output_path_label.grid(row=2, column=1, sticky="w")

        # 开始解析
        start_parsing = tk.Button(
            self.frame,
            text="快速生成",
            command=self.start_background_thread,
            width=22,
            height=2,
        )
        start_parsing.grid(row=3, column=0, sticky="w", pady=10)

        # 创建Label用于显示日志
        self.log_label = tk.Label(
            self.frame, text="", height=1, width=30, anchor="nw", justify="left"
        )
        self.log_label.grid(row=4, column=0, sticky="w", columnspan=3, pady=10)

    def select_original_video(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(filetypes=[("Video File", "*.mp4")])
        if not file_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.video_path = file_path
        print(file_path)

        # 获取文件名
        file_name = file_path.split("/")[-1]  # 从文件路径中提取文件名
        # 在标签中显示文件名
        self.original_video_path_label.config(text=f"已选择文件: {file_name}")

    def select_images_output_path(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.images_output_path = folder_path
        self.images_output_path_label.config(text=folder_path)

        print("选择输出文件夹", self.images_output_path)

    def start_background_thread(self):
        if not self.video_path:
            self.log("请选择原视频")
            return

        if not self.images_output_path:
            self.log("选择输出文件夹")
            return

        # 创建后台线程来执行请求
        background_thread = threading.Thread(target=self.start_generate)
        background_thread.start()

    def log(self, message):
        self.log_label.config(text=message)

    def start_generate(self):
        self.log("开始解析")

        self.sendDingtalk("开始解析")

        # 容错率阈值，可以根据需要调整
        tolerance_threshold = 0.538

        # 间隔帧数，如果未设置间隔帧数，则将其设置为 None
        frame_interval = None  # 设置为 None 或其他负数值以禁用间隔帧对比

        # 最小模糊度阈值，可以根据需要调整
        min_blur_threshold = 30

        # 确保输出文件夹存在
        os.makedirs(self.images_output_path, exist_ok=True)

        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)

        # 用于记录当前帧索引
        frame_index = 0

        # 初始化 previous_frame 为第一帧的灰度图像
        ret, frame = cap.read()
        previous_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 用于记录跳过的帧数
        skip_frames = 10  # 跳过前面10帧

        self.log("解析中，请稍后...")

        while True:
            # 读取当前帧
            ret, frame = cap.read()

            # 到达视频末尾
            if not ret:
                break

            if frame_index < skip_frames:
                frame_index += 1
                continue  # 跳过前面的模糊帧

            # 将图像转换为灰度图像
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 计算图像的模糊度
            blur_score = cv2.Laplacian(gray_frame, cv2.CV_64F).var()

            # 如果图像模糊度高于阈值，认为是清晰的图像
            is_clear = blur_score >= min_blur_threshold

            if not is_clear:
                continue

            if frame_interval is None or frame_interval <= 0:
                # 如果未设置间隔帧数，或者 frame_interval 为负数，则与上一帧做对比
                ssim_score = ssim(previous_frame, gray_frame)
            else:
                # 如果设置了间隔帧数，只在间隔帧上执行对比
                if frame_index % frame_interval == 0:
                    ssim_score = ssim(previous_frame, gray_frame)
                else:
                    ssim_score = 0  # 设置为0以跳过对比

            # 如果图像清晰且相似度低于容错率阈值，则认为是相同的图片
            if is_clear and ssim_score < tolerance_threshold:
                # 保存该图像到输出文件夹
                output_path = os.path.join(
                    self.images_output_path, f"frame_{frame_index}.jpg"
                )
                cv2.imwrite(output_path, frame)

            # 更新 previous_frame 为当前帧的灰度图像
            previous_frame = gray_frame

            frame_index += 1

        # 释放视频捕获对象
        cap.release()
        cv2.destroyAllWindows()

        log = "解析完成，请到 " + self.images_output_path + " 文件夹内查"
        self.log(log)

        self.sendDingtalk(log)

    def main(self):
        self.create_ui()
        

def center_window(width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()

    # 设置窗口大小
    window_width = 400
    window_height = 400
    # 将窗口置于屏幕中央
    center_window(window_width, window_height)

    video_pictures_frame = tk.Frame(root, padx=50, pady=20)
    video_pictures_frame.grid(row=0, column=2, sticky="nw")  # 使用grid布局

    parseVideo = ParseVideo(video_pictures_frame, sendMessage)
    parseVideo.main()

    root.mainloop()