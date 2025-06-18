import qrcode
import base64
from io import BytesIO
import mysql.connector

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': '橡胶树信息'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return None

def ensure_qrcode_column_exists(cursor, table_name='tree_data'):
    cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'qrcode'")
    result = cursor.fetchone()
    if not result:
        print("⚠️ 未检测到 'qrcode' 字段，正在添加...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN qrcode LONGTEXT")
        print("✅ 'qrcode' 字段已添加")
    else:
        print("✅ 'qrcode' 字段已存在")

def generate_qrcode_with_id(tree_id):
    frontend_url = f"http://localhost:8080/tree/{tree_id}"
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2
    )
    qr.add_data(frontend_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2c3e50", back_color="#ffffff")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_qrcode_base64(data_dict):
    def safe(v):
        return str(v) if v not in [None, ""] else "—"

    content = f"""🌿 Variety Right Info
Name: {safe(data_dict.get("variety_name"))}
Right No.: {safe(data_dict.get("variety_right_number"))}
Authorization Date: {safe(data_dict.get("authorization_date"))}
Breeder: {safe(data_dict.get("breeder"))}
Origin: {safe(data_dict.get("variety_origin"))}
Suitable Region: {safe(data_dict.get("suitable_region"))}
Rights Holder: {safe(data_dict.get("rights_holder"))}

🌱 Planting Info
Planting Unit: {safe(data_dict.get("planter_unit"))}
Planting Date: {safe(data_dict.get("planting_date"))}
Coordinates: {safe(data_dict.get("longitude"))}, {safe(data_dict.get("latitude"))}
Elevation: {safe(data_dict.get("elevation"))} m
"""

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2c3e50", back_color="#ffffff")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_and_save_qrcodes():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        ensure_qrcode_column_exists(cursor)

        print("🔍 正在查找缺失二维码的记录...")
        cursor.execute("""
            SELECT id, longitude, latitude, elevation,
                   variety_name, rights_holder, variety_right_number, authorization_date,
                   breeder, variety_origin, suitable_region,
                   planter_unit, planting_date
            FROM tree_data
            WHERE qrcode IS NULL OR qrcode = ''
        """)
        rows = cursor.fetchall()
        if not rows:
            print("✅ 所有记录都已生成二维码，无需处理。")
            return

        print(f"📦 共找到 {len(rows)} 条待处理记录。")

        for row in rows:
            id_ = row["id"]
            data_dict = {k: (v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else v) for k, v in row.items() if k != 'id'}

            # 二选一：
            # qrcode_base64 = generate_qrcode_base64(data_dict)  # 内容二维码
            qrcode_base64 = generate_qrcode_with_id(id_)        # 跳转二维码

            cursor.execute(
                "UPDATE tree_data SET qrcode = %s WHERE id = %s",
                (qrcode_base64, id_)
            )

        conn.commit()
        print("✅ 二维码批量生成并保存成功。")

    except Exception as e:
        print(f"❌ 处理过程中出错: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("🔚 数据库连接已关闭")

if __name__ == "__main__":
    generate_and_save_qrcodes()
