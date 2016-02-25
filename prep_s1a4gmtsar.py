# -*- coding: utf-8 -*-
__author__ = "Antoine Lucas"
__copyright__ = "Copyright 2016, Antoine Lucas"
__license__ = "CeCILL"
__version__ = "0.0.1"
__email__ = "dralucas@astrogeophysx.net"
__status__ = "Prototype"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Preparing S1A data for GMTSAR package
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, sys
import subprocess, fnmatch
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
os.system('clear')
debug=True # debugging mode
align_tops="/usr/local/GMT5SAR/bin/align_tops.csh"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "Preparing S1A data for GMTSAR package"
print "-------------------------------------"
print " "
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if debug: 
    print "!!! WARNING: Running in debugging mode, nothing but potential errors/warning will occur"  
    print " "
    
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print sys.argv[0]," usage:"
    print "  ",sys.argv[0]," demfile.grd s1afile1 s1afile2 [subswath_number {1,2,3}]"
    print "   if no subswath number is given, all of them (three) will be treated,"
    print "   this value must be either 1, 2 or 3."
    sys.exit(" ")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
n_img = 2  # Number of images are always equal 2
n_sw = 3   # Number of subswath = 3, this is easy to adjust if needed

if len(sys.argv) == 5:
    iwnum=sys.argv[4]
    n_sw = 1  #if one swath is specified we squeeze the structures to one
    
# We create structures that will contain the filenames we need later on    
S1Aswath = [ ([0] * n_sw) for nimg in range(n_img) ]
S1Aoef = [ ([0] * 1) for nimg in range(n_img) ]


print " 1/ Creating RAW directory"
cmd="mkdir raw"
if debug:
    print " debug mode:", cmd
    print " "
else:
    out = subprocess.check_output(cmd, shell=True);
        
demfile=str(sys.argv[1])
cmd="ln -sr " + str(demfile) + " ./raw/"
if debug:
    print " debug mode:", cmd
    print " "
else:
    out = subprocess.check_output(cmd, shell=True);
        
ii=0 # we initiate ii counter for the first image

print " 2/ linking tiff/xml into RAW directory for:"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for img in sys.argv[2:4]:
    print "    ", img

    if len(sys.argv)==4:  
        cmd="ln -sr ./" + img + ".SAFE/annotation/s1a*.xml ./raw/"
        S1Aswath[ii][:]=fnmatch.filter(os.listdir("./"+img+".SAFE/annotation/"),'s1a*-vv-*.xml')
      
    else:
        cmd="ln -sr ./" + img + ".SAFE/annotation/s1a-iw" + str(iwnum) + "*-vv-*.xml ./raw/"
        S1Aswath[ii][:]=fnmatch.filter(os.listdir("./"+img+".SAFE/annotation/"),"s1a-iw" + str(iwnum) + "*-vv-*.xml")

  
    if debug:
        print " debug mode:", cmd
        #print " debug mode:", S1Aswath
        print " "

    else:
        out = subprocess.check_output(cmd, shell=True)
       
    if len(sys.argv)==4:
        cmd="ln -sr ./" + img + ".SAFE/measurement/s1a*.tiff  ./raw/"
    else:
        cmd="ln -sr ./" + img + ".SAFE/measurement/s1a-iw" + str(iwnum) + "*-vv-*.tiff ./raw/"
        
    if debug:
        print " debug mode:", cmd
        print " "
    else:
        out = subprocess.check_output(cmd, shell=True)
    
    # we parse the EOF filename so we can find the one we need
    iT=img.index("T")
    iT1=img.rindex("T")
    date=img[iT-8:iT]
    timemin=img[iT+1:iT+7]
    timemax=img[iT1+1:iT1+7]
    findeof=False
    for eoffile in os.listdir("./"):
        if eoffile.endswith(".EOF"):
            
                
            iV=eoffile.index("V")
            iT2=eoffile.rindex("T")
            
            tmax=int(eoffile[iT2-8:iT2]+eoffile[iT2+1:iT2+7])
            tmin=int(eoffile[iV+1:iV+9]+eoffile[iV+10:iV+16])
            if int(date+timemin) >= tmin and int(date+timemax) <= tmax:
                print "     with its orb file:", eoffile
                cmd="ln -sr " + eoffile + " ./raw/"
                S1Aoef[ii]=eoffile
                findeof=True
                if debug:
                    print " debug mode:", cmd
                    #print cmd
                    #print S1Aoef
                    print " "
                else:
                    out = subprocess.check_output(cmd, shell=True)
                    
      
    if not findeof:
        sys.exit("ERROR !!!! EOF file is missing for " + img) 
                
    ii=ii+1 #iterate on images
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print " 3/ Preprocessing subswaths"

for ii in range(0,n_sw):
    if len(sys.argv)==4:  
        print "      Subswath #:", str(ii+1)
    else:
        print "      Subswath #:", str(iwnum)
    
    img1name = S1Aswath[0][ii][:-4]
    img2name = S1Aswath[1][ii][:-4]
    eof1name = S1Aoef[0]
    eof2name = S1Aoef[1]
    if demfile.rfind('/'):
        demfile=demfile[demfile.rfind('/')+1:]
    
    cmd =  align_tops + "  ./raw/" + img1name + "  ./raw/" + eof1name + " ./raw/" + img2name + "  ./raw/" + eof2name + "  ./raw/" + demfile 
    
    
    
    if debug:
        print " debug mode:", cmd

    else:
        out = subprocess.check_output(cmd, shell=True)
        
        
    if len(sys.argv)==4:  
        cmd="mkdir F" + str(ii+1)
    else: 
        cmd="mkdir F" + str(iwnum)
        
        
    if debug:
        print " debug mode:", cmd

    else:
        out = subprocess.check_output(cmd, shell=True)    
    
    
    if len(sys.argv)==4:  
        cmd="mkdir F" + str(ii+1) + "/raw"
        cmd2="ln -sr config.s1a.txt ./F" + str(ii+1) + "/"
        cmd3="ln -sr ./raw/*F" + str(ii+1) + "* ./F" + str(ii+1) + "/raw/"
    else: 
        cmd="mkdir F" + str(iwnum) + "/raw"
        cmd2="ln -sr config.s1a.txt ./F" + str(iwnum) + "/"  
        cmd3="ln -sr ./raw/*F" + str(iwnum) + "* ./F" + str(iwnum) + "/raw/"
        
    if debug:
        print " debug mode:", cmd
        print " debug mode:", cmd2
        print " debug mode:", cmd3
        
    else:
        out = subprocess.check_output(cmd, shell=True)    
        out = subprocess.check_output(cmd2, shell=True)   
        out = subprocess.check_output(cmd3, shell=True) 
