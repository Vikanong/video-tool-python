import re
import os
from gtts import gTTS

class AudioMaker:
    def __init__(self, lang, audio_speed, is_translated_subtitles, subtitlesTXT_path, datas_path):
        self.lines = ""
        self.language = lang
        self.audio_speed = float(audio_speed)
        self.is_translated_subtitles = is_translated_subtitles
        self.subtitlesTXT_path = subtitlesTXT_path
        self.datas_path = datas_path

    def extract_line_id(self, line):
        # 从给定的行中提取行ID
        match = re.search(r"--(\d+):", line)
        if match:
            return int(match.group(1))
        else:
            print("未找到匹配的数字")
            return 0

    def extract_text(self, line):
        # 从给定的行中提取文本
        return line[line.index(":") + 2 :]

    def process_audio_segment(self, audio_tmp, cur_line_audio, last_time_ms):
        # 处理音频段并更新时间
        duration_ms = len(cur_line_audio)
        start_time = last_time_ms
        end_time = start_time + duration_ms
        last_time_ms = end_time

        delay = 0
        return audio_tmp + cur_line_audio, last_time_ms

    def append_subtitle(self, subtitle_text, index, last_time_ms, line):
        # 添加字幕文本
        delay = 0
        subtitle_text += f"{index}\n"
        subtitle_text += "{:02d}:{:02d}:{:02d},{:03d} --> {:02d}:{:02d}:{:02d},{:03d}\n".format(
            last_time_ms // 3600000,
            (last_time_ms // 60000) % 60,
            (last_time_ms // 1000) % 60,
            last_time_ms % 1000,
            (last_time_ms - delay) // 3600000,
            ((last_time_ms - delay) // 60000) % 60,
            ((last_time_ms - delay) // 1000) % 60,
            last_time_ms % 1000,
        )
        subtitle_text += line[line.index(":") + 2 :] + "\n\n"
        return subtitle_text

    def save_and_clear_audio(self, audio_tmp, pre_line_id, audios_folder):
        # 保存音频并清空音频段
        audio_len = len(audio_tmp)
        silence_len = 100 - audio_len % 100
        silence_audio = AudioSegment.silent(duration=silence_len)
        audio_tmp += silence_audio

        mp3_path = os.path.join(audios_folder, f"{pre_line_id}.mp3")
        audio_tmp.export(mp3_path, format="mp3")

    def finalize_audio_and_subtitles(self, audio_all, audios_folder, subtitle_text, output_dir):
        # 完成音频和字幕生成
        mp3_file_path = os.path.join(output_dir, "audio.mp3")
        audio_all.export(mp3_file_path, format="mp3")

        srt_file_path = os.path.join(output_dir, "subtitles.srt")
        with open(srt_file_path, "w", encoding="utf-8") as subtitle_file:
            subtitle_file.write(subtitle_text)
        
        print("已生成语音文件和字幕文件!")

    def speed_change(self, path, speed):
        sound = AudioSegment.from_mp3(path)
        if float(1) == float(speed):
            return sound
        # 手动覆盖frame_rate。这个告诉电脑多少每秒播放的样本数
        sound_with_altered_frame_rate = sound._spawn(
            sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)}
        )
        # 将改变帧速率的声音转换为标准帧速率
        # 以便正常播放程序。他们通常只是 知道如何以标准帧速率播放音频（如44.1k）
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    def run(self):
        self.open_file()
        self.generate()

    def open_file(self):
        print(self.is_translated_subtitles)
        print(self.subtitlesTXT_path)
        file_path = ""

        if self.is_translated_subtitles == 1:
            file_path = self.subtitlesTXT_path
        else:
            file_path = os.path.join(self.datas_path, "outputs", self.language, "subtitles.txt")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as text_file:
                    lines = text_file.readlines()
                    self.lines = [line for line in lines if line.strip() != ""]
            except Exception as e:
                print(f"发生错误: {str(e)}")

    def generate(self):
        print("开始生成，请稍后...")
        
        output_dir = os.path.join(self.datas_path, "outputs", self.language)
        temp_folder = os.path.join(output_dir, "temps")
        audios_folder = os.path.join(output_dir, "audios")
        
        audio_all = AudioSegment.empty()
        audio_tmp = AudioSegment.empty()
        subtitle_text = ""
        
        last_time_ms = 0
        pre_line_id = 1
        cur_line_id = 0
        
        for index, line in enumerate(self.lines, start=1):
            if line.startswith("--"):
                cur_line_id = self.extract_line_id(line)

                # 将每条字幕文本转换为语音
                tts = gTTS(text=self.extract_text(line), lang=self.language)
                print("生成第" + str(index) + "条语音成功！")
                
                temp_file_path = os.path.join(temp_folder, f"temp_{index}.mp3")
                tts.save(temp_file_path)
                
                audio_temp = self.speed_change(temp_file_path, self.audio_speed)
                mp3_path = os.path.join(temp_folder, f"{index}.mp3")
                audio_temp.export(mp3_path, format="mp3")
                
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                cur_line_audio = AudioSegment.from_mp3(mp3_path)
                audio_tmp, last_time_ms = self.process_audio_segment(audio_tmp, cur_line_audio, last_time_ms)
                
                if pre_line_id != cur_line_id:
                    self.save_and_clear_audio(audio_tmp, pre_line_id, audios_folder)
                    audio_all += audio_tmp
                    audio_tmp = AudioSegment.empty()
                
                subtitle_text = self.append_subtitle(subtitle_text, index, last_time_ms, line)
                pre_line_id = cur_line_id
            
            if index == len(self.lines):
                audio_len = len(audio_tmp)
                silence_len = 100 - audio_len % 100
                silence_audio = AudioSegment.silent(duration=silence_len)
                audio_tmp += silence_audio
                mp3_path = os.path.join(audios_folder, f"{cur_line_id}.mp3")
                audio_tmp.export(mp3_path, format="mp3")
                
                self.save_and_clear_audio(audio_tmp, pre_line_id, audios_folder)
                audio_all += audio_tmp
                audio_tmp = AudioSegment.empty()
        
        print("生成完成正在合成语音")
        
        self.finalize_audio_and_subtitles(audio_all, audios_folder, subtitle_text, output_dir)
