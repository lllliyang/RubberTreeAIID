import mysql.connector
import os
import logging
from typing import Dict


class DatabaseProcessor:
    """
    数据库处理器：将树木数据保存到MySQL数据库
    """

    def __init__(self, config: Dict):
        """
        初始化数据库处理器
        @param config: 配置信息字典
        """
        self.config = config
        self.db_config = config['database']

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect_to_db(self):
        """建立数据库连接"""
        try:
            connection = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            return connection
        except mysql.connector.Error as err:
            self.logger.error(f"数据库连接失败: {str(err)}")
            raise

    def create_table(self):
        """创建数据表"""
        connection = self.connect_to_db()
        cursor = connection.cursor()

        try:
            # 创建表（如果不存在）
            create_table_query = """
            CREATE TABLE IF NOT EXISTS tree_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                longitude DOUBLE NOT NULL,
                latitude DOUBLE NOT NULL,
                elevation DOUBLE NOT NULL,
                image_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tree_id VARCHAR(255) NOT NULL,
                yield FLOAT,
                tree_height FLOAT,
                branch_height FLOAT,
                crown_diameter FLOAT,
                cross_section_area FLOAT,
                crown_area FLOAT,
                crown_volume FLOAT,
                biomass FLOAT
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            self.logger.info("数据表创建成功或已存在")

        except mysql.connector.Error as err:
            self.logger.error(f"创建表失败: {str(err)}")
            raise
        finally:
            cursor.close()
            connection.close()

    def save_coordinates(self):
        """将坐标结果保存到数据库"""
        coordinates_dir = os.path.join(self.config['output_dir'], 'coordinates')

        # 建立数据库连接
        connection = self.connect_to_db()
        cursor = connection.cursor()

        try:
            # 获取所有坐标文件
            coord_files = [f for f in os.listdir(coordinates_dir) if f.endswith('.txt')]

            for coord_file in coord_files:
                self.logger.info(f"Processing coordinate file: {coord_file}")
                file_path = os.path.join(coordinates_dir, coord_file)

                # 读取坐标文件
                with open(file_path, 'r') as f:
                    coordinates = [line.strip().split() for line in f if line.strip()]  # 过滤空行

                # 准备插入语句
                insert_query = """
                INSERT INTO tree_data (longitude, latitude, elevation, image_name, tree_id) 
                VALUES (%s, %s, %s, %s, %s)
                """

                # 批量插入数据
                for index, coord in enumerate(coordinates):
                    if len(coord) < 3:  # 确保有足够的数据
                        self.logger.warning(f"跳过无效坐标行: {coord}")
                        continue

                    try:
                        lon, lat, elev = map(float, coord[:3])  # 取经度、纬度和高程
                        image_name = os.path.splitext(coord_file.replace('coord_', ''))[0]
                        tree_id = f"tree_{index + 1}"  # 生成一个示例 tree_id，您可以根据需要修改

                        data = (lon, lat, elev, image_name, tree_id)
                        cursor.execute(insert_query, data)
                    except ValueError as ve:
                        self.logger.warning(f"无效数据行: {coord} - 错误: {str(ve)}")
                        continue

                connection.commit()
                self.logger.info(f"Coordinates of the file {coord_file} have been saved to the database")

            self.logger.info("All coordinate data has been successfully saved to the database")

        except Exception as e:
            self.logger.error(f"保存坐标到数据库失败: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()