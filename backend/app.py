from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from utils.qrcode_util import generate_and_save_qrcodes
from config import CONFIG
from utils.image_processor import ImageProcessor  # 导入图像处理类
from utils.detector import RubberTreeDetector  # 导入检测器类
from utils.coordinate_processor import CoordinateProcessor  # 导入坐标处理类
from utils.db_processor import DatabaseProcessor  # 导入数据库处理类
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# JWT 配置
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # 更改为你的密钥
jwt = JWTManager(app)

# 数据库连接函数
def get_db_connection():
    connection = mysql.connector.connect(
        host=CONFIG['database']['host'],
        user=CONFIG['database']['user'],
        password=CONFIG['database']['password'],
        database=CONFIG['database']['database']
    )
    return connection
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Rubber Tree System API!"})
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    username = request.json.get('username')
    password = request.json.get('password')

    connection = get_db_connection()
    if connection is None:
        return jsonify({"msg": "数据库连接失败"}), 500  # 处理连接失败的情况

    cursor = connection.cursor()

    # 检查用户是否已存在
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        print(f"用户 {username} 已存在")  # 添加调试信息
        return jsonify({"msg": "用户已存在"}), 400

    # 存储用户信息，明文密码
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    connection.commit()

    cursor.close()
    connection.close()

    print(f"用户 {username} 注册成功")  # 添加调试信息
    return jsonify({"msg": "注册成功"}), 201
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    username = request.json.get('username')
    password = request.json.get('password')

    connection = get_db_connection()
    if connection is None:
        return jsonify({"msg": "数据库连接失败"}), 500  # 处理连接失败的情况

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        print(f"找到用户: {username}")  # 添加调试信息
        if user[2] == password:  # user[1] 是明文密码
            access_token = create_access_token(identity=username)
            print(f"用户 {username} 登录成功")  # 添加调试信息
            return jsonify(access_token=access_token), 200
        else:
            print(f"用户 {username} 密码错误")  # 添加调试信息
    else:
        print(f"用户 {username} 不存在")  # 添加调试信息

    return jsonify({"msg": "用户名或密码错误"}), 401
@app.route('/api/upload/dom', methods=['POST'])
def upload_dom_file():
    """处理 DOM 文件上传"""
    if 'domFile' not in request.files:
        return jsonify({'error': '没有 DOM 文件被上传'}), 400

    file = request.files['domFile']
    if file.filename == '':
        return jsonify({'error': '没有选择 DOM 文件'}), 400

    # 获取当前文件的绝对路径
    base_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
    save_path = os.path.join(base_path, 'input', 'dom', file.filename)  # 保存到 backend/input/dom
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 确保目录存在
    file.save(save_path)

    return jsonify({'message': 'DOM 文件上传成功！'}), 200
@app.route('/api/upload/dsm', methods=['POST'])
def upload_dsm_file():
    """处理 DSM 文件上传"""
    if 'dsmFile' not in request.files:
        return jsonify({'error': '没有 DSM 文件被上传'}), 400

    file = request.files['dsmFile']
    if file.filename == '':
        return jsonify({'error': '没有选择 DSM 文件'}), 400

    # 获取当前文件的绝对路径
    base_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
    save_path = os.path.join(base_path, 'input', 'dsm', file.filename)  # 保存到 backend/input/dsm
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 确保目录存在
    file.save(save_path)

    return jsonify({'message': 'DSM 文件上传成功！'}), 200
# 获取文件夹的绝对路径
def get_directory_path(folder_name):
    base_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
    return os.path.join(base_path, 'output', folder_name)
@app.route('/api/dom_count', methods=['GET'])
def get_dom_count():
    """获取 DOM 分割数量"""
    try:
        dom_tiles_path = get_directory_path('dom_tiles')
        count = len([name for name in os.listdir(dom_tiles_path) if os.path.isfile(os.path.join(dom_tiles_path, name))])  # 计算文件数量
    except Exception as e:
        print(f"读取 DOM 分割数量失败: {e}")
        return jsonify({'count': 0}), 500  # 如果读取失败，返回 0

    return jsonify({'count': count})
@app.route('/api/dsm_count', methods=['GET'])
def get_dsm_count():
    """获取 DSM 分割数量"""
    try:
        dsm_tiles_path = get_directory_path('dsm_tiles')
        count = len([name for name in os.listdir(dsm_tiles_path) if os.path.isfile(os.path.join(dsm_tiles_path, name))])  # 计算文件数量
    except Exception as e:
        print(f"读取 DSM 分割数量失败: {e}")
        return jsonify({'count': 0}), 500  # 如果读取失败，返回 0

    return jsonify({'count': count})
@app.route('/api/process', methods=['POST'])
def process_files():
    """处理上传的 DOM 和 DSM 文件"""
    try:
        # 创建图像处理器实例
        config = {
            'input_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'input')),  # 输入目录
            'output_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))  # 输出目录
        }
        processor = ImageProcessor(config)

        # 执行处理
        processor.process_first_step()

        return jsonify({'message': '文件处理完成，切割和CSV生成成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/detect', methods=['POST'])
def detect_objects():
    """对切割好的DOM图片进行检测"""
    try:
        # 使用 CONFIG 中的权重目录
        config = {
            'weights_dir': CONFIG['weights_dir'],  # 从配置中获取权重目录
            'output_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))  # 输出目录
        }
        detector = RubberTreeDetector(config)

        # 执行检测
        detector.detect_tiles()

        return jsonify({'message': '检测完成，结果已保存！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/process_coordinates', methods=['POST'])
def process_coordinates():
    """处理检测结果以提取坐标信息"""
    try:
        # 创建坐标处理器实例
        config = {
            'output_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))  # 输出目录
        }
        coordinate_processor = CoordinateProcessor(config)

        # 执行坐标处理
        coordinate_processor.process_detection_results()  # 确保调用了处理检测结果的方法

        return jsonify({'message': '坐标处理完成，结果已保存！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/save_coordinates', methods=['POST'])
def save_coordinates():
    """将坐标结果保存到数据库"""
    try:
        # 创建数据库处理器实例
        config = {
            'output_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'output')),  # 输出目录
            'database': {
                'host': CONFIG['database']['host'],
                'user': CONFIG['database']['user'],
                'password': CONFIG['database']['password'],
                'database': CONFIG['database']['database']
            }
        }
        db_processor = DatabaseProcessor(config)

        # 创建数据表
        db_processor.create_table()

        # 保存坐标
        db_processor.save_coordinates()

        return jsonify({'message': '坐标数据已成功保存到数据库！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/coordinates', methods=['GET'])
def get_coordinates():
    """获取所有坐标信息"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tree_coordinates")
    coordinates = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(coordinates)
@app.route('/api/get_tree_ids', methods=['GET'])
def get_tree_ids():
    """获取所有树木 ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM tree_data")  # 查询树木 ID
        tree_ids = [row[0] for row in cursor.fetchall()]  # 获取所有树木 ID
        return jsonify({"tree_ids": tree_ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
@app.route('/api/input_tree_data', methods=['POST'])
def input_tree_data():
    """输入树木数据"""
    data = request.json

    # 从请求中提取数据
    required_fields = [
        'id', 'yield', 'tree_height', 'branch_height',
        'crown_diameter', 'cross_section_area', 'crown_area',
        'crown_volume', 'biomass'
    ]

    # 检查所有必需字段是否存在
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少字段: {field}"}), 400

    # 提取数据
    tree_id = data['id']  # 使用 id
    yield_data = data['yield']
    tree_height = data['tree_height']
    branch_height = data['branch_height']  # 确保使用正确的字段名
    crown_diameter = data['crown_diameter']
    cross_section_area = data['cross_section_area']
    crown_area = data['crown_area']
    crown_volume = data['crown_volume']
    biomass = data['biomass']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 更新树木数据
        cursor.execute("""
            UPDATE tree_data SET 
            yield = %s, 
            tree_height = %s, 
            branch_height = %s,  -- 修改为正确的列名
            crown_diameter = %s, 
            cross_section_area = %s, 
            crown_area = %s, 
            crown_volume = %s, 
            biomass = %s 
            WHERE id = %s
        """, (yield_data, tree_height, branch_height, crown_diameter,
              cross_section_area, crown_area, crown_volume, biomass, tree_id))

        connection.commit()  # 提交更改
        return jsonify({"message": "树木数据已成功更新！"}), 200

    except Exception as e:
        return jsonify({"error": f"更新树木数据失败: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()
@app.route('/api/get_tree_data/<int:id>', methods=['GET'])
def get_tree_data(id):
    """根据 id 获取树木的详细数据"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tree_data WHERE id = %s", (id,))
        tree_data = cursor.fetchone()

        if tree_data:
            return jsonify(tree_data), 200
        else:
            return jsonify({"error": "未找到树木数据"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



@app.route('/api/generate_qrcode', methods=['POST'])
def generate_qrcode():
    """
    @function generate_qrcode
    @description 生成二维码的API接口
    @return {json} 包含二维码base64字符串的响应
    """
    try:
        qrcode_base64 = generate_and_save_qrcodes()
        if qrcode_base64:
            return jsonify({
                'status': 'success',
                'qrcode': qrcode_base64
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '无法生成二维码，请检查数据库连接和数据'
            }), 500
    except Exception as e:
        print(f"API错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'生成二维码时出错: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True)