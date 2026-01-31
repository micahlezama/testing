python setup.py build_ext --inplace

for %%I in (launch_win.bat launch_unix.sh) do copy %%I .\dist\

cd src

for %%I in (auxil.py requirements.txt wps.ps1) do copy %%I ..\dist\src\

pause