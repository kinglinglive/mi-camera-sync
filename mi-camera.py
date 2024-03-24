import os
import subprocess
import imageio_ffmpeg as ffmpeg
import oss2
import time

# 获取阿里云 OSS 密钥的环境变量
access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
oss_endpoint = os.environ.get('OSS_ENDPOINT')
bucket_name = os.environ.get('OSS_BUCKET_NAME')
oss_prefix = os.environ.get('OSS_PREFIX')
exec_hours = os.environ.get('EXEC_HOURS')

print(f"access_key_id: {access_key_id}")
print(f"access_key_secret: {access_key_secret}")
print(f"oss_endpoint: {oss_endpoint}")
print(f"bucket_name: {bucket_name}")
print(f"oss_prefix: {oss_prefix}")
print(f"exec_hours: {exec_hours}")

# 检查环境变量是否存在
if access_key_id is None or access_key_secret is None or oss_endpoint is None or bucket_name is None or oss_prefix is None or exec_hours is None:
    print("Please set the environment variables.")
    exit()

oss_auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(oss_auth, oss_endpoint, bucket_name)


# 封装一个方法用来上传文件到阿里云oss
def upload_to_oss(file_path, oss_path):
    oss_name=f"{oss_prefix}/{oss_path}.mp4"
    # 检查oss中是否已存在同名文件
    if bucket.object_exists(oss_name):
        print(f"File {oss_name} already exists in OSS.")
        return

    bucket.put_object_from_file(oss_name, file_path)
    print(f"Uploaded {file_path} to {oss_path}")

# 定义你的视频文件夹路径
folder_path = "/data"

# 将下边内容封装为方法
def sync_video():
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print("The folder does not exist.")
        exit()

    # 存储每天需要合并的视频文件夹
    daily_folders = {}

    # 获取文件夹中的所有子文件夹，并按照文件夹名称进行排序，正序
    sub_folders = sorted([folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))])

    # 如果文件夹中没有子文件夹，则退出程序
    if len(sub_folders) == 0:
        print("There are no subfolders in the folder.")
        exit()

    # 循环这些文件夹，按天分组
    for sub_folder in sub_folders:
        # 提取文件夹的日期部分
        folder_date = sub_folder[:8]
        # 将文件夹添加到对应日期的列表中
        if folder_date not in daily_folders:
            daily_folders[folder_date] = []
        daily_folders[folder_date].append(sub_folder)

    # 循环每天的文件夹
    for date in daily_folders:
        print(f"Processing date {date}...")

        # 如果data小于last_folder.txt中的文件夹，跳过
        if os.path.exists("last_folder.txt"):
            with open("last_folder.txt", "r") as file:
                last_folder = file.read().strip()
                if date <= last_folder:
                    print(f"Skipped date {date}")
                    continue

        # 如果是倒数第一项，continue
        if date == list(daily_folders.keys())[-1]:
            print(f"Skipped date {date}")
            continue

        # 获取每天的文件夹列表
        date_folders = daily_folders[date]

        # 检查oss中是否已存在同名文件
        file_name= f"{oss_prefix}/{date}.mp4"
        if bucket.object_exists(file_name):
            print(f"File {file_name} already exists in OSS.")
            continue

        # 如果只有一个文件夹，并且文件夹只有一个文件，直接上传
        if len(date_folders) == 1:
            clip_list = sorted([file for file in os.listdir(os.path.join(folder_path, date_folders[0])) if file.endswith(".MP4") or file.endswith(".mp4")])
            if len(clip_list) == 1:
                upload_to_oss(os.path.join(folder_path, date_folders[0], clip_list[0]), date)
                continue

        # check filelist.txt file
        if os.path.exists("filelist.txt"):
            os.remove("filelist.txt")

        if os.path.exists(f"{date}.mp4"):
            os.remove(f"{date}.mp4")

        # 创建一个文件列表，其中包含所有要合并的视频文件的路径
        with open("filelist.txt", "w") as file:
            for folder in date_folders:
                clip_list = sorted([file for file in os.listdir(os.path.join(folder_path, folder)) if file.endswith(".MP4") or file.endswith(".mp4")])
                for clip in clip_list:
                    file.write(f"file '{os.path.join(folder_path, folder, clip)}'\n")

        # 获取FFmpeg的路径
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()

        # 创建并运行FFmpeg命令
        command = f"{ffmpeg_path} -stats -progress pipe:1 -f concat -safe 0 -i filelist.txt -c:v copy -c:a aac {date}.mp4"
        
        subprocess.run(command, shell=True)

        # 上传合并后的视频文件到阿里云oss，文件名为当前文件夹的名称
        upload_to_oss(f"{date}.mp4", date)

        # 删除文件列表和合并后的视频文件
        os.remove("filelist.txt")
        os.remove(f"{date}.mp4")

    # 保存进度，保存最后一天的名称到last_folder.txt
    if len(daily_folders) > 0:
        # 存在删除
        if os.path.exists("last_folder.txt"):
            os.remove("last_folder.txt")
        with open("last_folder.txt", "w") as file:
            file.write(list(daily_folders.keys())[-2])
            print(f"Saved last folder {list(daily_folders.keys())[-1]}")
        print("All done.")

# 如果是脚本运行
if __name__ == "__main__":
    # 循环，每2分钟执行一次
    while True:
        # 获取当前时间的小时24小时制，判断是否在指定的小时范围内
        current_hour = time.strftime("%H")
        if current_hour in exec_hours.split(","):
            sync_video()
        time.sleep(120)