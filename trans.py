import requests
import os


class Translator:
    def __init__(self, lang, lang_name, subtitles_path):
        self.language = lang
        self.requests_url = ""  # 请求的接口地址
        self.translate_text = ""  # 翻译的文本
        self.selected_language = lang_name
        self.subtitles_path = subtitles_path

    def run(self):
        self.read_file()
        self.translate()

    def read_file(self):
        file_path = self.subtitles_path
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        file_content = file.read()

                        # 将换行符 \n 替换为其他特殊符号
                        replacement_symbol = "===="
                        modified_content = file_content.replace(
                            "\n", replacement_symbol + "\n"
                        )
                        self.translate_text = modified_content

                    except UnicodeDecodeError as e:
                        # 处理异常字符
                        print(f"遇到异常字符: {e}")

            except Exception as e:
                print(f"发生错误: {str(e)}")

    def translate(self):
        headers = {
            "Content-Type": "application/json",
        }
        param = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "system",
                    "content": "Each sentence starts with --*: this symbol, where * is a number representing the identifier for each of my texts. Each text can only be translated individually to ensure that the final translation corresponds to the original text with the same number. Following the format mentioned above, provide the corresponding translations for each text one by one, ensuring that each text has a clear translation. Do not combine multiple original texts into a single request to ensure that each text can be identified and translated separately. Make sure that each unique identifier has at least one corresponding translation result. Also, refrain from using statements like 'The text has been translated into English' or 'I have translated the text into English as you requested,' and avoid using prompts like 'Please note...' Remember, you only need to provide me with the translated results.",
                },
                {
                    "role": "user",
                    "content": "Translate from cn to " + self.language,
                },
                {"role": "user", "content": self.translate_text},
            ],
        }

        # 发送翻译请求
        response = requests.post(url=self.requests_url, headers=headers, json=param)
        result = response.json()
        # 解析返回结果
        content = result["choices"][0]["message"]["content"]

        # 保存为txt文件
        self.save_txt(content)

    def save_txt(self, content):
        # 以符号间隔生成数组
        text_array = content.split("====")
        array = [line for line in text_array if line.strip() != ""]
        formatted_text = "\n".join(array)  # 将列表中的部分用 "\n" 符号进行连接，以实现换行操作

        # 删除已存在的文件
        output_dir = "./Datas/outputs/" + self.language
        subtitles_file_path = os.path.join(output_dir, "subtitles.txt")
        if os.path.exists(subtitles_file_path):
            os.remove(subtitles_file_path)

        # 将格式化后的文本写入文件
        with open(subtitles_file_path, "w", encoding="utf-8") as file:
            file.write(formatted_text)

        print("翻译完成，文件已保存至 " + subtitles_file_path)
