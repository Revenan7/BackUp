import subprocess
import os
import psycopg2

# Константы
DOCKER_CONTAINER_NAME = "timescaledb" 
LOCAL_BACKUP_DIR = r"C:\Users\Revenant\Desktop\BD\backups" 
DB_NAME = "clone"
DB_USER = "postgres"
DB_HOST = "host.docker.internal"  
DB_PASSWORD = "123456" 


def restore_backup():
    if not os.path.exists(LOCAL_BACKUP_DIR):
        print(f"Директория {LOCAL_BACKUP_DIR} не существует.")
        return
    
    backup_files = [f for f in os.listdir(LOCAL_BACKUP_DIR) if f.endswith(".tar")]
    if not backup_files:
        print("Нет доступных бэкапов в директории.")
        return
    

    first_backup = backup_files[0]
    local_backup_path = os.path.join(LOCAL_BACKUP_DIR, first_backup)
    


    command = [
        "docker", "cp",  
        f"{LOCAL_BACKUP_DIR}/{first_backup}",
        f"{DOCKER_CONTAINER_NAME}:/home/postgres/{first_backup}"
    ]

        #docker cp timescaledb:/home/postgres/backup_2025-02-12_22-16-34.tar "C:\Users\Revenant\Desktop\BD\backups"

    result = subprocess.run(command, capture_output=True, text=True)
    if result == 0:
        command2 = [
        "docker", "exec", DOCKER_CONTAINER_NAME,
        "sh", "-c", f"rm -f {first_backup}"
        ]
        result2 = subprocess.run(command2, capture_output=True, text=True)
        if result2 == 0:
            print("удалил .tar")
    restore_command = [
        "docker", "exec", "-i", DOCKER_CONTAINER_NAME,
        "pg_restore", "-U", DB_USER, "-d", DB_NAME
    ]
    
    try:
        with open(local_backup_path, "rb") as backup_file:
            result = subprocess.run(
                restore_command,
                input=backup_file.read(),
                capture_output=True,
                text=False
            )
        
        if result.returncode != 0:
            print("Ошибка при восстановлении бэкапа:", result.stderr.decode("utf-8").strip())
        else:
            print(f"Бэкап {first_backup} успешно восстановлен.")
    except Exception as e:
        print("Ошибка при выполнении pg_restore:", str(e))




import psycopg2

def add_foreign_keys():
    connection_string = "postgresql://postgres:123456@host.docker.internal:5440/clone"
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                """)
                tables = [row[0] for row in cursor.fetchall()]
                

                tables_to_process = [table for table in tables if table != "device"]
                

                hypertable_name = "registers" 
                if hypertable_name in tables_to_process:
                    cursor.execute(f"""
                        SELECT show_chunks('{hypertable_name}');
                    """)
                    chunks = cursor.fetchall()
                    for chunk in chunks:
                        chunk_name = chunk[0]
                        if chunk_name and chunk_name not in tables_to_process:
                            tables_to_process.append(chunk_name)
                

                for table in tables_to_process:
                    print(f"Обработка таблицы: {table}")
                    try:

                        

                        cursor.execute("""
                            SELECT constraint_name
                            FROM information_schema.key_column_usage
                            WHERE table_name = %s AND column_name = 'ip_device';
                        """, (table.split('.')[-1],)) 

                        constraint_name = f"fk_{table.replace('.', '_')}_ip_device"
                            

                        escaped_table_name = f'"{table}"' if '.' in table else table
                            
                            # Добавляем внешний ключ
                        cursor.execute(f"""
                                ALTER TABLE {escaped_table_name}
                                ADD CONSTRAINT {constraint_name}
                                FOREIGN KEY (ip_device) REFERENCES device(ip_adress);
                            """)

                       
                        

                        conn.commit()
                    except Exception as e:

                        conn.rollback()
                        print(f"Ошибка при обработке таблицы {table}: {e}")
                
    except Exception as e:
        print("Ошибка подключения к базе данных:", e)

if __name__ == "__main__":
    print("Шаг 1: Восстановление бэкапа...")
    restore_backup()
    
    print("\nШаг 2: Добавление внешних ключей...")
    add_foreign_keys()
    
    print("Скрипт завершён.")