import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json

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
            agent VARCHAR(100) NOT NULL,
            tool_calls TEXT,
            content TEXT,
            role VARCHAR(30),
            tool_calls_id VARCHAR(200),
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
            
            # 检查并更新表结构（兼容旧版本）
            self._update_table_structure()
            
            cursor.close()
        except Error as e:
            print(f"创建表时发生错误: {e}")
    
    def _update_table_structure(self):
        """更新表结构以兼容新版本"""
        try:
            cursor = self.connection.cursor()
            
            # 检查并添加agent列（如果不存在）
            try:
                cursor.execute("ALTER TABLE history ADD COLUMN agent VARCHAR(100) NOT NULL DEFAULT 'default_agent'")
                print("已添加agent列到history表")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    print(f"添加agent列时发生错误: {e}")
            
            # 检查并修改tool_calls列为TEXT类型（如果存在）
            try:
                cursor.execute("ALTER TABLE history MODIFY COLUMN tool_calls TEXT")
                print("已将tool_calls列修改为TEXT类型")
            except Error as e:
                if "Unknown column 'tool_calls' in 'history'" not in str(e):
                    print(f"修改tool_calls列时发生错误: {e}")
            
            # 检查并修改content列为TEXT类型（如果存在）
            try:
                cursor.execute("ALTER TABLE history MODIFY COLUMN content TEXT")
                print("已将content列修改为TEXT类型")
            except Error as e:
                if "Unknown column 'content' in 'history'" not in str(e):
                    print(f"修改content列时发生错误: {e}")
            
            # 检查并重命名is_llm列为role（如果存在）
            try:
                cursor.execute("ALTER TABLE history CHANGE is_llm role VARCHAR(30)")
                print("已将is_llm列重命名为role")
            except Error as e:
                if "Unknown column 'is_llm' in 'history'" not in str(e):
                    print(f"重命名is_llm列时发生错误: {e}")
            
            # 检查并添加tool_calls_id列（如果不存在）
            try:
                cursor.execute("ALTER TABLE history ADD COLUMN tool_calls_id VARCHAR(200)")
                print("已添加tool_calls_id列到history表")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    print(f"添加tool_calls_id列时发生错误: {e}")
            
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"更新表结构时发生错误: {e}")
    
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
    
    def clear_users_table(self):
        """清空用户表中的所有数据"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM users")
            self.connection.commit()
            cursor.close()
            print("用户表已清空")
            return True
        except Error as e:
            print(f"清空用户表时发生错误: {e}")
            return False
    
    def clear_history_table(self):
        """清空历史记录表中的所有数据"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM history")
            self.connection.commit()
            cursor.close()
            print("历史记录表已清空")
            return True
        except Error as e:
            print(f"清空历史记录表时发生错误: {e}")
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
    
    def insert_history(self, user_name="", agent_name="", tool_calls=[], content="", role="", tool_calls_id=None):
        """
        插入历史记录，成功返回True，失败返回False
        
        参数:
        - user_name: 用户名
        - agent_name: 代理名称
        - tool_calls: 工具调用列表，格式如 [{"id":"1","type": "function", "function":{"name":"get_weather","arguments":"12"}}]
        - content: 内容文本
        - role: 角色（如"user", "assistant"等）
        - tool_calls_id: 工具调用ID（可选）
        """
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO history (name, agent, tool_calls, content, role, tool_calls_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # 将tool_calls列表转换为JSON字符串
            tool_calls_json = json.dumps(tool_calls) if tool_calls else None
            
            cursor.execute(insert_query, (user_name, agent_name, tool_calls_json, content, role, tool_calls_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"插入历史记录时发生错误: {e}")
            return False
    
    def get_all_history(self, user_name, agent_name):
        """获取指定用户和代理的所有历史记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT tool_calls, content, role, tool_calls_id, created_at 
            FROM history 
            WHERE name = %s AND agent = %s
            ORDER BY created_at DESC
            """
            cursor.execute(select_query, (user_name, agent_name))
            result = cursor.fetchall()
            cursor.close()
            
            # 处理结果，将JSON字符串转换回列表，并过滤空字段
            processed_result = []
            for record in result:
                processed_record = {
                    "role": record["role"],
                    "content": record["content"]
                }
                
                # 如果tool_calls存在且不为空，则添加到结果中
                if record["tool_calls"]:
                    try:
                        processed_record["tool_calls"] = json.loads(record["tool_calls"])
                    except json.JSONDecodeError:
                        processed_record["tool_calls"] = record["tool_calls"]
                
                # 如果tool_calls_id存在且不为空，则添加到结果中
                if record["tool_calls_id"]:
                    processed_record["tool_calls_id"] = record["tool_calls_id"]
                
                #processed_record["created_at"] = record["created_at"]
                processed_result.append(processed_record)
            
            return processed_result
        except Error as e:
            print(f"获取历史记录时发生错误: {e}")
            return []
    
    def get_last_n_history(self, user_name, agent_name, n=1):
        """获取指定用户和代理的最近n条历史记录，按id递减排序"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT tool_calls, content, role, tool_calls_id, created_at 
            FROM history 
            WHERE name = %s AND agent = %s
            ORDER BY id DESC 
            LIMIT %s
            """
            cursor.execute(select_query, (user_name, agent_name, n))
            result = cursor.fetchall()
            cursor.close()
            
            # 将结果按时间正序排列
            result.reverse()
            
            # 处理结果，将JSON字符串转换回列表，并过滤空字段
            processed_result = []
            for record in result:
                processed_record = {
                    "role": record["role"],
                    "content": record["content"]
                }
                
                # 如果tool_calls存在且不为空，则添加到结果中
                if record["tool_calls"]:
                    try:
                        processed_record["tool_calls"] = json.loads(record["tool_calls"])
                    except json.JSONDecodeError:
                        processed_record["tool_calls"] = record["tool_calls"]
                
                # 如果tool_calls_id存在且不为空，则添加到结果中
                if record["tool_calls_id"]:
                    processed_record["tool_calls_id"] = record["tool_calls_id"]
                
                #processed_record["created_at"] = record["created_at"]
                processed_result.append(processed_record)
            
            return processed_result
        except Error as e:
            print(f"获取最近历史记录时发生错误: {e}")
            return []
    
    def get_history_by_tool_calls_id(self, tool_calls_id):
        """根据tool_calls_id获取历史记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT name, agent, tool_calls, content, role, created_at 
            FROM history 
            WHERE tool_calls_id = %s
            ORDER BY created_at ASC
            """
            cursor.execute(select_query, (tool_calls_id,))
            result = cursor.fetchall()
            cursor.close()
            
            # 处理结果，将JSON字符串转换回列表，并过滤空字段
            processed_result = []
            for record in result:
                processed_record = {
                    "name": record["name"],
                    "agent": record["agent"],
                    "role": record["role"],
                    "content": record["content"]
                }
                
                # 如果tool_calls存在且不为空，则添加到结果中
                if record["tool_calls"]:
                    try:
                        processed_record["tool_calls"] = json.loads(record["tool_calls"])
                    except json.JSONDecodeError:
                        processed_record["tool_calls"] = record["tool_calls"]
                
                #processed_record["created_at"] = record["created_at"]
                processed_result.append(processed_record)
            
            return processed_result
        except Error as e:
            print(f"根据tool_calls_id获取历史记录时发生错误: {e}")
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
        tool_calls_id = "call_12345"
        
        # 示例tool_calls数据
        tool_calls_data = [
            {
                "id": "1",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": "{\"city\": \"Beijing\"}"
                }
            }
        ]
        
        success = db_manager.insert_history("alice", "agent1", tool_calls_data, "查询北京天气", "assistant", tool_calls_id)
        print(f"插入结果: {success}")
        
        success = db_manager.insert_history("alice", "agent1", [], "我想知道北京的天气", "user", tool_calls_id)
        print(f"插入结果: {success}")
        
        success = db_manager.insert_history("alice", "agent1", None, "翻译Hello World", "assistant", "call_67890")
        print(f"插入结果: {success}")
        
        # 获取所有历史记录
        print("获取agent1的所有历史记录...")
        history = db_manager.get_all_history("alice", "agent1")
        for i, record in enumerate(history, 1):
            print(record)
        
        # 获取最近2条历史记录
        print("获取agent1的最近2条历史记录...")
        recent_history = db_manager.get_last_n_history("alice", "agent1", 2)
        for i, record in enumerate(recent_history, 1):
            print(record)
            
        # 根据tool_calls_id获取历史记录
        print(f"根据tool_calls_id '{tool_calls_id}' 获取历史记录...")
        tool_history = db_manager.get_history_by_tool_calls_id(tool_calls_id)
        for i, record in enumerate(tool_history, 1):
            print(record)
            
        # 测试清空表功能
        print("\n=== 测试清空表功能 ===")
        print("清空历史记录表...")
        success = db_manager.clear_history_table()
        print(f"清空结果: {success}")
        
        print("清空用户表...")
        success = db_manager.clear_users_table()
        print(f"清空结果: {success}")
            
    finally:
        # 关闭数据库连接
        db_manager.close_connection()

if __name__ == "__main__":
    main()
