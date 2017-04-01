#!./bash
./get-pip.py
pip install BeautifulSoup
pip install psutil  
git clone -b master git://github.com/Diaoul/subliminal /tmp/subliminal
cd /tmp/subliminal /bin/python setup.py install 
