import subprocess
import os
import datetime

container_name = "timescaledb"
local_backup_dir = r"C:\Users\Revenant\Desktop\BD\backups"


def generate_backup_filename():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"backup_{timestamp}.tar"


def create_backup():
    backup_filename = generate_backup_filename()
    dump_command = [
    "docker", "exec", container_name,  
    "pg_dump", "-U", "postgres", "-d", "original", "-F", "t", "-f", backup_filename
    ]


    result = subprocess.run(dump_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Бэкап успешно скопирован:")

        if not os.path.exists(local_backup_dir):
            os.makedirs(local_backup_dir)
            print(f"Директория {local_backup_dir} создана.")

        

        command = [
        "docker", "cp",  
        f"{container_name}:/home/postgres/{backup_filename}", 
        local_backup_dir,
        ]

        #docker cp timescaledb:/home/postgres/backup_2025-02-12_22-16-34.tar "C:\Users\Revenant\Desktop\BD\backups"

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("всё чётко")

        command2 = [
        "docker", "exec", container_name,
        "sh", "-c", f"rm {backup_filename}"
        ]
        result2 = subprocess.run(command2, capture_output=True, text=True)
        if result2.returncode == 0:
            print("всё чётко2")

    else:
        print("Ошибка при копировании бэкапа:")

    
    
 
if __name__ == "__main__":
    create_backup();