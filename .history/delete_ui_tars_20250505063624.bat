@echo off
timeout /t 5 /nobreak
rd /s /q "C:\unbeknown\UI-TARS"
if exist "C:\unbeknown\UI-TARS" (
  echo Failed to delete UI-TARS folder > "C:\unbeknown\delete_failed.log"
) else (
  echo Successfully deleted UI-TARS folder > "C:\unbeknown\delete_success.log"
)
del "%~f0" 