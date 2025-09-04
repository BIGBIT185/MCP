import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
    def __init__(self, host, database, user, password, port=3306):
        self.config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.connection = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("数据库连接成功")
            return True
        except Error as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def create_table(self):
        """创建表"""
        create_user_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(100),
            name VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100),
            password VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id VARCHAR(100),
            tool VARCHAR(100),
            text VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_user_table_query)
            cursor.execute(create_history_table_query)
            print("表创建成功")
        except Error as e:
            print(f"创建表失败: {e}")
    def insert_user(self, name, password):
        """插入用户数据"""
        insert_query = """
        INSERT INTO users (id,name, email, password)
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, ("",name,"", password))
            self.connection.commit()
            print(f"用户 {name} 插入成功")
            return True
        except Error as e:
            print(f"插入失败: {e}")
            return False
    def is_legal_user(self, name: str, password: str) -> bool:
        """
        检查是否存在合法的用户
        
        Args:
            name: 用户名
            password: 密码（明文）
        
        Returns:
            bool: 如果用户存在且密码正确返回 True，否则返回 False
        """
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor(dictionary=True)  # 返回字典格式的结果
            
            # 使用参数化查询防止SQL注入
            query = "SELECT id, password FROM users WHERE name = %s"
            cursor.execute(query, (name,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result is None:
                print(f"用户 '{name}' 不存在")
                return False
            
            # 验证密码（这里假设密码是加密存储的）
            stored_password = result['password']
            user_id = result['id']
            
            # 比较密码（实际应该使用加密比较）
            if self.verify_password(password, stored_password):
                print(f"用户 '{name}' (ID: {user_id}) 验证成功")
                return True
            else:
                print(f"用户 '{name}' 密码错误")
                return False
                
        except Error as e:
            print(f"数据库查询错误: {e}")
            return False
        
    def has_user(self, name: str) -> bool:
        """
        检查是否存在该用户
        """
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor(dictionary=True)  # 返回字典格式的结果
            
            # 使用参数化查询防止SQL注入
            query = "SELECT id, password FROM users WHERE name = %s"
            cursor.execute(query, (name,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result is None:
                print(f"用户 '{name}' 不存在")
                return False
            
            return True
                
        except Error as e:
            print(f"数据库查询错误: {e}")
            return False
