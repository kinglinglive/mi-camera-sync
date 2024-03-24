# mi-camera-sync
同步米家摄像头视频到阿里云对象存储OSS。

## 使用方法 Docker

``` shell
docker run -d --name mi-camera-sync \
--restart always \
-v /your-camera-data:/data \ # 你的视频所在的文件夹，挂载到容器的data目录
-e OSS_ACCESS_KEY_ID=your-access-key \ # OSS账户
-e OSS_ACCESS_KEY_SECRET=your-access-secret \ # OSS密钥
-e OSS_ENDPOINT=https://oss-cn-beijing.aliyuncs.com \ # 存储桶所在位置域名
-e OSS_BUCKET_NAME=your-bucket-name \ # 存储桶名称
-e OSS_PREFIX=your-file-prefix \ # 合并的文件名前缀。例如 camera/01
-e EXEC_HOURS=13 \ # 每天几点执行。可多配置 13,14,15
kinglinglive/mi-camera-sync
```

