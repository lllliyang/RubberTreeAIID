import numpy as np
import rasterio
from rasterio.windows import Window
import os
import csv
import logging
from typing import Dict
from PIL import Image


class ImageProcessor:
    """
    图像处理类：处理DOM和DSM图像的第一步 - 切割图像
    """

    def __init__(self, config: Dict):
        """
        初始化图像处理器
        @param config: 配置信息字典
        """
        self.config = config
        self.tile_size = 640  # 固定切片大小为640*640

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 创建输入输出目录
        self.create_directories()

    def create_directories(self):
        """创建必要的目录结构"""
        # 输入目录
        self.dom_input_dir = os.path.join(self.config['input_dir'], 'dom')
        self.dsm_input_dir = os.path.join(self.config['input_dir'], 'dsm')
        os.makedirs(self.dom_input_dir, exist_ok=True)
        os.makedirs(self.dsm_input_dir, exist_ok=True)

        # 输出目录
        self.dom_output_dir = os.path.join(self.config['output_dir'], 'dom_tiles')
        self.dsm_output_dir = os.path.join(self.config['output_dir'], 'dsm_tiles')
        os.makedirs(self.dom_output_dir, exist_ok=True)
        os.makedirs(self.dsm_output_dir, exist_ok=True)

    # def split_tif(self, dom_tif_path: str, output_folder: str):
    #     """
    #     将DOM TIFF文件分割为PNG小块
    #     @param dom_tif_path: DOM文件路径
    #     @param output_folder: 输出文件夹路径
    #     """
    #     with rasterio.open(dom_tif_path) as src:
    #         # 获取图像数据
    #         bands = src.count  # 图像的通道数
    #         height = src.height
    #         width = src.width
    #
    #         # 计算分块数量
    #         n_tiles_x = (width + self.tile_size - 1) // self.tile_size
    #         n_tiles_y = (height + self.tile_size - 1) // self.tile_size
    #
    #         for i in range(n_tiles_x):
    #             for j in range(n_tiles_y):
    #                 # 计算分块的范围
    #                 left = i * self.tile_size
    #                 top = j * self.tile_size
    #                 right = min(left + self.tile_size, width)
    #                 bottom = min(top + self.tile_size, height)
    #
    #                 # 计算窗口大小
    #                 window = Window(left, top, right - left, bottom - top)
    #
    #                 # 读取分块数据
    #                 tile_data = np.zeros((bands, window.height, window.width), dtype=np.uint8)
    #                 for b in range(bands):
    #                     tile_data[b, :, :] = src.read(b + 1, window=window)
    #
    #                 # 转换为RGB格式
    #                 rgb_data = np.transpose(tile_data, (1, 2, 0))
    #
    #                 # 创建640*640的空白图像
    #                 full_tile = np.zeros((self.tile_size, self.tile_size, 3), dtype=np.uint8)
    #
    #                 # 将实际数据复制到空白图像中
    #                 h, w = rgb_data.shape[:2]
    #                 full_tile[:h, :w, :] = rgb_data
    #
    #                 # 转换为PIL图像并保存为PNG
    #                 img = Image.fromarray(full_tile)
    #
    #                 # 创建分块图像的文件名
    #                 tile_filename = f'tile_{i}_{j}.png'
    #                 tile_path = os.path.join(output_folder, tile_filename)
    #
    #                 # 保存为PNG
    #                 img.save(tile_path, 'PNG')
    #
    #                 self.logger.info(f"生成PNG图像: {tile_path}")
    # def split_tif(self, dom_tif_path: str, output_folder: str):
    #     """
    #     将DOM TIFF文件分割为PNG小块
    #     @param dom_tif_path: DOM文件路径
    #     @param output_folder: 输出文件夹路径
    #     """
    #     with rasterio.open(dom_tif_path) as src:
    #         # 获取图像数据
    #         bands = src.count  # 图像的通道数
    #         height = src.height
    #         width = src.width
    #
    #         # 计算分块数量
    #         n_tiles_x = (width + self.tile_size - 1) // self.tile_size
    #         n_tiles_y = (height + self.tile_size - 1) // self.tile_size
    #
    #         for i in range(n_tiles_x):
    #             for j in range(n_tiles_y):
    #                 # 计算分块的范围
    #                 left = i * self.tile_size
    #                 top = j * self.tile_size
    #                 right = min(left + self.tile_size, width)
    #                 bottom = min(top + self.tile_size, height)
    #
    #                 # 计算窗口大小
    #                 window = Window(left, top, right - left, bottom - top)
    #
    #                 # 读取分块数据
    #                 tile_data = np.zeros((bands, window.height, window.width), dtype=np.uint8)
    #                 for b in range(bands):
    #                     tile_data[b, :, :] = src.read(b + 1, window=window)
    #
    #                 # 转换为RGB格式
    #                 rgb_data = np.transpose(tile_data, (1, 2, 0))
    #
    #                 # 检查通道数并处理
    #                 if rgb_data.shape[2] == 4:  # 如果是RGBA图像
    #                     rgb_data = rgb_data[:, :, :3]  # 只保留RGB通道
    #
    #                 # 创建640*640的空白图像
    #                 full_tile = np.zeros((self.tile_size, self.tile_size, 3), dtype=np.uint8)
    #
    #                 # 将实际数据复制到空白图像中
    #                 h, w = rgb_data.shape[:2]
    #                 full_tile[:h, :w, :] = rgb_data
    #
    #                 # 转换为PIL图像并保存为PNG
    #                 img = Image.fromarray(full_tile)
    #
    #                 # 创建分块图像的文件名
    #                 tile_filename = f'tile_{i}_{j}.png'
    #                 tile_path = os.path.join(output_folder, tile_filename)
    #
    #                 # 保存为PNG
    #                 img.save(tile_path, 'PNG')
    #
    #                 self.logger.info(f"Generate PNG: {tile_path}")
    def split_tif(self, dom_tif_path: str, output_folder: str):
        """
        将 DOM TIFF 文件切割为 640x640 的图像，边缘补黑，不丢块
        """
        with rasterio.open(dom_tif_path) as src:
            bands = src.count
            height = src.height
            width = src.width

            n_tiles_x = (width + self.tile_size - 1) // self.tile_size
            n_tiles_y = (height + self.tile_size - 1) // self.tile_size

            for i in range(n_tiles_x):
                for j in range(n_tiles_y):
                    left = i * self.tile_size
                    top = j * self.tile_size

                    # 窗口宽高最多为 tile_size，边缘可能不足
                    win_width = min(self.tile_size, width - left)
                    win_height = min(self.tile_size, height - top)

                    window = Window(left, top, win_width, win_height)

                    # 读取窗口数据
                    tile_data = np.zeros((bands, self.tile_size, self.tile_size), dtype=np.uint8)
                    for b in range(bands):
                        band_data = src.read(b + 1, window=window)

                        # 填充到完整 tile 中
                        tile_data[b, :win_height, :win_width] = band_data

                    # # 转换为 RGB 格式
                    # rgb_data = np.transpose(tile_data[:3], (1, 2, 0))  # 只取前3通道防止异常
                    # img = Image.fromarray(rgb_data)
                    bands, h, w = tile_data.shape

                    # 判断通道数并处理
                    if bands >= 3:
                        rgb_data = np.transpose(tile_data[:3], (1, 2, 0))  # RGB
                    elif bands == 1:
                        gray = tile_data[0]
                        rgb_data = np.stack([gray] * 3, axis=-1)  # 灰度转 RGB
                    else:
                        raise ValueError(f"Unsupported band count: {bands}")

                    # 构建图像
                    img = Image.fromarray(rgb_data)

                    tile_filename = f'tile_{i}_{j}.png'
                    tile_path = os.path.join(output_folder, tile_filename)
                    img.save(tile_path, 'PNG')
                    self.logger.info(f"✅ Generate tile: {tile_path} ({img.size})")

    def split_tif_and_generate_csv(self, dsm_tif_path: str, output_folder: str):
        """
        将DSM TIFF文件分割为小块并生成对应的CSV文件
        @param dsm_tif_path: DSM文件路径
        @param output_folder: 输出文件夹路径
        """
        with rasterio.open(dsm_tif_path) as src:
            # 获取数据
            dsm_data = src.read(1)  # 读取高程数据
            transform = src.transform

            width = src.width
            height = src.height

            # 计算分块数量
            n_tiles_x = (width + self.tile_size - 1) // self.tile_size
            n_tiles_y = (height + self.tile_size - 1) // self.tile_size

            for i in range(n_tiles_x):
                for j in range(n_tiles_y):
                    # 计算分块范围
                    left = i * self.tile_size
                    top = j * self.tile_size
                    right = min(left + self.tile_size, width)
                    bottom = min(top + self.tile_size, height)

                    # 提取分块数据
                    tile_data = dsm_data[top:bottom, left:right]

                    # 保存分块CSV文件
                    tile_filename = f'tile_{i}_{j}.csv'
                    tile_csv_path = os.path.join(output_folder, tile_filename)

                    with open(tile_csv_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['row', 'col', 'longitude', 'latitude', 'elevation'])

                        for row in range(tile_data.shape[0]):
                            for col in range(tile_data.shape[1]):
                                elevation = tile_data[row, col]

                                # 计算经纬度
                                x, y = transform * (left + col, top + row)

                                writer.writerow([row, col, x, y, elevation])

                    self.logger.info(f"Generate CSV: {tile_csv_path}")

    def process_first_step(self):
        """
        执行第一步处理：切割DOM为PNG，切割DSM并生成CSV
        """
        try:
            # 处理DOM图像
            for dom_file in os.listdir(self.dom_input_dir):
                if dom_file.endswith('.tif'):
                    dom_path = os.path.join(self.dom_input_dir, dom_file)
                    self.logger.info(f"Start processing DOM file: {dom_file}")
                    self.split_tif(dom_path, self.dom_output_dir)

            # 处理DSM图像
            for dsm_file in os.listdir(self.dsm_input_dir):
                if dsm_file.endswith('.tif'):
                    dsm_path = os.path.join(self.dsm_input_dir, dsm_file)
                    self.logger.info(f"Start processing DSM file: {dsm_file}")
                    self.split_tif_and_generate_csv(dsm_path, self.dsm_output_dir)

            self.logger.info("Step 1 completed: DOM and DSM image slicing finished")

        except Exception as e:
            self.logger.error(f"第一步处理出错: {str(e)}")
            raise