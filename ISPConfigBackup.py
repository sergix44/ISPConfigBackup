from time import gmtime, strftime
import os
import tempfile
import shutil
import subprocess

#######--CONFIG--#######
DB_USER = 'root'
DB_PASSWORD = 'root'
BACKUP_DIR = '/root'
########################

temp_folder = tempfile.mkdtemp(prefix='pyISPCbackup')
temp_folder_databases = '/databases/'
temp_folder_sites = '/sites/'

print(' * Fetching databases...')
databases = subprocess.check_output('mysql --user=' + DB_USER + ' --password=' + DB_PASSWORD + ' -e "SHOW DATABASES;" | tr -d "| " | grep -v Database', shell=True).split('\n')
databases = [x for x in databases if x]

print(' * Creating folders...')
os.mkdir(temp_folder + temp_folder_databases)
os.mkdir(temp_folder + temp_folder_sites)

print('-- Backup databases')
for db in databases:
    if db[0] == 'c':
        print(' * Saving ' + db + '...')
        os.system('mysqldump --user=' + DB_USER + ' --password=' + DB_PASSWORD + ' ' + db + ' > ' + temp_folder + temp_folder_databases + db + '.sql')

print('-- Backup sites')
sites = subprocess.check_output('ls /var/www/ | grep "\."', shell=True).split('\n')
sites = [x for x in sites if x]
for site in sites:
    if site.count('.') >= 2:
        continue
    print(' * Saving ' + site + '...')
    os.system('cp -Lr /var/www/' + site + ' ' + temp_folder + temp_folder_sites + site + '/')
    if os.path.isdir(temp_folder + temp_folder_sites + site + '/backup'):
        print(' * Removing old ' + site + ' saved backups...')
        shutil.rmtree(temp_folder + temp_folder_sites + site + '/backup')
    if os.path.isdir(temp_folder + temp_folder_sites + site + '/log'):
        print(' * Removing ' + site + ' logs...')
        shutil.rmtree(temp_folder + temp_folder_sites + site + '/log')

print('-- Compressing...')
os.system('cd ' + temp_folder + ' && tar -zcf ' + BACKUP_DIR + '/ispconfig_' + strftime("%d-%m-%Y_%H:%M:%S", gmtime()) + '.tar.gz *')

print(' * Removing temp files...')
shutil.rmtree(temp_folder)
print('-- Done.')
