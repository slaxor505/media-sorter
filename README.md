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

# -c use first 20 character of Camera model as a top folder
