# ISPConfigBackup
A simple python script for backup all sites and databases for ISPConfig

# Requirements
Python 2

# How to use
Just edit the config in the main file, the `BACKUP_DIR` MUST be an absolute path.

```
#######--CONFIG--#######
DB_USER = 'root'
DB_PASSWORD = 'root'
BACKUP_DIR = '/root'
########################
```

And finally launch it from console:

```shell
python ISPConfigBackup.py
```
