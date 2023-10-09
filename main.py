import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
from audio import AudioMaker
from trans import Translator
from video import VideoMaker
import requests
from compress import VideoCompress

# 语言列表
# "中文": "zh-CN",
# "英语": "en",
# "法语": "fr",
# "韩语": "ko",
# "日语": "ja",
# "菲律宾语": "tl",

dingtalk_webhook = ""


def sendDingtalk(txt):
    headers = {
        "Content-Type": "application/json",
    }
    param = {"msgtype": "text", "text": {"content": "叮：" + txt}}
    response = requests.post(url=dingtalk_webhook, headers=headers, json=param)
    result = response.json()


class GUIAPP:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI")
        self.selected_language = ""
        self.selected_language_txt = ""
        self.option_dict = {
            "中文": "zh-CN",
            "英语": "en",
            "法语": "fr",
            "韩语": "ko",
            "日语": "ja",
            "菲律宾语": "tl",
        }
        self.images_select_path = ""  # 选择图片文件夹
        self.subtitlesTXT_path = ""  # 选择初始字幕文件

        self.output_video_path = ""  # 输出视频路径
        self.audio_speed = 1.1  # 语音速度
        self.is_translated_subtitles = tk.IntVar(value=1)  # 是否选择翻译后字幕

        self.datas_path = "./Datas"  # 选择Datas文件夹

        self.original_path = ""  # 压缩视频选择原视频地址
        self.zip_output_path = ""  # 压缩视频选择输出视频地址
        self.output_bitrate = 1000  # 压缩视频选择码率
        self.cover_img_path = ""  # 视频封面地址

        self.original_video_cover_path = ""  # 封面视频选择原视频地址
        self.generate_video_cover_output_path = ""  # 封面视频选择输出视频地址
        self.cover_image_path = ""  # 视频封面地址

    # 添加视频封面
    def video_cover_image(self):
        # 创建一个Frame来容纳窗口中的所有控件
        video_cover_frame = tk.Frame(self.root, padx=50, pady=20)
        video_cover_frame.grid(row=0, column=3, sticky="nw")  # 使用grid布局

        # 功能标题 Title
        video_cover_title = tk.Label(video_cover_frame, text="添加视频封面", font=["微软雅黑", 14])
        video_cover_title.grid(row=0, column=0, sticky="w")

        # 选择视频
        original_select_button = tk.Button(
            video_cover_frame, text="选择原视频", command=self.select_original_video_cover_path, width=22
        )
        original_select_button.grid(row=1, column=0, sticky="w", pady=10)

        self.original_video_cover_path_label = tk.Label(video_cover_frame, text="")
        self.original_video_cover_path_label.grid(row=1, column=1, sticky="w")

        # 选择视频封面
        cover_label = tk.Label(video_cover_frame, text="选择视频封面图：")
        cover_label.grid(row=2, column=0, sticky="w", pady=[10, 0])

        cover_button = tk.Button(video_cover_frame, text="选择图片", command=self.choose_cover_image, width=22)
        cover_button.grid(row=3, column=0, sticky="w", pady=10)

        self.cover_image_path_label = tk.Label(video_cover_frame, text="")
        self.cover_image_path_label.grid(row=3, column=1, sticky="w")

        output_select_button = tk.Button(
            video_cover_frame,
            text="选择添加封面后视频路径",
            command=self.select_cover_output_path,
            width=22,
        )
        output_select_button.grid(row=4, column=0, sticky="w", pady=10)

        self.cover_output_path_label = tk.Label(video_cover_frame, text="")
        self.cover_output_path_label.grid(row=4, column=1, sticky="w")

        # 生成带封面视频
        video_cover_button = tk.Button(
            video_cover_frame,
            text="生成带封面视频",
            command=self.video_cover_thread,
            width=22,
            height=2,
        )
        video_cover_button.grid(row=5, column=0, sticky="w", pady=10)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_ui(self):
        # 创建一个Frame来容纳窗口中的所有控件
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nw")  # 使用grid布局

        # 功能标题 Title
        function_title = tk.Label(main_frame, text="步骤生成视频工具", font=["微软雅黑", 14])
        function_title.grid(row=0, column=0, sticky="w")

        images_label = tk.Label(main_frame, text="图片：")
        images_label.grid(row=1, column=0, sticky="w", pady=[10, 0])

        select_button = tk.Button(
            main_frame, text="选择图片列表", command=self.select_images, width=22
        )
        select_button.grid(row=2, column=0, sticky="w", pady=10)

        self.file_images_label = tk.Label(main_frame, text="")
        self.file_images_label.grid(row=2, column=1, sticky="w")

        text_button_label = tk.Label(main_frame, text="字幕：")
        text_button_label.grid(row=3, column=0, sticky="w", pady=[10, 0])

        # 用于选择txt文件并执行操作
        text_button = tk.Button(
            main_frame, text="选择字幕TXT文件", command=self.process_text_file, width=22
        )
        text_button.grid(row=4, column=0, sticky="w", pady=10)

        check_button = tk.Checkbutton(
            main_frame, text="翻译后译文", variable=self.is_translated_subtitles
        )
        check_button.select()

        check_button.grid(row=4, column=1, sticky="w", pady=10)

        self.file_name_label = tk.Label(main_frame, text="")
        self.file_name_label.grid(row=4, column=2, sticky="w")

        translate_label = tk.Label(main_frame, text="语言类型：")
        translate_label.grid(row=5, column=0, sticky="w", pady=[10, 0])

        # 创建一个下拉菜单
        self.language_select = ttk.Combobox(
            main_frame, values=list(self.option_dict.keys())
        )
        self.language_select.grid(row=6, column=0, sticky="w", pady=10)
        # 为下拉菜单绑定事件处理程序
        self.language_select.bind("<<ComboboxSelected>>", self.on_select)

        audio_speed_label = tk.Label(main_frame, text="语音速度：")
        audio_speed_label.grid(row=5, column=1, sticky="w", padx=10, pady=[10, 0])

        # 语音速度
        self.audio_speed_input = tk.Entry(main_frame)
        self.audio_speed_input.grid(row=6, column=1, sticky="w", padx=10)
        self.audio_speed_input.insert(0, self.audio_speed)  # 设置默认值

        # 选择视频输出路径
        select_button = tk.Button(
            main_frame, text="选择视频输出路径", command=self.select_output_video_path, width=22
        )
        select_button.grid(row=7, column=0, sticky="w", pady=10)

        self.output_video_label = tk.Label(main_frame, text="")
        self.output_video_label.grid(row=7, column=1, sticky="w")

        # 执行操作
        generate_files = tk.Button(
            main_frame,
            text="生成视频",
            command=self.start_background_thread,
            width=22,
            height=2,
        )
        generate_files.grid(row=8, column=0, sticky="w", pady=10)

        # 创建Label用于显示日志
        self.log_label = tk.Label(
            main_frame, text="", height=10, width=50, anchor="nw", justify="left"
        )
        self.log_label.grid(row=9, column=0, sticky="w", columnspan=3, pady=10)

        # ---------------------------------------------------------------------------------------------------------------------------

        # 创建一个Frame来容纳窗口中的所有控件
        gather_frame = tk.Frame(self.root, padx=50, pady=20)
        gather_frame.grid(row=0, column=1, sticky="nw")  # 使用grid布局

        # 功能标题 Title
        gather_function_title = tk.Label(gather_frame, text="快速生成", font=["微软雅黑", 14])
        gather_function_title.grid(row=0, column=0, sticky="w")

        fast_translate_label = tk.Label(gather_frame, text="语言类型：")
        fast_translate_label.grid(row=1, column=0, sticky="w", pady=[10, 0])

        # 创建一个下拉菜单
        self.fast_language_select = ttk.Combobox(
            gather_frame, values=list(self.option_dict.keys())
        )
        # 为下拉菜单绑定事件处理程序
        self.fast_language_select.bind("<<ComboboxSelected>>", self.fast_select)
        self.fast_language_select.grid(row=2, column=0, sticky="w", pady=10)

        gather_label = tk.Label(gather_frame, text="选择文件：")
        gather_label.grid(row=3, column=0, sticky="w", pady=[10, 0])

        gather_select_button = tk.Button(
            gather_frame, text="选择 Datas 文件夹", command=self.select_datas_path, width=22
        )
        gather_select_button.grid(row=4, column=0, sticky="w", pady=10)

        self.datas_path_label = tk.Label(gather_frame, text="")
        self.datas_path_label.grid(row=4, column=1, sticky="w")

        cover_label = tk.Label(gather_frame, text="选择视频封面图：")
        cover_label.grid(row=5, column=0, sticky="w", pady=[10, 0])

        cover_button = tk.Button(gather_frame, text="选择图片", command=self.choose_cover, width=22)
        cover_button.grid(row=6, column=0, sticky="w", pady=10)

        self.cover_path_label = tk.Label(gather_frame, text="")
        self.cover_path_label.grid(row=6, column=1, sticky="w")

        # 快速生成
        quickly_generate = tk.Button(
            gather_frame,
            text="快速生成",
            command=self.fast_background_thread,
            width=22,
            height=2,
        )
        quickly_generate.grid(row=7, column=0, sticky="w", pady=10)

        # 创建Label用于显示日志
        self.fast_log_label = tk.Label(
            gather_frame, text="", height=1, width=20, anchor="nw", justify="left"
        )
        self.fast_log_label.grid(row=8, column=0, sticky="w", columnspan=3, pady=10)

        # ---------------------------------------------------------------------------------------------------------------------------

        compression_frame = tk.Frame(self.root, padx=50, pady=20)
        compression_frame.grid(row=0, column=2, sticky="nw")  # 使用grid布局

        # 功能标题 Title
        compression_title = tk.Label(compression_frame, text="视频压缩", font=["微软雅黑", 14])
        compression_title.grid(row=0, column=0, sticky="w")

        original_select_button = tk.Button(
            compression_frame, text="选择原视频", command=self.select_original_path, width=22
        )
        original_select_button.grid(row=1, column=0, sticky="w", pady=10)

        self.original_path_label = tk.Label(compression_frame, text="")
        self.original_path_label.grid(row=1, column=1, sticky="w")

        output_select_button = tk.Button(
            compression_frame,
            text="选择压缩后视频路径",
            command=self.select_output_path,
            width=22,
        )
        output_select_button.grid(row=2, column=0, sticky="w", pady=10)

        self.output_path_label = tk.Label(compression_frame, text="")
        self.output_path_label.grid(row=2, column=1, sticky="w")

        bitrate_label = tk.Label(compression_frame, text="输出码率：")
        bitrate_label.grid(row=3, column=0, sticky="w", pady=[10, 0])

        # 输出视频码率
        self.output_bitrate_input = tk.Entry(compression_frame)
        self.output_bitrate_input.grid(row=4, column=0, sticky="w")
        self.output_bitrate_input.insert(0, self.output_bitrate)  # 设置默认值

        # 压缩视频
        compression_button = tk.Button(
            compression_frame,
            text="压缩视频",
            command=self.zip_video_thread,
            width=22,
            height=2,
        )
        compression_button.grid(row=5, column=0, sticky="w", pady=10)

        # ----------------------------------------------- 添加视频封面 ---------------------------------------------------

        self.video_cover_image()


    # 快速生成-选择语言
    def fast_select(self, event):
        selected_text = self.fast_language_select.get()
        self.selected_language = self.option_dict[selected_text]
        self.selected_language_txt = selected_text

    # 选择图片文件夹
    def select_images(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.images_select_path = folder_path
        self.file_images_label.config(text=folder_path)

        print(folder_path)

    # 选择字幕文件
    def process_text_file(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.subtitlesTXT_path = file_path
        print(file_path)

        # 获取文件名
        file_name = file_path.split("/")[-1]  # 从文件路径中提取文件名
        # 在标签中显示文件名
        self.file_name_label.config(text=f"已选择文件: {file_name}")

    # 选择语言
    def on_select(self, event):
        selected_text = self.language_select.get()
        self.selected_language = self.option_dict[selected_text]
        self.selected_language_txt = selected_text

    # 选择输出文件夹
    def select_output_video_path(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.output_video_path = folder_path
        self.output_video_label.config(text=folder_path)

        print("选择输出文件夹", self.output_video_label)

    # 快速生成选择文件夹
    def select_datas_path(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.datas_path = folder_path
        self.datas_path_label.config(text=folder_path)

        print("选择Datas文件夹", self.datas_path)

    # 压缩视频选择原视频地址
    def select_original_path(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(filetypes=[("Video File", "*.mp4")])
        if not file_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.original_path = file_path
        print(file_path)

        # 获取文件名
        file_name = file_path.split("/")[-1]  # 从文件路径中提取文件名
        # 在标签中显示文件名
        self.original_path_label.config(text=f"已选择文件: {file_name}")

    # 压缩视频选择输出视频地址
    def select_output_path(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.zip_output_path = folder_path
        self.output_path_label.config(text=folder_path)

    def choose_cover(self):
        cover_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        self.cover_img_path = cover_path
        self.cover_path_label.config(text=cover_path)

    # ------------------------------- 生成视频封面 ----------------------------------------------------------------

    # 生成视频封面选择原视频地址
    def select_original_video_cover_path(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(filetypes=[("Video File", "*.mp4")])
        if not file_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.original_video_cover_path = file_path
        print(file_path)

        # 获取文件名
        file_name = file_path.split("/")[-1]  # 从文件路径中提取文件名
        # 在标签中显示文件名
        self.original_video_cover_path_label.config(text=f"已选择文件: {file_name}")

    # 生成视频封面选择输出视频地址
    def select_cover_output_path(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return  # 如果用户取消选择文件，不执行任何操作
        self.generate_video_cover_output_path = folder_path
        self.cover_output_path_label.config(text=folder_path)

    # 选择视频封面图片
    def choose_cover_image(self):
        cover_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        self.cover_image_path = cover_path
        self.cover_image_path_label.config(text=cover_path)

    # ------------------------------- 生成视频封面 选择框 结束 ----------------------------------------------------------------

    # 快速生成事件
    def fast_background_thread(self):
        if not self.datas_path:
            self.fast_log("请选择Datas文件夹！")
            return

        if not self.cover_img_path:
            self.fast_log("请选择视频封面图！")
            return

        # 创建后台线程来执行请求
        background_thread = threading.Thread(target=self.fast_generate)
        background_thread.start()

    # 开始执行
    def start_background_thread(self):
        if not self.images_select_path:
            self.log("请选择图片文件夹！")
            return

        if not self.subtitlesTXT_path:
            self.log("请选择字幕文件！")
            return

        if not self.selected_language:
            self.log("请选择语言类型！")
            return

        if not self.output_video_path:
            self.log("请选视频输出路径！")
            return

        # 创建后台线程来执行请求
        background_thread = threading.Thread(target=self.generate)
        background_thread.start()

    # 点击压缩视频
    def zip_video_thread(self):
        if not self.original_path:
            self.log("请选择原视频")
            return

        if not self.zip_output_path:
            self.log("请选择输出视频地址")
            return

        # 创建后台线程来执行请求
        background_thread = threading.Thread(target=self.zip_video)
        background_thread.start()

    # 点击生成视频封面
    def video_cover_thread(self):
        if not self.original_video_cover_path:
            self.log("请选择原视频")
            return

        if not self.cover_image_path:
            self.log("请选择视频封面图片")
            return

        if not self.generate_video_cover_output_path:
            self.log("请选择输出视频地址")
            return

        # 创建后台线程来执行请求
        background_thread = threading.Thread(target=self.generate_video_cover)
        background_thread.start()

    # 压缩视频
    def zip_video(self):
        bitrate = self.output_bitrate_input.get()
        print(self.original_path)
        print(self.zip_output_path)
        print(bitrate)
        VideoCompress.compress(self.original_path, self.zip_output_path, bitrate)

    # 生成带封面视频
    def generate_video_cover(self):
        print(self.original_video_cover_path)
        print(self.cover_image_path)
        print(self.generate_video_cover_output_path)
        VideoMaker.add_cover_image_to_video(self.original_video_cover_path,
                                            self.cover_image_path,
                                            self.generate_video_cover_output_path)
        log = "视频生成成功，请到 " + self.generate_video_cover_output_path + " 文件夹内查"
        self.log(log)

    def log(self, message):
        self.log_label.config(text=message)

    def fast_log(self, message):
        self.fast_log_label.config(text=message)

    # 步骤生成
    def generate(self):
        self.log("开始生成，请稍后...")
        print(self.selected_language)
        print(self.images_select_path)
        print(self.subtitlesTXT_path)
        print(self.output_video_path)
        # 创建所需文件夹
        audios_folder = (
            self.datas_path + "/outputs/" + self.selected_language + "/audios"
        )
        if not os.path.exists(audios_folder):
            os.makedirs(audios_folder)
        temps_folder = self.datas_path + "/outputs/" + self.selected_language + "/temps"
        if not os.path.exists(temps_folder):
            os.makedirs(temps_folder)

        try:
            is_translated_subtitles = self.is_translated_subtitles.get()
            if is_translated_subtitles == 0:
                # 执行翻译
                transer = Translator(
                    self.selected_language,
                    self.selected_language_txt,
                    self.subtitlesTXT_path,
                )
                transer.run()

            audio_speed = self.audio_speed_input.get()
            audioer = AudioMaker(
                self.selected_language,
                audio_speed,
                is_translated_subtitles,
                self.subtitlesTXT_path,
                self.datas_path,
            )
            audioer.run()

            videoer = VideoMaker(
                self.selected_language,
                self.images_select_path,
                self.output_video_path,
                self.datas_path,
            )
            videoer.make()
            videoer.merge()
            log = "视频生成成功，请到 " + self.output_video_path + " 文件夹内查"
            self.log(log)
            print(log)
            sendDingtalk(log)
        except Exception as e:
            print(f"发生错误: {str(e)}")
            sendDingtalk("生成视频发生错误啦！请尽快查看运行程序！")

    # 快速生成
    def fast_generate(self):
        print(self.datas_path)
        print(self.selected_language)

        # 创建所需文件夹
        audios_folder = (
            self.datas_path + "/outputs/" + self.selected_language + "/audios"
        )
        if not os.path.exists(audios_folder):
            os.makedirs(audios_folder)
        temps_folder = self.datas_path + "/outputs/" + self.selected_language + "/temps"
        if not os.path.exists(temps_folder):
            os.makedirs(temps_folder)

        subtitlesTXT_path = self.datas_path + "/subtitles.txt"

        try:
            audio_speed = self.audio_speed_input.get()
            audioer = AudioMaker(
                self.selected_language,
                audio_speed,
                1,
                subtitlesTXT_path,
                self.datas_path,
            )
            audioer.run()

            images_select_path = self.datas_path + "/images"
            output_video_path = self.datas_path + "/outputs"

            videoer = VideoMaker(
                self.selected_language,
                images_select_path,
                output_video_path,
                self.datas_path,
                self.cover_img_path
            )
            videoer.make()
            videoer.merge()

            print("视频生成成功")
            log = "视频生成成功，请到 " + output_video_path + " 文件夹内查"
            self.fast_log(log)
            sendDingtalk(log)

        except Exception as e:
            print(f"发生错误: {str(e)}")
            sendDingtalk(f"生成视频发生错误啦！请尽快查看运行程序！{str(e)}")

    def main(self):
        # 设置窗口大小
        window_width = 1200
        window_height = 650
        # 将窗口置于屏幕中央
        self.center_window(window_width, window_height)
        self.create_ui()
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIAPP(root)
    app.main()