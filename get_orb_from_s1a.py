# -*- coding: utf-8 -*-
__author__ = "Antoine Lucas"
__copyright__ = "Copyright 2016, Antoine Lucas"
__license__ = "CeCILL"
__version__ = "0.0.1"
__email__ = "dralucas@astrogeophysx.net"
__status__ = "Prototype"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# download S1A orbits from https://www.unavco.org/data/imaging/sar/lts1/winsar/s1qc/aux_poeorb/
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os,sys
from bs4 import BeautifulSoup
import requests

os.system('clear')
url="https://www.unavco.org/data/imaging/sar/lts1/winsar/s1qc/aux_poeorb"
ext="EOF"

for img in sys.argv[1:]: 
    print "    Get orbit for", img
    iT=img.index("T")
    iT1=img.rindex("T")
    date=img[iT-8:iT]
    timemin=img[iT+1:iT+7]
    timemax=img[iT1+1:iT1+7]
    print "      > Acquisition date is", date, "in the time range of",timemin,"/",timemax


def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

for remotefile in listFD(url, ext):
    iV=remotefile.index("V")
    iT2=remotefile.rindex("T")
    islash = remotefile.rindex("/")
    eofname=remotefile[islash+1:]
    tmax=int(remotefile[iT2-8:iT2]+remotefile[iT2+1:iT2+7])
    tmin=int(remotefile[iV+1:iV+9]+remotefile[iV+10:iV+16])
    
    
    if int(date+timemin) >= tmin and int(date+timemax) <= tmax:
        print "      > Orbit file:", eofname
        import urllib2


        file_name = remotefile.split('/')[-1]
        u = urllib2.urlopen(remotefile)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        
        while True:
          buffer = u.read(block_sz)
          if not buffer:
            break

          file_size_dl += len(buffer)
          f.write(buffer)
          status = r"  [%3.2f%%]" % (file_size_dl * 100. / file_size)
          print status,

        f.close()

