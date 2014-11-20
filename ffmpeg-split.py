#!/usr/bin/env python

import subprocess
import re
import math
from optparse import OptionParser


length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

def main():

    (filename, split_length) = parse_options()
    if split_length <= 0:
        print "Split length can't be 0"
        raise SystemExit

    output = subprocess.Popen("ffmpeg -i '"+filename+"' 2>&1 | grep 'Duration'", 
                            shell = True,
                            stdout = subprocess.PIPE
                            ).stdout.read()
    print output
    matches = re_length.search(output)
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                        int(matches.group(2)) * 60 + \
                        int(matches.group(3))
        print "Video length in seconds: "+str(video_length)
    else:
        print "Can't determine video length."
        raise SystemExit

    split_count = int(math.ceil(video_length/float(split_length)))
    if(split_count == 1):
        print "Video length is less then the target split length."
        raise SystemExit

    split_cmd = "ffmpeg -i '"+filename+"' -vcodec copy "
    for n in range(0, split_count):
        split_str = ""
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n
        
        split_str += " -ss "+str(split_start)+" -t "+str(split_length) + \
                    " '"+filename[:-4] + "-" + str(n) + "." + filename[-3:] + \
                    "'"
        print "About to run: "+split_cmd+split_str
        output = subprocess.Popen(split_cmd+split_str, shell = True, stdout =
                               subprocess.PIPE).stdout.read()


def parse_options():
    parser = OptionParser()    
    
    parser.add_option("-f", "--file",
                        dest = "filename",
                        help = "file to split, for example sample.avi",
                        type = "string",
                        action = "store"
                        )
    parser.add_option("-s", "--split-size",
                        dest = "split_size",
                        help = "split or chunk size in seconds, for example 10",
                        type = "int",
                        action = "store"
                        )
    (options, args) = parser.parse_args()
    
    if options.filename and options.split_size:

        return (options.filename, options.split_size)

    else:
        parser.print_help()
        raise SystemExit

if __name__ == '__main__':

    try: 
        main()
    except Exception, e:
        print "Exception occured running main():"
        print str(e)

