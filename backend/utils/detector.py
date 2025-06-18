import sys
import os

# 添加当前目录到导入路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ultralytics import YOLO  # ❌ 不要写 .ultralytics，会导致 relative import 错误
from PIL import Image
import logging
from typing import Dict

from ultralytics.nn.Addmodule import DFF
print("✅ 自定义模块导入成功！")



from PIL import Image

class RubberTreeDetector:
    """
    橡胶树检测器：使用YOLOv11对切割好的DOM图片进行检测
    """

    def __init__(self, config: Dict):
        """
        初始化检测器
        @param config: 配置信息字典
        """
        self.config = config
        self.weights_path = os.path.join(config['weights_dir'], 'best.pt')  # 使用 weights_file

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 创建输出目录
        self.detection_output_dir = os.path.join(config['output_dir'], 'detection_results')
        os.makedirs(self.detection_output_dir, exist_ok=True)

        # 加载模型
        try:
            self.model = YOLO(self.weights_path)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"加载模型失败: {str(e)}")
            raise

    def detect_tiles(self):
        """
        对所有切割好的DOM图片进行检测
        """
        dom_tiles_dir = os.path.join(self.config['output_dir'], 'dom_tiles')

        try:
            # 获取所有PNG图片
            for tile_file in os.listdir(dom_tiles_dir):
                if tile_file.endswith('.png'):
                    tile_path = os.path.join(dom_tiles_dir, tile_file)
                    self.logger.info(f"Processing image: {tile_file}")

                    # 获取基础文件名（不包含扩展名）
                    base_name = os.path.splitext(tile_file)[0]  # 例如：example_0_0

                    # 执行检测
                    results = self.model(tile_path)

                    # 保存检测结果
                    for result in results:
                        # 保存带标注的图片，保持原始文件名
                        result_path = os.path.join(self.detection_output_dir, f'det_{base_name}.png')
                        result.save(result_path)

                        # 保存检测框信息到txt文件，保持原始文件名
                        boxes = result.boxes
                        if len(boxes) > 0:
                            txt_path = os.path.join(self.detection_output_dir, f'det_{base_name}.txt')
                            with open(txt_path, 'w') as f:
                                for box in boxes:
                                    # 获取检测框信息
                                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                                    conf = box.conf[0].item()
                                    cls = box.cls[0].item()
                                    # 写入格式：类别 置信度 x1 y1 x2 y2
                                    f.write(f"{int(cls)} {conf:.4f} {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f}\n")

                    self.logger.info(f"Image processing completed: {tile_file}")

            self.logger.info("All image detection completed")

        except Exception as e:
            self.logger.error(f"检测过程出错: {str(e)}")
            raise