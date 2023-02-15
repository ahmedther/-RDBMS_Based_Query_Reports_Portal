@REM The -m option in plink is used to specify a file containing a list of commands to run on the remote server once the connection has been established.
@REM The -t option in plink is used to force plink to open a terminal on the remote server and run the commands as if you were typing them interactively.




plink -ssh ahmed@172.20.100.81 -pw ahmed -batch -v -m "D:\Python Projects\report_portal\Scripts\Portal\utility\publish_n_restart_linux_server.sh 
plink -ssh itapps@172.20.200.40 -pw Kh@123457 -batch -v "C:\AhmedWebsites\report_portal\Scripts\Portal\utility\publish_n_restart_windows_server.bat"




pause
