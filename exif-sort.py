import exifread
import os
import sys
import shutil
from win32com.propsys import propsys, pscon

# Script creates extract original creation date from jpg and avi files,
# and then copy them to directories in accord with the date. Format YYYY-MM-DD

skipped = 0
skipext = []

basedir = os.getcwd()

walk_dir = os.path.join(basedir,'pr1')
#walk_dir = str('d:\works\\foto\!canon\!raw')

dst_dir = os.path.join(basedir,'pr1dst')
#dst_dir = str('d:\\3')

print('walk_dir = ' + walk_dir)

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)

    for subdir in subdirs:
        print('\t- subdirectory ' + subdir)

    for filename in files:

        file_path = os.path.join(root, filename)
        fname, fileext =  os.path.splitext(filename)
        fileext= fileext.lower()
        

        #if fileext.lower() in ['.jpg','.avi'] :
        if fileext.lower() == '.jpg' :

            print('\t- file %s ' % (filename))

            # Open image file for reading (binary mode)
            f = open(file_path, 'rb')

            # Return Exif tags
            tags = exifread.process_file(f,details=False, stop_tag='DateTimeOriginal')

            fdate = str(tags.get('EXIF DateTimeOriginal')).lstrip()

            #NEED to check if date is valid

            g = fdate.split(' ',1)
            dirname=(g[0].replace(':','-'))

        elif fileext.lower() == '.avi' :

            print('AVI!!!\t- file %s ' % (filename))

            properties = propsys.SHGetPropertyStoreFromParsingName(file_path)
            dt = str(properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue())

            g = dt.split(' ',1)
            dirname = g[0]

        else :

            print ('SKIPPED: %s' % file_path)
            skipped +=1
            if not fileext in skipext:
                skipext.append(fileext)
            continue
 
        dstpath = os.path.join(dst_dir, dirname)
        if not os.path.exists(dstpath) :
            
            print('Creating dir: %s' % dstpath)
            os.makedirs(dstpath)

        print('Copying to: %s' % dstpath)
        shutil.copy2(file_path, dstpath)


print('Skipped: '+str(skipped))
print (skipext)
print('Complete.')

