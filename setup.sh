#!./bash
./get-pip.py
pip install BeautifulSoup
pip install psutil  
git clone -b master https://github.com/Diaoul/subliminal /tmp/subliminal
cd /tmp/subliminal /bin/python setup.py install 
