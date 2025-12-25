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

# 启动命令 (使用 Gunicorn 替代 Flask dev server)
# -w 4: 4个worker进程
# -b 0.0.0.0:5000: 绑定所有IP的5000端口
# --timeout 300: 超时时间设为300秒 (5分钟)，防止大文件上传/合并时超时
# run:app : 加载 run.py 中的 app 对象
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "run:app"]