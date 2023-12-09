import subprocess
import os
from datetime import datetime

# Set the PGPASSWORD environment variable
os.environ['PGPASSWORD'] = 'P0stgresadmin23!'

# Define the command
command = '"C:/Program Files/PostgreSQL/16/bin/pg_dump.exe" -U postgres -h localhost -p 5432 -d timetracker_db'

# Define the backup file name
backup_file_name = f'timetracker_db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'

# Define the full path for the backup file
backup_file_path = os.path.join('E:/Github/orgs/ncgcloudhub/punchin-genius-timesheet/dev/time_tracker/backup_db/', backup_file_name)

# Run the command and write the output to the backup file
with open(backup_file_path, 'w') as f:
    subprocess.run(command, shell=True, stdout=f)