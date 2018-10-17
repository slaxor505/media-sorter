
# TODO: TEST! not working: dst and src argument mixed up and does not work dst
# DONE! TODO: TEST! locate avprobe dynamicaly
# NEED to check if date is valid. See JPG
# DONE! TODO: env screw up. "which" does not work under debug
#
#python3 do not execute script with arguments in shell
# TODO: [-r] remove original files  
# TODO: [ -f YYYY-MM-DD] 
# TODO: [-v] extra video files extension 
# TODO: [-i] extra image files extensions comma separated
# TODO: use video codec name for video folder
# TODO: logging facility

import exifread
import os
import sys
import shutil
import argparse
#import unicodedata
import string
import subprocess


# Script extracts original creation date from jpg and avi files,
# and then copy them to directories in accord with the date. Format YYYY-MM-DD

#Pre-requiesites: 
#For MacOSX and Linux avprobe
# MacOSX: brew install libav
# Ubuntu: sudo apt install libav-tools 
#For Windows: Python for Windows Extensions https://sourceforge.net/projects/pywin32/
# 
# usage:
# media-sorter.py [-c] [src_dir] [dst_dir]

# -c user first 20 character of Camera model as a top folder


def removeDisallowedFilenameChars(strValue):
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    #cleanedFilename = unicodedata.normalize('NFKD', strValue).encode('ASCII', 'ignore')
    return ''.join(c for c in strValue if c in validFilenameChars)
    
def parseArguments():
    argParser = argparse.ArgumentParser()
    
    argParser.add_argument("srcDir", nargs="?", help="Source media directory", default=os.getcwd())
    argParser.add_argument("dstDir", nargs="?", help="Destination media directory", default="_media_sorter_dir")
    argParser.add_argument('-c', '--camera-dir',action='store_true',
                         dest='camModel',
                         help='Use camera model name as top level directory')
    argParser.add_argument('-f', '--folder-name',action='store',
                         dest='folderFormat',default="YYYY-MM-DD",
                         help='Format of folder name')

    args = argParser.parse_args()

    return args


if __name__ == '__main__':
    
    if os.name=="posix":
        procVideo = shutil.which("avprobe")
        if procVideo==None:
            print("'Avprobe' executable not found. Video files will not be processed.")
        
    elif os.uname=="nt":
        
        try:
            from win32com.propsys import propsys, pscon
            procVideo="Windows"
        except:
            print("'Python for Windows Extensions' library is not installed. Video files will not be processed.")
            procVideo=None
    
    else:
        procVideo=None
        print('Not supported OS for Video files. Video files will not be processed.')
    

    cmdArgs = parseArguments()
    cameraDir=cmdArgs.camModel
    
    skipped = 0
    skipext = []
    
    baseDir = os.getcwd()
    
    #walk_dir = os.path.join(basedir,'pr1')
    #walk_dir = str('d:\works\\foto\!canon\!raw')
  
    #dst_dir = os.path.join(basedir,'pr1dst')
    #dst_dir = str('d:\\3')
    
    walk_dir = os.path.expanduser(cmdArgs.srcDir)
    if not os.path.isabs(walk_dir): walk_dir = os.path.join(baseDir,walk_dir)
        
    dst_dir = os.path.expanduser(cmdArgs.dstDir)
    if not os.path.isabs(dst_dir): dst_dir = os.path.join(baseDir,dst_dir)
    
    walk_dir=os.path.normpath(walk_dir)
    dst_dir=os.path.normpath(dst_dir)
     
    
#    if not os.access(dst_dir,os.W_OK):
    
    try:
        os.makedirs(dst_dir)
    except FileExistsError:
        if not os.access(dst_dir,os.W_OK):
            print('Error! Destination directory %s is not writable' % dst_dir)
    except:
        print('Error! Unable to create destination directory %s' % dst_dir)
        quit(False)
            
#    else:
            
#        print('Error! Destination directory %s is not writable or does not exist' % dst_dir)
#        quit(False)

    print('walk_dir = ' + walk_dir)
    print('dst_dir = ' + dst_dir)
    
    for root, subdirs, files in os.walk(walk_dir):
        print('--\nroot = ' + root)
    
        for subdir in subdirs:
            print('\t- subdirectory ' + subdir)
    
        for filename in files:
    
            file_path = os.path.join(root, filename)
            fname, fileext =  os.path.splitext(filename)
            fileext= fileext.lower()
            
            camModel="unknown_camera_model"
    
            if fileext.lower() == '.jpg' :
    
                print('\t- file %s ' % (filename))
    
                # Open image file for reading (binary mode)
                f = open(file_path, 'rb')
                # Return Exif tags
                tags = exifread.process_file(f,details=False, stop_tag='DateTimeOriginal')
                fdate = str(tags.get('EXIF DateTimeOriginal')).lstrip()
    
                #NEED to check if date is valid
                g = fdate.split(' ',1)
                dirname=removeDisallowedFilenameChars((g[0].replace(':','-')))
                
                if cameraDir :
                    camModel = removeDisallowedFilenameChars(str(tags.get('Image Model')).lstrip()[:20])

            elif (procVideo!=None) and ((fileext.lower() == '.avi') or (fileext.lower() == '.mp4')) :
    
                print('AVI!!!\t- file %s ' % (filename))
                
                if os.name=="posix":

                    #avOutput1 = subprocess.run(["which", "avprobe1"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #find out the actual path dynamically
                    
                    avOutput = subprocess.run(["/usr/local/bin/avprobe", "-show_format", "-of", "ini", file_path], stdout=subprocess.PIPE)
                    
                    if avOutput.returncode==0:
                        strOut = avOutput.stdout.decode()
                        strOut=strOut[strOut.find("creation_time"):]
                        strOut=strOut[:(strOut.find("\n"))]
                        strOut=strOut[strOut.find("=")+1:]
                        strOut=strOut[:strOut.find(" ")]
                        dirname = strOut
                    
                elif os.uname=="nt":
                    properties = propsys.SHGetPropertyStoreFromParsingName(file_path)
                    dt = str(properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue())
        
                    g = dt.split(' ',1)
                    dirname = g[0]
                else:
                    raise Exception("Unexpected OS to handle Video file")
    
            else:
    
                print ('SKIPPED: %s' % file_path)
                skipped +=1
                if not fileext in skipext:
                    skipext.append(fileext)
                continue
     
            if cameraDir :
                dirname = os.path.join(camModel, dirname)

            dstpath = os.path.join(dst_dir, dirname)            
            
            try:
            
                if not os.path.exists(dstpath) :
                    
                    print('Creating dir: %s' % dstpath)
                    os.makedirs(dstpath)
    
            except:
                
                print('Error! Unable to create directories along %s' % dstpath)
                quit()
    
            print('Copying to: %s' % dstpath)
            shutil.copy2(file_path, dstpath)
    
    
    print('Skipped: '+str(skipped))
    print (skipext)
    print('Complete.')
