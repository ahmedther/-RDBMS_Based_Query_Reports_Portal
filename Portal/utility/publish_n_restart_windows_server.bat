runas /user:itapps@KDAHIT.COM /savecred "%~dp0%~nx0"

xcopy "\\10.72.176.37\d$\Python Projects\report_portal\Scripts\Portal" "C:\AhmedWebsites\report_portal\Scripts\Portal" /s /d /y 

forfiles /p "C:\AhmedWebsites\report_portal\Scripts\Portal" /m *.* /c "cmd /c if not exist \"\\10.72.176.37\d$\Python Projects\report_portal\Scripts\Portal\@file\" del @path"

NET STOP Query_Report_Portal
NET STOP "UHID Card Generator Website"
NET STOP nginx
NET START Query_Report_Portal
NET START "UHID Card Generator Website"
NET START nginx

del /Q C:\AhmedWebsites\report_portal\Scripts\Portal\web_excel_files\*


echo %date% - Service Restarted Successfully >>"C:\AhmedWebsites\report_portal\Scripts\restart.log"

@REM pause


@REM import winrm

@REM # Connection to WinRM
@REM session = winrm.Session('10.72.176.37', auth=('itapps@KDAHIT.COM', 'password'))

@REM # XCOPY command
@REM session.run_cmd('xcopy', [
@REM     '\\\\10.72.176.37\\d$\\Python Projects\\report_portal\\Scripts\\Portal',
@REM     'C:\\AhmedWebsites\\report_portal\\Scripts\\Portal',
@REM     '/s', '/d', '/y'
@REM ])

@REM # FORFILES command
@REM session.run_cmd('forfiles', [
@REM     '/p', 'C:\\AhmedWebsites\\report_portal\\Scripts\\Portal',
@REM     '/m', '*.*',
@REM     '/c', 'cmd /c if not exist \\\\10.72.176.37\\d$\\Python Projects\\report_portal\\Scripts\\Portal\\@file del @path'
@REM ])

@REM # NET STOP and NET START commands
@REM session.run_cmd('net', ['stop', 'Query_Report_Portal'])
@REM session.run_cmd('net', ['stop', '"UHID Card Generator Website"'])
@REM session.run_cmd('net', ['stop', 'nginx'])
@REM session.run_cmd('net', ['start', 'Query_Report_Portal'])
@REM session.run_cmd('net', ['start', '"UHID Card Generator Website"'])
@REM session.run_cmd('net', ['start', 'nginx'])

@REM # DEL command
@REM session.run_cmd('del', ['/Q', 'C:\\AhmedWebsites\\report_portal\\Scripts\\Portal\\web_excel_files\\*'])

@REM # ECHO command
@REM session.run_cmd('echo', [f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Service Restarted Successfully >> C:\\AhmedWebsites\\report_portal\\Scripts\\restart.log"])