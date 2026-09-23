@echo off
:: ===================================================================
::  size_match_demo.bat  —  BENIGN Windows reproduction of the
::  campaign's size-match cache carve (Cybervoid Saga, Appendix E).
::
::  It mirrors the real one-liner's SELECTION logic exactly:
::      for /r <dir> %%f in (f_*) do @if %%~zf==<size> copy ...
::  ...but against a fake local cache of harmless files, and it
::  PRINTS the match instead of executing it. No network. No malware.
::
::  Run in a scratch folder:  size_match_demo.bat
:: ===================================================================
setlocal enabledelayedexpansion
set "ROOT=%TEMP%\cybervoid_sizedemo"
set "TARGET=17635"

:: ---- seed a fake cache with decoys + one exact-size "payload" ----
rmdir /s /q "%ROOT%" 2>nul
mkdir "%ROOT%\Cache_Data" 2>nul
call :mkfile "%ROOT%\Cache_Data\f_000000" 2048
call :mkfile "%ROOT%\Cache_Data\f_000001" 17634
call :mkfile "%ROOT%\Cache_Data\f_000002" 17636
call :mkfile "%ROOT%\Cache_Data\f_000583" %TARGET%   :: <-- the exact match

echo [demo] seeded fake cache at %ROOT%\Cache_Data
echo [demo] searching for f_* whose size == %TARGET% ...

:: ---- the SELECTION-BY-SIZE carve (execution intentionally omitted) ----
for /r "%ROOT%\Cache_Data" %%f in (f_*) do @if %%~zf==%TARGET% (
    echo [demo] MATCH: %%~nxf  is exactly %%~zf bytes
    copy "%%f" "%ROOT%\t.bat" >nul
    echo [demo] copied match to %ROOT%\t.bat  ^(stands in for %%TEMP%%\t.bat^)
    echo [demo] the REAL command would now run t.bat -- this demo does NOT.
)

echo [demo] done. No download, no execution. Selection was by SIZE alone.
rmdir /s /q "%ROOT%" 2>nul
goto :eof

:mkfile
:: :mkfile <path> <bytes>  — create a file of an exact byte length (benign 'A's)
setlocal
set "P=%~1" & set /a N=%~2
fsutil file createnew "%P%" %N% >nul 2>nul || (
    powershell -NoP -C "[IO.File]::WriteAllBytes('%P%', (New-Object byte[] %N%))"
)
endlocal & goto :eof
