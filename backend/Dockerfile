FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖 (利用缓存机制，先拷 requirements)
COPY requirements.txt .
# 换源加速下载 (可选)
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制所有代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令 (生产环境建议用 gunicorn，毕设用 python run.py 也行)
# 注意：run.py 里 app.run(host='0.0.0.0') 必须由 127.0.0.1 改为 0.0.0.0
CMD ["python", "run.py"]