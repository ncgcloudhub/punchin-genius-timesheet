DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': 'timetracker_db',
'USER': 'postgres',
'PASSWORD': 'P0stgresadmin23!',
'HOST': 'localhost',
'PORT': '5432',
}
}

---

==================================
Automating with Scripts
You can also run these commands from a shell script or directly by passing them to the psql command using the -c flag. For example:

bash
Copy code

# psql -U username -d databasename -c "CREATE DATABASE mynewdatabase;"

# Make sure you are using these commands wisely and understand the implications, especially when dropping databases, as this can lead to irreversible data loss. Always ensure you have recent backups of any important data.

=================================

time_tracker secrets:
db name: timetracker_db

django db:
super user: saiful / admin (changed to use email address)
trionxai@gmail.com
pw: T!metracker23!

---

db root directory: C:\Program Files\PostgreSQL\16\data
postgre database user user:
user: postgres
pw: P0stgresadmin23!
port: 5432

---

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'stritstax.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'no-reply@stritstax.com'
EMAIL_HOST_PASSWORD = 'T!metracker@Punchin23!'

---

email: trionxai@gmail.com
google app pw: ltmv kigw akdh afki

--
Installation Directory: C:\Program Files\PostgreSQL\16
Server Installation Directory: C:\Program Files\PostgreSQL\16
Data Directory: C:\Program Files\PostgreSQL\16\data
Database Port: 5432
Database Superuser: postgres
Operating System Account: NT AUTHORITY\NetworkService
Database Service: postgresql-x64-16
Command Line Tools Installation Directory: C:\Program Files\PostgreSQL\16
pgAdmin4 Installation Directory: C:\Program Files\PostgreSQL\16\pgAdmin 4
Stack Builder Installation Directory: C:\Program Files\PostgreSQL\16
Installation Log: C:\Users\saiful\AppData\Local\Temp\install-postgresql.log
