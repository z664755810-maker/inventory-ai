import os
import shutil

BACKUP_EXT = '.bak'

FILES_TO_ROLLBACK = [
    'frontend/categories.html',
    'frontend/css/style.css',
    'backend/migrate_to_mysql.py'
]

def get_full_path(relative_path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def check_backup_exists(filepath):
    backup_path = filepath + BACKUP_EXT
    return os.path.exists(backup_path)

def rollback_file(filepath):
    backup_path = filepath + BACKUP_EXT
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filepath)
        return True, f"Rollback successful: {filepath}"
    else:
        return False, f"Backup file not found: {backup_path}"

def show_status():
    print("=" * 60)
    print("File Status Check")
    print("=" * 60)
    
    for rel_path in FILES_TO_ROLLBACK:
        filepath = get_full_path(rel_path)
        backup_path = filepath + BACKUP_EXT
        
        if os.path.exists(filepath):
            print(f"\n{rel_path}:")
            
            if rel_path == 'frontend/categories.html':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'vue.global.js' in content:
                    print("  Status: Vue3 version")
                else:
                    print("  Status: Native JavaScript version")
            
            elif rel_path == 'frontend/css/style.css':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'tree-actions' in content:
                    print("  Status: Updated (contains Vue3 styles)")
                else:
                    print("  Status: Original version")
            
            elif rel_path == 'backend/migrate_to_mysql.py':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'MYSQL_RESERVED_WORDS' in content:
                    print("  Status: Fixed version")
                else:
                    print("  Status: Original version")
        else:
            print(f"\n{rel_path}: Not found")
        
        if os.path.exists(backup_path):
            print(f"  Backup: Exists")
        else:
            print(f"  Backup: Not found")

def main():
    print("=" * 60)
    print("JD Electronic Product Logistics System - Rollback Tool")
    print("=" * 60)
    print()
    print("1. Rollback categories.html to native JavaScript version")
    print("2. Rollback style.css to original version")
    print("3. Rollback migrate_to_mysql.py")
    print("4. Show current file status")
    print("5. Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-5): ")
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    if choice == '1':
        filepath = get_full_path('frontend/categories.html')
        success, message = rollback_file(filepath)
        print(message)
    
    elif choice == '2':
        filepath = get_full_path('frontend/css/style.css')
        success, message = rollback_file(filepath)
        print(message)
    
    elif choice == '3':
        filepath = get_full_path('backend/migrate_to_mysql.py')
        success, message = rollback_file(filepath)
        print(message)
    
    elif choice == '4':
        show_status()
    
    elif choice == '5':
        print("Exiting...")
    
    else:
        print("Invalid choice, please try again")

if __name__ == '__main__':
    main()