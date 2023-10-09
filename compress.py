from moviepy.editor import VideoFileClip


class VideoCompress:

    # original_video_path 原视频路径
    # compressed_video_path 压缩后的使用路径
    # target_bitrate 压缩比特率(码率)
    @staticmethod
    def compress(original_video_path, compressed_video_path, target_bitrate='1000'):
        video_clip = VideoFileClip(original_video_path)
        # 压缩视频并保存
        compressed_clip = video_clip.resize(height=1080)  # 调整视频分辨率
        compressed_clip.write_videofile(compressed_video_path+'/compressed_video.mp4', bitrate=target_bitrate + 'k')

        # 关闭视频文件
        video_clip.close()
