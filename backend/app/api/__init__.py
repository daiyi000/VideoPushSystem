from flask import Blueprint

# 创建蓝图对象
video_bp = Blueprint('video', __name__)

from . import video