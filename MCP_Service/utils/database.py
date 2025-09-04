import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseManager:
    def __init__(self, host="localhost", database="user_history_db", 
                 user="root", password=""):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("成功连接到MySQL数据库")
        except Error as e:
            print(f"连接MySQL数据库时发生错误: {e}")
            # 如果数据库不存在，尝试创建它
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
                if self.connection.is_connected():
                    cursor = self.connection.cursor()
                    cursor.execute(f"CREATE DATABASE {self.database}")
                    print(f"创建数据库 {self.database}")
                    cursor.close()
                    self.connection.close()
                    
                    # 重新连接到新创建的数据库
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        database=self.database,
                        user=self.user,
                        password=self.password
                    )
            except Error as e:
                print(f"创建数据库时发生错误: {e}")
    
    def create_tables(self):
        """创建用户表和历史记录表"""
        create_user_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            name VARCHAR(100) Primary key,
            password VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            tool VARCHAR(100),
            text VARCHAR(200),
            is_llm BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (name) REFERENCES users(name) ON DELETE CASCADE
        )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_user_table_query)
            cursor.execute(create_history_table_query)
            self.connection.commit()
            print("表创建成功或已存在")
            cursor.close()
        except Error as e:
            print(f"创建表时发生错误: {e}")
    
    def drop_all_tables(self):
        """
        删除数据库中的所有表
        成功返回True，失败返回False
        """
        try:
            cursor = self.connection.cursor()
            
            # 首先禁用外键检查，避免删除时出现外键约束错误
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 获取所有表名
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if not tables:
                print("数据库中没有表")
                return True
            
            # 删除所有表
            for table in tables:
                table_name = table[0]
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(drop_query)
                print(f"已删除表: {table_name}")
            
            # 重新启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.connection.commit()
            cursor.close()
            print("所有表已成功删除")
            return True
            
        except Error as e:
            print(f"删除表时发生错误: {e}")
            # 确保外键检查被重新启用，即使在出错的情况下
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                self.connection.commit()
            except:
                pass
            return False
    
    def insert_user(self, name, password):
        """插入用户，成功返回True，失败返回False"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO users (name, password) VALUES (%s, %s)"
            cursor.execute(insert_query, (name, password))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"插入用户时发生错误: {e}")
            return False
    
    def has_user(self, name):
        """检查用户是否存在，存在返回True，否则返回False"""
        try:
            cursor = self.connection.cursor()
            select_query = "SELECT name FROM users WHERE name = %s"
            cursor.execute(select_query, (name,))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            print(f"检查用户是否存在时发生错误: {e}")
            return False
    
    def is_legal_user(self, name, password):
        """验证用户名和密码，正确返回True，否则返回False"""
        try:
            cursor = self.connection.cursor()
            select_query = "SELECT name FROM users WHERE name = %s AND password = %s"
            cursor.execute(select_query, (name, password))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            print(f"验证用户时发生错误: {e}")
            return False
    
    def insert_history(self, name, tool, text, is_llm):
        """插入历史记录，成功返回True，失败返回False"""
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO history (name, tool, text, is_llm) 
            VALUES (%s, %s, %s, %s)
            """
            # 将Python的布尔值转换为MySQL支持的1/0
            is_llm_value = 1 if is_llm else 0
            cursor.execute(insert_query, (name, tool, text, is_llm_value))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"插入历史记录时发生错误: {e}")
            return False
    
    def get_all_history(self, name):
        """获取指定用户的所有历史记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT tool, text, is_llm, created_at 
            FROM history 
            WHERE name = %s 
            ORDER BY created_at desc
            """
            cursor.execute(select_query, (name,))
            result = cursor.fetchall()
            cursor.close()
            
            # 将MySQL的1/0转换回Python布尔值
            for record in result:
                record['is_llm'] = bool(record['is_llm'])
            return result
        except Error as e:
            print(f"获取历史记录时发生错误: {e}")
            return []
    
    def get_last_n_history(self, name, n):
        """获取指定用户的最近n条历史记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT tool, text, is_llm, created_at 
            FROM history 
            WHERE name = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(select_query, (name, n))
            result = cursor.fetchall()
            cursor.close()
            
            # 将结果按时间正序排列并转换布尔值
            result.reverse()
            for record in result:
                record['is_llm'] = bool(record['is_llm'])
            return result
        except Error as e:
            print(f"获取最近历史记录时发生错误: {e}")
            return []
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")

databasetool=DatabaseManager(
        host="localhost", 
        database="test_db",
        user="root", 
        password="123456"  # 请根据您的MySQL设置修改密码
    )

def main():
    # 初始化数据库管理器
    db_manager = DatabaseManager(
        host="localhost", 
        database="test_db",
        user="root", 
        password="123456"  # 请根据您的MySQL设置修改密码
    )
    
    try:
        # 测试用户管理功能
        print("\n=== 测试用户管理功能 ===")
        
        # 插入用户
        print("插入用户 'alice'...")
        success = db_manager.insert_user("alice", "password123")
        print(f"插入结果: {success}")
        
        print("再次插入用户 'alice' (应失败)...")
        success = db_manager.insert_user("alice", "password123")
        print(f"插入结果: {success}")
        
        # 检查用户是否存在
        print("检查用户 'alice' 是否存在...")
        exists = db_manager.has_user("alice")
        print(f"用户存在: {exists}")
        
        print("检查用户 'bob' 是否存在...")
        exists = db_manager.has_user("bob")
        print(f"用户存在: {exists}")
        
        # 验证用户
        print("验证用户 'alice' 和正确密码...")
        valid = db_manager.is_legal_user("alice", "password123")
        print(f"验证结果: {valid}")
        
        print("验证用户 'alice' 和错误密码...")
        valid = db_manager.is_legal_user("alice", "wrongpassword")
        print(f"验证结果: {valid}")
        
        # 测试历史记录功能
        print("\n=== 测试历史记录功能 ===")
        
        # 插入历史记录
        print("插入历史记录...")
        success = db_manager.insert_history("alice", "搜索引擎", "查询Python教程", True)
        print(f"插入结果: {success}")
        
        success = db_manager.insert_history("alice", "计算器", "计算2+2", False)
        print(f"插入结果: {success}")
        
        success = db_manager.insert_history("alice", "翻译工具", "翻译Hello World", True)
        print(f"插入结果: {success}")
        
        # 获取所有历史记录
        print("获取所有历史记录...")
        history = db_manager.get_all_history("alice")
        for i, record in enumerate(history, 1):
            print(f"{i}. {record['tool']}: {record['text']} (AI: {record['is_llm']}) - {record['created_at']}")
        
        # 获取最近2条历史记录
        print("获取最近2条历史记录...")
        recent_history = db_manager.get_last_n_history("alice", 2)
        for i, record in enumerate(recent_history, 1):
            print(f"{i}. {record['tool']}: {record['text']} (AI: {record['is_llm']}) - {record['created_at']}")
            
    finally:
        # 关闭数据库连接
        db_manager.close_connection()

if __name__ == "__main__":
    main()
