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
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id INT NOT NULL,
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
    
    def insert_histroy(self, id, tool, text):
        """插入历史信息数据"""
        insert_query = """
        INSERT INTO histroy (id,tool,text)
        VALUES (%s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (id, tool, text))
            self.connection.commit()
            print(f"历史信息插入成功，ID: {id},tool: {tool},text : {text}")
            return id
        except Error as e:
            print(f"插入失败: {e}")
            return None
    def insert_user(self, name, email, password):
        """插入用户数据"""
        insert_query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (name, email, password))
            self.connection.commit()
            print(f"用户 {name} 插入成功，ID: {cursor.lastrowid}")
            return cursor.lastrowid
        except Error as e:
            print(f"插入失败: {e}")
            return None
    def get_users(self):
        """查询所有用户"""
        select_query = "SELECT * FROM users"
        try:
            cursor = self.connection.cursor(dictionary=True)  # 返回字典格式
            cursor.execute(select_query)
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"查询失败: {e}")
            return []
    def get_history(self):
        """查询历史记录"""
        select_query = "SELECT * FROM history"
        try:
            cursor = self.connection.cursor(dictionary=True)  # 返回字典格式
            cursor.execute(select_query)
            history = cursor.fetchall()
            return history
        except Error as e:
            print(f"查询失败: {e}")
            return []
    def update_user(self, user_id, age):
        """更新用户年龄"""
        update_query = "UPDATE users SET age = %s WHERE id = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(update_query, (age, user_id))
            self.connection.commit()
            print(f"用户 {user_id} 更新成功")
            return cursor.rowcount
        except Error as e:
            print(f"更新失败: {e}")
            return 0
    
    def delete_user(self, user_id):
        """删除用户"""
        delete_query = "DELETE FROM users WHERE id = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_query, (user_id,))
            self.connection.commit()
            print(f"用户 {user_id} 删除成功")
            return cursor.rowcount
        except Error as e:
            print(f"删除失败: {e}")
            return 0

# 使用示例
if __name__ == "__main__":
    db = MySQLDatabase('localhost', 'test_db', 'root', '123456')
    
    if db.connect():
        # 创建表
        db.create_table()
        
        # 插入数据
        db.insert_user('张三', 'zhangsan@email.com', 25)
        db.insert_user('李四', 'lisi@email.com', 30)
        
        # 查询数据
        users = db.get_users()
        print("所有用户:")
        for user in users:
            print(user)
        
        # 更新数据
        if users:
            db.update_user(users[0]['id'], 26)
        
        # 再次查询
        users = db.get_users()
        print("更新后的用户:")
        for user in users:
            print(user)
        
        # 关闭连接
        db.disconnect()
