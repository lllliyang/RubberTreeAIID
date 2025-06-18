import mysql.connector
import logging
from typing import Dict

class DataInputProcessor:
    """
    数据输入处理器：将树木数据保存到MySQL数据库
    """

    def __init__(self, config: Dict):
        """
        初始化数据输入处理器
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
        except mysql.connector.Error as e:
            self.logger.error(f"数据库连接失败: {str(e)}")
            raise

    def save_tree_data(self, tree_id: str, yield_data: float, tree_height: float, branchHeight: float,
                       crownDiameter: float, crossSectionArea: float, crownArea: float,
                       crownVolume: float, biomass: float, longitude: float, latitude: float,
                       elevation: float, image_name: str):
        """将树木数据保存到数据库"""
        # 检查非负数
        if yield_data < 0 or tree_height < 0 or branchHeight < 0 or crownDiameter < 0 or \
           crossSectionArea < 0 or crownArea < 0 or crownVolume < 0 or biomass < 0:
            self.logger.error("输入数据无效，必须为非负数")
            raise ValueError("输入数据无效，必须为非负数")

        # 检查经度和纬度范围
        if longitude < -180 or longitude > 180:
            self.logger.error("输入数据无效，经度必须在 -180 到 180 之间")
            raise ValueError("输入数据无效，经度必须在 -180 到 180 之间")

        if latitude < -90 or latitude > 90:
            self.logger.error("输入数据无效，纬度必须在 -90 到 90 之间")
            raise ValueError("输入数据无效，纬度必须在 -90 到 90 之间")

        try:
            with self.connect_to_db() as connection:
                with connection.cursor() as cursor:
                    # 准备插入语句
                    insert_query = """
                    INSERT INTO tree_data (tree_id, yield, treeHeight, branchHeight, crownDiameter, 
                                           crossSectionArea, crownArea, crownVolume, biomass,
                                           longitude, latitude, elevation, image_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (tree_id, yield_data, tree_height, branchHeight, crownDiameter,
                            crossSectionArea, crownArea, crownVolume, biomass,
                            longitude, latitude, elevation, image_name)
                    cursor.execute(insert_query, data)
                    connection.commit()
                    self.logger.info(f"树木数据 {tree_id} 已成功保存到数据库")
                    return cursor.lastrowid  # 返回插入的记录 ID

        except mysql.connector.Error as e:
            self.logger.error(f"保存树木数据失败: {str(e)}")
            raise