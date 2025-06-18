# backend/utils/coordinate_processor.py

import pandas as pd
import os
from pyproj import Transformer
import logging
from typing import Dict


class CoordinateProcessor:
    """
    坐标处理器：处理检测框的中心点坐标
    """

    def __init__(self, config: Dict):
        """
        初始化坐标处理器
        @param config: 配置信息字典
        """
        self.config = config
        self.image_width = 640
        self.image_height = 640

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 初始化坐标转换器
        self.transformer = Transformer.from_crs("EPSG:32649", "EPSG:4326", always_xy=True)

        # 创建输出目录
        self.coordinate_output_dir = os.path.join(config['output_dir'], 'coordinates')
        os.makedirs(self.coordinate_output_dir, exist_ok=True)

    def process_detection_results(self):
        """
        处理YOLO检测结果，只输出经度、纬度和高程信息
        """
        detection_dir = os.path.join(self.config['output_dir'], 'detection_results')
        dsm_dir = os.path.join(self.config['output_dir'], 'dsm_tiles')

        # 获取所有检测结果文件
        det_files = [f for f in os.listdir(detection_dir) if f.endswith('.txt')]

        for det_file in det_files:
            try:
                # 从检测结果中提取基础名称
                base_name = det_file.replace('det_', '').replace('.txt', '')  # 获取基础名称，例如 11_9
                csv_file = f'{base_name}.csv'  # 生成与检测文件一致的CSV文件名
                csv_path = os.path.join(dsm_dir, csv_file)

                if not os.path.exists(csv_path):
                    self.logger.warning(f"未找到对应的CSV文件: {csv_file}，跳过该检测文件: {det_file}")
                    continue

                # 读取检测结果 (格式: 类别 置信度 x1 y1 x2 y2)
                det_path = os.path.join(detection_dir, det_file)
                with open(det_path, 'r') as f:
                    detections = [line.strip().split() for line in f]

                if not detections:
                    self.logger.warning(f"检测文件为空: {det_file}")
                    continue

                # 读取并处理CSV文件
                df = pd.read_csv(csv_path)
                df.columns = [col.strip().lower() for col in df.columns]

                # 归一化row和col列
                df['row_normalized'] = df['row'] / self.image_height
                df['col_normalized'] = df['col'] / self.image_width

                # 处理每个检测框
                coordinates = []
                for det in detections:
                    # 解析检测结果
                    cls_id, conf, x1, y1, x2, y2 = det  # 解析六列数据

                    # 计算中心点坐标
                    x_center = (float(x1) + float(x2)) / 2
                    y_center = (float(y1) + float(y2)) / 2

                    # 归一化中心点坐标
                    x_center_normalized = round(x_center / self.image_width, 6)
                    y_center_normalized = round(y_center / self.image_height, 6)

                    # 匹配坐标
                    tolerance = 1e-3
                    data_point = df[
                        (abs(df['row_normalized'] - y_center_normalized) < tolerance) &
                        (abs(df['col_normalized'] - x_center_normalized) < tolerance)
                    ]

                    if not data_point.empty:
                        # 获取经纬度和高程
                        longitude = data_point['longitude'].values[0]
                        latitude = data_point['latitude'].values[0]
                        elevation = data_point['elevation'].values[0]

                        # 转换坐标系
                        lon, lat = self.transformer.transform(longitude, latitude)

                        # 只保存经度、纬度和高程信息
                        coordinates.append([lon, lat, elevation])

                # 保存结果
                if coordinates:
                    output_file = os.path.join(self.coordinate_output_dir, f'coord_{base_name}.txt')
                    with open(output_file, 'w') as f:
                        for coord in coordinates:
                            # 只写入经度、纬度、高程
                            f.write(f"{coord[0]} {coord[1]} {coord[2]}\n")
                    self.logger.info(f'Coordinates results have been saved to: {output_file}')
                else:
                    self.logger.warning(f'文件 {det_file} 没有找到任何有效的坐标信息')

            except Exception as e:
                self.logger.error(f"处理文件 {det_file} 时出错: {str(e)}")

        self.logger.info("Coordinate processing for all detection results is completed")