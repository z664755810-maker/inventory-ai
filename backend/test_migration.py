import unittest
import sqlite3
import tempfile
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from migrate_to_mysql import (
    escape_mysql_identifier,
    sqlite_to_mysql_type,
    get_sqlite_tables,
    get_table_columns,
    MYSQL_RESERVED_WORDS
)

class TestMigrationUtils(unittest.TestCase):
    
    def test_escape_mysql_identifier(self):
        self.assertEqual(escape_mysql_identifier('pending'), '`pending`')
        self.assertEqual(escape_mysql_identifier('issue'), '`issue`')
        self.assertEqual(escape_mysql_identifier('role'), '`role`')
        self.assertEqual(escape_mysql_identifier('status'), '`status`')
        self.assertEqual(escape_mysql_identifier('order'), '`order`')
        self.assertEqual(escape_mysql_identifier('user'), '`user`')
        self.assertEqual(escape_mysql_identifier('normal_column'), '`normal_column`')
        self.assertEqual(escape_mysql_identifier('Pending'), '`Pending`')
        self.assertEqual(escape_mysql_identifier('ORDER'), '`ORDER`')
    
    def test_sqlite_to_mysql_type(self):
        self.assertEqual(sqlite_to_mysql_type('INTEGER'), ('INT', False))
        self.assertEqual(sqlite_to_mysql_type('BIGINT'), ('BIGINT', False))
        self.assertEqual(sqlite_to_mysql_type('VARCHAR(255)'), ('VARCHAR(255)', False))
        self.assertEqual(sqlite_to_mysql_type('TEXT'), ('TEXT', True))
        self.assertEqual(sqlite_to_mysql_type('DECIMAL(10,2)'), ('DECIMAL(10,2)', False))
        self.assertEqual(sqlite_to_mysql_type('DATETIME'), ('DATETIME', False))
        self.assertEqual(sqlite_to_mysql_type('DATE'), ('DATE', False))
        self.assertEqual(sqlite_to_mysql_type('TIME'), ('TIME', False))
        self.assertEqual(sqlite_to_mysql_type('FLOAT'), ('FLOAT', False))
        self.assertEqual(sqlite_to_mysql_type('REAL'), ('DOUBLE', False))
        self.assertEqual(sqlite_to_mysql_type('BOOLEAN'), ('TINYINT(1)', False))
        self.assertEqual(sqlite_to_mysql_type('BLOB'), ('LONGBLOB', True))
        self.assertEqual(sqlite_to_mysql_type('CLOB'), ('TEXT', True))
        self.assertEqual(sqlite_to_mysql_type('UNKNOWN_TYPE'), ('VARCHAR(255)', False))
    
    def test_sqlite_to_mysql_type_no_default(self):
        mysql_type, no_default = sqlite_to_mysql_type('TEXT')
        self.assertTrue(no_default)
        
        mysql_type, no_default = sqlite_to_mysql_type('BLOB')
        self.assertTrue(no_default)
        
        mysql_type, no_default = sqlite_to_mysql_type('INTEGER')
        self.assertFalse(no_default)
        
        mysql_type, no_default = sqlite_to_mysql_type('VARCHAR(255)')
        self.assertFalse(no_default)
    
    def test_reserved_words_contains_keywords(self):
        self.assertIn('pending', MYSQL_RESERVED_WORDS)
        self.assertIn('issue', MYSQL_RESERVED_WORDS)
        self.assertIn('role', MYSQL_RESERVED_WORDS)
        self.assertIn('status', MYSQL_RESERVED_WORDS)
        self.assertIn('order', MYSQL_RESERVED_WORDS)
        self.assertIn('user', MYSQL_RESERVED_WORDS)
        self.assertIn('group', MYSQL_RESERVED_WORDS)
        self.assertIn('desc', MYSQL_RESERVED_WORDS)

class TestSQLiteOperations(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                role TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount DECIMAL(10,2),
                status VARCHAR(20)
            )
        ''')
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
        os.unlink(self.db_path)
    
    def test_get_sqlite_tables(self):
        tables = get_sqlite_tables(self.cursor)
        self.assertIn('test_table', tables)
        self.assertIn('orders', tables)
    
    def test_get_table_columns(self):
        columns = get_table_columns(self.cursor, 'test_table')
        self.assertEqual(len(columns), 5)
        
        col_names = [col[1] for col in columns]
        self.assertIn('id', col_names)
        self.assertIn('name', col_names)
        self.assertIn('status', col_names)
        self.assertIn('role', col_names)
        self.assertIn('created_at', col_names)
    
    def test_table_column_attributes(self):
        columns = get_table_columns(self.cursor, 'test_table')
        
        for col in columns:
            if col[1] == 'id':
                self.assertEqual(col[2].upper(), 'INTEGER')
                self.assertEqual(col[3], 0)
                self.assertIsNone(col[4])
                self.assertEqual(col[5], 1)
            elif col[1] == 'name':
                self.assertEqual(col[2].upper(), 'VARCHAR(100)')
                self.assertEqual(col[3], 1)
                self.assertIsNone(col[4])
                self.assertEqual(col[5], 0)
            elif col[1] == 'status':
                self.assertEqual(col[2].upper(), 'VARCHAR(20)')
                self.assertEqual(col[3], 0)
                self.assertTrue(col[4] in ['pending', "'pending'"])
                self.assertEqual(col[5], 0)
            elif col[1] == 'role':
                self.assertEqual(col[2].upper(), 'TEXT')
                self.assertEqual(col[3], 0)
                self.assertIsNone(col[4])
                self.assertEqual(col[5], 0)

class TestEdgeCases(unittest.TestCase):
    
    def test_empty_table_name(self):
        with self.assertRaises(sqlite3.OperationalError):
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            get_table_columns(cursor, '')
    
    def test_nonexistent_table(self):
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        result = get_table_columns(cursor, 'nonexistent')
        self.assertEqual(result, [])
        conn.close()
    
    def test_escape_special_characters(self):
        self.assertEqual(escape_mysql_identifier('column with space'), '`column with space`')
        self.assertEqual(escape_mysql_identifier('column-name'), '`column-name`')
        self.assertEqual(escape_mysql_identifier('column.name'), '`column.name`')

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                parent_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                role TEXT,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                issue_date DATE,
                total_amount DECIMAL(12,2),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('INSERT INTO categories (name, parent_id) VALUES (?, ?)', ('电子产品', None))
        self.cursor.execute('INSERT INTO categories (name, parent_id) VALUES (?, ?)', ('手机', 1))
        self.cursor.execute('INSERT INTO categories (name, parent_id) VALUES (?, ?)', ('电脑', 1))
        
        self.cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                          ('admin', 'hashed_password', 'admin'))
        self.cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                          ('user1', 'hashed_password', 'user'))
        
        self.cursor.execute('INSERT INTO invoices (invoice_no, issue_date, total_amount) VALUES (?, ?, ?)', 
                          ('INV-2024001', '2024-01-15', 1000.00))
        self.cursor.execute('INSERT INTO invoices (invoice_no, issue_date, total_amount) VALUES (?, ?, ?)', 
                          ('INV-2024002', '2024-01-16', 2500.00))
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_full_table_migration_flow(self):
        tables = get_sqlite_tables(self.cursor)
        self.assertIn('categories', tables)
        self.assertIn('users', tables)
        self.assertIn('invoices', tables)
        
        for table in tables:
            columns = get_table_columns(self.cursor, table)
            self.assertGreater(len(columns), 0)
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                mysql_type, no_default = sqlite_to_mysql_type(col_type)
                
                escaped_name = escape_mysql_identifier(col_name)
                self.assertTrue(escaped_name.startswith('`') and escaped_name.endswith('`'))
    
    def test_export_sql_generation(self):
        from migrate_to_mysql import export_sql_to_file
        
        temp_sql = tempfile.NamedTemporaryFile(suffix='.sql', delete=False)
        sql_path = temp_sql.name
        temp_sql.close()
        
        try:
            result = export_sql_to_file(self.db_path, sql_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(sql_path))
            
            with open(sql_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('CREATE TABLE', content)
            self.assertIn('`categories`', content)
            self.assertIn('`users`', content)
            self.assertIn('`invoices`', content)
            self.assertIn('`status`', content)
            self.assertIn('`role`', content)
            self.assertIn('INSERT INTO', content)
            
        finally:
            if os.path.exists(sql_path):
                os.unlink(sql_path)
    
    def test_data_count_validation(self):
        tables = ['categories', 'users', 'invoices']
        expected_counts = {'categories': 3, 'users': 2, 'invoices': 2}
        
        for table in tables:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = self.cursor.fetchone()[0]
            self.assertEqual(count, expected_counts[table])

class TestReservedWordHandling(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_column_name_with_reserved_word(self):
        reserved_cols = ['status', 'role', 'user', 'group', 'desc', 'asc', 'pending', 'issue']
        
        col_defs = ', '.join([f'`{col}` VARCHAR(50)' for col in reserved_cols])
        create_sql = f'CREATE TABLE test_reserved ({col_defs})'
        
        self.cursor.execute(create_sql)
        self.conn.commit()
        
        columns = get_table_columns(self.cursor, 'test_reserved')
        self.assertEqual(len(columns), len(reserved_cols))
        
        for col in columns:
            escaped = escape_mysql_identifier(col[1])
            self.assertTrue(escaped.startswith('`') and escaped.endswith('`'))
    
    def test_table_name_with_reserved_word(self):
        self.cursor.execute('CREATE TABLE `order` (id INTEGER PRIMARY KEY)')
        self.conn.commit()
        
        tables = get_sqlite_tables(self.cursor)
        self.assertIn('order', tables)

def run_tests():
    print("=" * 60)
    print("运行数据库迁移工具单元测试")
    print("=" * 60)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMigrationUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestSQLiteOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestReservedWordHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("[SUCCESS] 所有 {} 个测试通过！".format(result.testsRun))
    else:
        print("[FAILED] {} 个测试失败，{} 个错误".format(len(result.failures), len(result.errors)))
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)