FROM python:3.9.19-slim-bullseye

WORKDIR /app

COPY . .

# 设置时区为Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

ENTRYPOINT ["python", "-u", "/app/mi-camera.py"]