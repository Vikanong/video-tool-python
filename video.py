import os
import cv2
import numpy as np
from pydub import AudioSegment
import subprocess


def calc_resize(seconds, fps, action, fwidth, fheight, width, height):
    if action == "下" or action == "上":
        target_width = fwidth
        target_height = int((height / width) * target_width)
        if fheight + (seconds * fps - 1) * 2 < target_height:
            mpx = 2
        else:
            mpx = int((target_height - fheight) / (seconds * fps - 1))
    elif action == "右" or action == "左":
        target_width = fwidth + (seconds * fps - 1) * 2
        target_height = int((height / width) * target_width)
        mpx = 2
    elif action == "大":
        target_width = fwidth
        target_height = int((height / width) * target_width)
        mpx = 2
    elif action == "小":
        target_width = fwidth + (seconds * fps - 1) * 2
        target_height = int((height / width) * target_width)
        mpx = 2
    else:
        target_width = 0
        target_height = 0
        mpx = 0
    return target_width, target_height, mpx


def extract_number(file_name):
    parts = file_name.split('-')
    try:
        number = int(parts[0])
        return number
    except ValueError:
        pass
    return float('inf')


class VideoMaker:
    def __init__(self, lang, images_path, output_path, datas_path, video_cover):
        self.language = lang
        self.images_path = images_path
        self.output_video_path = output_path
        self.datas_path = datas_path
        self.video_cover = video_cover

    # 添加视频封面
    @staticmethod
    def add_cover_image_to_video(input_video_path, cover_image, output_video_path):
        # 构建FFmpeg命令
        command = [
            'ffmpeg',
            '-i', input_video_path,
            '-i', cover_image,
            '-map', '0',
            '-map', '1',
            '-c', 'copy',
            '-disposition:v:1', 'attached_pic',
            os.path.join(output_video_path, "video_audio_subtitles_cover.mp4")
        ]

        # 执行命令
        try:
            subprocess.run(command, check=True)
            print("添加视频封面成功")
        except subprocess.CalledProcessError as e:
            print("添加视频封面失败:", e)

    def make(self):
        fwidth, fheight = 1920, 1080
        fps = 30
        image_dir = self.images_path
        video_dir = os.path.join(self.datas_path, "outputs", self.language)
        audio_dir = os.path.join(self.datas_path, "outputs", self.language, "audios")

        # 创建一个VideoWriter对象来保存视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_file_path = os.path.join(video_dir, "video.mp4")
        
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
        out = cv2.VideoWriter(video_file_path, fourcc, fps, (fwidth, fheight))

        cover_image = cv2.imread(self.video_cover)
        cover_image = cv2.resize(cover_image, (fwidth, fheight))
        out.write(cover_image)

        file_list = os.listdir(image_dir)
        sorted_file_list = sorted(file_list, key=extract_number)

        for file_name in sorted_file_list:
            base_name, _ = os.path.splitext(file_name)
            parts = base_name.split("-")
            idx = parts[0]
            action = parts[1]

            mp3_file_path = os.path.join(audio_dir, f"{int(idx)}.mp3")
            mp3 = AudioSegment.from_mp3(mp3_file_path)
            duration_ms = len(mp3)
            seconds = int(duration_ms / 100) / 10

            image_file_path = os.path.join(image_dir, file_name)
            original_image = cv2.imdecode(np.fromfile(image_file_path, dtype=np.uint8), -1)
            height, width, _ = original_image.shape

            target_width, target_height, mpx = calc_resize(seconds, fps, action, fwidth, fheight, width, height)
            target_width = int(target_width)
            target_height = int(target_height)
            image, mpx = resize_image(original_image, action, fwidth, fheight, width, height, mpx)

            num_frames = int(fps * seconds)
            for frame_num in range(num_frames):
                frame = np.zeros((fheight, fwidth, 3), dtype=np.uint8)
                if action == "下":
                    y1 = (num_frames - 1) * mpx - frame_num * mpx
                    y2 = y1 + fheight
                    x1 = 0
                    x2 = fwidth
                elif action == "上":
                    y1 = target_height - fheight - (num_frames - 1) * mpx + frame_num * mpx
                    y2 = y1 + fheight
                    x1 = 0
                    x2 = fwidth
                elif action == "右":
                    y1 = target_height - fheight - 1
                    y2 = y1 + fheight
                    x1 = target_width - fwidth - frame_num * mpx
                    x2 = x1 + fwidth
                elif action == "左":
                    y1 = target_height - fheight - 1
                    y2 = y1 + fheight
                    x1 = frame_num * mpx
                    x2 = x1 + fwidth
                elif action == "大":
                    x10 = 0 + int(frame_num * mpx / 2)
                    x20 = int(width - frame_num * mpx / 2)
                    temp_h = int((x20 - x10) * fheight / fwidth)
                    y10 = int(height / 2) - int(temp_h / 2)
                    y20 = int(height / 2) + int(temp_h / 2)
                    image = cv2.resize(original_image[y10:y20, x10:x20, :], (fwidth, fheight),
                                       interpolation=cv2.INTER_LINEAR)
                    y1 = 0
                    y2 = fheight
                    x1 = 0
                    x2 = fwidth
                elif action == "小":
                    x10 = int(num_frames - frame_num * mpx / 2)
                    x20 = width - x10
                    temp_h = int((x20 - x10) * fheight / fwidth)
                    y10 = int(height / 2) - int(temp_h / 2)
                    y20 = int(height / 2) + int(temp_h / 2)
                    image = cv2.resize(original_image[y10:y20, x10:x20, :], (fwidth, fheight),
                                       interpolation=cv2.INTER_LINEAR)
                    y1 = 0
                    y2 = fheight
                    x1 = 0
                    x2 = fwidth
                else:
                    y1 = 0
                    y2 = y1 + fheight
                    x1 = fwidth
                    x2 = x1

                frame = image[y1:y2, x1:x2, 0:3]
                out.write(frame)
                # 写入帧
        out.release()

    def merge(self):
        output_path = os.path.join(self.datas_path, "outputs", self.language)
        video_clip = VideoFileClip(os.path.join(output_path, "video.mp4"))
        audio_clip = AudioSegment.from_mp3(os.path.join(output_path, "audio.mp3"))
        video_clip = video_clip.set_audio(audio_clip)

        video_audio_path = os.path.join(output_path, "video_audio.mp4")
        if os.path.exists(video_audio_path):
            os.remove(video_audio_path)
        video_clip.write_videofile(video_audio_path, codec="libx264", audio_codec="aac")

        subtitles_file_path = os.path.join(output_path, "subtitles.srt")
        
        output_video_path = os.path.join(self.output_video_path, self.language)
        if not os.path.exists(output_video_path):
            os.makedirs(output_video_path)

        video_subtitles_path = os.path.join(output_video_path, "video_audio_subtitles.mp4")
        if os.path.exists(video_subtitles_path):
            os.remove(video_subtitles_path)

        subtitles = f"'{subtitles_file_path}'"

        subprocess.run(
            [
                'ffmpeg',
                '-i', video_audio_path,
                '-vf', f'subtitles={subtitles}',
                video_subtitles_path
            ],
            check=True
        )

        if self.video_cover:
            VideoMaker.add_cover_image_to_video(video_subtitles_path, self.video_cover, output_video_path)