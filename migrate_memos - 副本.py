import traceback
import sqlite3
import mysql.connector
import datetime  # 导入 datetime 模块

# SQLite 数据库文件
sqlite_db_file = 'path\\memos_prod.db'

# MySQL 数据库连接参数
mysql_config = {
    'user': '',
    'password': '',
    'host': '',  # 不需要加端口号
    'database': '',
    'raise_on_warnings': True,
}

def migrate_data():
    # 连接SQLite数据库
    sqlite_conn = sqlite3.connect(sqlite_db_file)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # 连接MySQL数据库
    mysql_conn = mysql.connector.connect(**mysql_config)
    mysql_cursor = mysql_conn.cursor()

    try:
        # 依次处理每张表的数据迁移
        tables = [
            "migration_history", "system_setting", "user", "user_setting",
            "memo", "memo_organizer", "memo_relation", "resource",
             "activity", "reaction", "idp", "inbox", "webhook"
        ]

        for table in tables:
            # 查询SQLite表数据
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()

            # 获取SQLite表的列名
            columns = [f"{col[0]}" for col in sqlite_cursor.description]

            # 构造MySQL插入语句
            column_names = '`, `'.join(columns)
            column_names = '`'+column_names+'`'
            print(f"column_names: {column_names}")
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

            # 执行插入操作
            for row in rows:
                # 处理日期时间值的转换
                if 'created_ts' in row.keys():
                    created_ts = int(row['created_ts'])  # 将字符串转换为整数
                    created_ts_str = datetime.datetime.fromtimestamp(created_ts).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"created time: '{created_ts_str}'.")
                    row = dict(row)  # 将 sqlite3.Row 转换为字典以便修改
                    row['created_ts'] = created_ts_str

                if 'updated_ts' in row.keys():
                    updated_ts = int(row['updated_ts'])  # 将字符串转换为整数
                    updated_ts_str = datetime.datetime.fromtimestamp(updated_ts).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"updated time: '{updated_ts_str}'.")
                    row = dict(row)  # 将 sqlite3.Row 转换为字典以便修改
                    row['updated_ts'] = updated_ts_str

                if 'version' in row.keys():
                    # 检查是否已经存在相同的 version
                    check_query = f"SELECT COUNT(*) FROM {table} WHERE version = %s"
                    mysql_cursor.execute(check_query, (row['version'],))
                    result = mysql_cursor.fetchone()
                    if result[0] > 0:
                        print(f"Skipping insertion of duplicate version '{row['version']}' in table '{table}'.")
                        continue

                if 'version' in row.keys():
                    # 检查是否已经存在相同的 version
                    check_query = f"SELECT COUNT(*) FROM {table} WHERE version = %s"
                    mysql_cursor.execute(check_query, (row['version'],))
                    result = mysql_cursor.fetchone()
                    if result[0] > 0:
                        print(f"Skipping insertion of duplicate version '{row['version']}' in table '{table}'.")
                        continue

                # 执行插入操作
                values = tuple(row[col] for col in columns)
                mysql_cursor.execute(insert_query, values)

            # 提交MySQL事务
            mysql_conn.commit()

            print(f"Table '{table}' migrated successfully.")

    except mysql.connector.Error as mysql_err:
        print(f"MySQL Error occurred: {mysql_err.msg}")
        traceback.print_exc()  # 输出异常回溯信息
        mysql_conn.rollback()

    except sqlite3.Error as sqlite_err:
        print(f"SQLite Error occurred: {sqlite_err}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()  # 输出异常回溯信息
        mysql_conn.rollback()

    finally:
        # 关闭数据库连接
        sqlite_conn.close()
        mysql_conn.close()

# 执行数据迁移
migrate_data()