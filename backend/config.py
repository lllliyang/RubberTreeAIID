import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置信息
CONFIG = {
    'input_dir': os.path.join(BASE_DIR, 'input'),
    'output_dir': os.path.join(BASE_DIR, 'output'),
    'weights_dir': os.path.join(BASE_DIR, 'models/weights'),  # 修改为你的权重文件路径
    'tile_size': 640,
    'weight_file': 'best.pt',  # 修改为你的权重文件名

    # 数据库配置
    'database': {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': '橡胶树信息'
    }
}