# backend/utils/dsm_to_dom_with_matching.py

import os
import logging
import pandas as pd
import rasterio
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List

class DsmToDomWithMatching:
    """
    从DSM图像提取经纬度和高程信息，并与识别坐标进行匹配，最后在DOM图像上进行标注
    """

    def __init__(self, config: Dict):
        """
        初始化
        @param config: 配置信息字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # 创建输出目录
        self.coordinate_output_dir = os.path.join(config['output_dir'], 'dsm_coordinates')
        os.makedirs(self.coordinate_output_dir, exist_ok=True)

        self.annotated_output_dir = os.path.join(config['output_dir'], 'annotated_dom')
        os.makedirs(self.annotated_output_dir, exist_ok=True)

        self.logger.info("初始化完成，输出目录已创建。")

    def extract_coordinates_from_dsm(self, dsm_path: str):
        """
        从DSM图像中提取经纬度和高程信息并保存为CSV文件
        @param dsm_path: DSM图像路径
        """
        self.logger.info(f"开始从DSM图像提取坐标: {dsm_path}")
        coordinates = []
        with rasterio.open(dsm_path) as src:
            transform = src.transform
            width = src.width
            height = src.height
            self.logger.info(f"图像宽度: {width}, 高度: {height}")

            for y in range(height):
                for x in range(width):
                    # 计算经纬度
                    lon, lat = transform * (x, y)
                    elevation = src.read(1)[y, x]  # 假设高程数据在第一波段
                    coordinates.append({'row': y, 'col': x, 'longitude': lon, 'latitude': lat, 'elevation': elevation})

        # 保存为CSV文件
        output_file = os.path.join(self.coordinate_output_dir, 'a.csv')
        df = pd.DataFrame(coordinates)
        df.to_csv(output_file, index=False)

        self.logger.info(f'坐标结果已保存到: {output_file}')
        return coordinates

    def load_txt_coordinates(self, txt_dir: str) -> List[Dict]:
        """
        从TXT文件中加载经纬度信息
        @param txt_dir: TXT文件目录
        @return: 匹配的坐标列表
        """
        self.logger.info(f"开始加载TXT文件中的坐标: {txt_dir}")
        matched_coords = []
        for txt_file in os.listdir(txt_dir):
            if txt_file.endswith('.txt'):
                self.logger.info(f"处理文件: {txt_file}")
                with open(os.path.join(txt_dir, txt_file), 'r') as f:
                    for line in f:
                        lon, lat, _ = map(float, line.split())
                        matched_coords.append({'longitude': lon, 'latitude': lat})
        self.logger.info(f"加载到的坐标数量: {len(matched_coords)}")
        return matched_coords

    def annotate_dom_with_coordinates(self, dom_path: str, matched_coords: List[Dict], a_coords: pd.DataFrame):
        """
        在DOM图像上标注匹配的经纬度
        @param dom_path: DOM图像路径
        @param matched_coords: 匹配的坐标列表
        @param a_coords: 从a.csv加载的坐标数据
        """
        self.logger.info(f"开始在DOM图像上标注坐标: {dom_path}")
        with Image.open(dom_path) as img:
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()  # 使用默认字体

            for match in matched_coords:
                # 查找匹配的经纬度
                matched_row = a_coords[(a_coords['longitude'] == match['longitude']) & (a_coords['latitude'] == match['latitude'])]
                if not matched_row.empty:
                    pixel_x = matched_row['col'].values[0]
                    pixel_y = matched_row['row'].values[0]

                    # 在图像上标注经纬度
                    draw.text((pixel_x, pixel_y), f"({match['longitude']:.2f}, {match['latitude']:.2f})", fill="red", font=font)

            # 保存标注后的图像
            output_path = os.path.join(self.annotated_output_dir, os.path.splitext(os.path.basename(dom_path))[0] + '_annotated.png')
            img.save(output_path, 'PNG')
            self.logger.info(f'标注后的DOM图像已保存到: {output_path}')

    def process_images(self, dsm_path: str, txt_dir: str, dom_path: str):
        """
        处理DSM图像、TXT文件和DOM图像
        @param dsm_path: DSM图像路径
        @param txt_dir: TXT文件目录
        @param dom_path: DOM图像路径
        """
        try:
            self.logger.info("开始处理图像...")
            # 提取经纬度并保存为CSV
            a_coords = self.extract_coordinates_from_dsm(dsm_path)

            # 加载TXT文件中的经纬度
            matched_coords = self.load_txt_coordinates(txt_dir)

            # 将匹配的坐标标注到DOM图像上
            self.annotate_dom_with_coordinates(dom_path, matched_coords, pd.DataFrame(a_coords))

            self.logger.info("所有图像处理完成")

        except Exception as e:
            self.logger.error(f"处理图像时出错: {str(e)}")