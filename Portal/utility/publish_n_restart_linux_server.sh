#!/bin/bash
echo -e  "Trying to Copy Portal FIles\n"
echo "ahmed" |sudo -S sshpass -p 'Whatt1@1' rsync -avzr --chmod=777 --progress --delete -e ssh 51003720@10.72.176.37:"'/cygdrive/d/Python Projects/report_portal/Scripts/Portal'" "/home/ahmed/Desktop/AHMED/Django_Websites/reports_portal/"
echo -e "Copying Files Don\n"

echo -e "Don Z - Killing Begins\n"
sudo -S pkill nginx
sudo -S pkill apache2
sudo -S pkill postgres
sudo -S pkill RDBMS_Query_Reports_Portal_gunicorn.service

echo -e "JoyBoy\n"
sudo -S systemctl stop nginx
sudo -S systemctl stop RDBMS_Query_Reports_Portal_gunicorn.service

echo -e "\nRED X - Stating Services\n"
sudo -S systemctl start nginx
sudo -S systemctl start RDBMS_Query_Reports_Portal_gunicorn.service

echo -e "Gonz Key\n"
sudo -S service apache2 restart
sudo -S service postgresql start

echo -e "Deleting ALL files in web_exel_files"
sudo -S rm -rf /home/ahmed/Desktop/AHMED/Django_Websites/reports_portal/Portal/web_excel_files/*

echo -e "Dont have a good day! Have a great day!!!\n"

# import paramiko
# import os

# # Connect to the remote host
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect('10.72.176.37', username='51003720', password='Whatt1@1')

# # Execute the remote commands
# commands = [
#     "rsync -avzr --chmod=777 --progress --delete -e ssh 51003720@10.72.176.37:/cygdrive/d/Python Projects/report_portal/Scripts/Portal /home/ahmed/Desktop/AHMED/Django_Websites/reports_portal/",
#     "pkill nginx",
#     "pkill apache2",
#     "pkill postgres",
#     "pkill RDBMS_Query_Reports_Portal_gunicorn.service",
#     "systemctl stop nginx",
#     "systemctl stop RDBMS_Query_Reports_Portal_gunicorn.service",
#     "systemctl start nginx",
#     "systemctl start RDBMS_Query_Reports_Portal_gunicorn.service",
#     "service apache2 restart",
#     "service postgresql start",
#     "rm -rf /home/ahmed/Desktop/AHMED/Django_Websites/reports_portal/Portal/web_excel_files/*"
# ]

# for command in commands:
#     stdin, stdout, stderr = ssh.exec_command(f"echo 'ahmed' | sudo -S {command}")
#     print(stdout.read().decode())
#     print(stderr.read().decode())

# # Close the connection
# ssh.close()

