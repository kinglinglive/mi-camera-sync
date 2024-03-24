# mi-camera-sync
同步米家摄像头视频到阿里云对象存储OSS。

## 使用方法 Docker

``` shell
docker run -d --name mi-camera-sync \
--restart always \
-v /your-camera-data:/data \
-e OSS_ACCESS_KEY_ID=your-access-key \
-e OSS_ACCESS_KEY_SECRET=your-access-secret \
-e OSS_ENDPOINT=https://oss-cn-beijing.aliyuncs.com \
-e OSS_BUCKET_NAME=your-bucket-name \
-e OSS_PREFIX=your-file-prefix \
-e EXEC_HOURS=13 \
kinglinglive/mi-camera-sync
```

