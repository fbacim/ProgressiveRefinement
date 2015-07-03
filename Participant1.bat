@echo off
echo Participant 1, Raycasting
rem ABCD
echo    Starting abstract tutorial
Study3.1-abstract.py --participant 1 --technique 0 --mode 1
echo    Starting abstract
Study3.1-abstract.py --participant 1 --technique 0 --mode 0
echo    Starting supermarket, locations tutorial
Study3.2-supermarket.py --participant 1 --technique 0 --mode 3
echo    Starting supermarket, locations
Study3.2-supermarket.py --participant 1 --technique 0 --mode 0
echo    Starting supermarket, locations and navigation tutorial
Study3.2-supermarket.py --participant 1 --technique 0 --mode 3
echo    Starting supermarket, locations and navigation
Study3.2-supermarket.py --participant 1 --technique 0 --mode 1
echo    Starting supermarket, free navigation
Study3.2-supermarket.py --participant 1 --technique 0 --mode 2