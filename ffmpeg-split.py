#!/usr/bin/env python

import csv
import subprocess
import re
import math
import json
import os
from optparse import OptionParser


length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

def split_by_manifest(filename, manifest):
    if not os.path.exists(manifest):
        print "File does not exist: %s" % manifest
        raise SystemExit

    try:
        with open(manifest) as manifest_file:
            manifest_type = manifest.split(".")[-1]
            if manifest_type == "json":
                config = json.load(manifest_file)
            elif manifest_type == "csv":
                config = csv.DictReader(manifest_file)
            else:
                print "Format not supported. File must be a csv or json file"
                raise SystemExit

            split_cmd = "ffmpeg -i '"+filename+"' -vcodec copy "
            split_count = 1
            split_error = []
            try:
                fileext = filename.split(".")[-1]
            except IndexError as e:
                raise IndexError("No . in filename. Error: " + str(e))
            for video_config in config:
                split_str = ""
                try:
                    split_start = video_config["start_time"]
                    split_length = video_config.get("end_time", None)
                    if not split_length:
                        split_length = video_config["length"]
                    filebase = video_config["rename_to"]
                    if fileext in filebase:
                        filebase = ".".join(filebase.split(".")[:-1])

                    split_str += " -ss " + str(split_start) + " -t " + \
                        str(split_length) + \
                        " '"+ filebase + "." + fileext + \
                        "'"
                    print "About to run: "+split_cmd+split_str
                    output = subprocess.Popen(split_cmd+split_str,
                                              shell = True, stdout =
                                              subprocess.PIPE).stdout.read()
                except IndexError as e:
                    print "############# Incorrect format ##############"
                    print "The format of each json array should be:"
                    print "{start_time: <int>, length: <int>, rename_to: <string>}"
                    print "#############################################"
                    print e
                    raise SystemExit
    except Exception as e:
        print e
        raise SystemExit



def split_by_seconds(filename, split_length):
    if split_length and split_length <= 0:
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
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
    for n in range(0, split_count):
        split_str = ""
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n

        split_str += " -ss "+str(split_start)+" -t "+str(split_length) + \
                    " '"+filebase + "-" + str(n) + "." + fileext + \
                    "'"
        print "About to run: "+split_cmd+split_str
        output = subprocess.Popen(split_cmd+split_str, shell = True, stdout =
                               subprocess.PIPE).stdout.read()


def main():
    parser = OptionParser()

    parser.add_option("-f", "--file",
                        dest = "filename",
                        help = "File to split, for example sample.avi",
                        type = "string",
                        action = "store"
                        )
    parser.add_option("-s", "--split-size",
                        dest = "split_size",
                        help = "Split or chunk size in seconds, for example 10",
                        type = "int",
                        action = "store"
                        )
    parser.add_option("-m", "--manifest",
                      dest = "manifest",
                      help = "Split video based on a json manifest file. ",
                      type = "string",
                      action = "store"
                     )
    (options, args) = parser.parse_args()

    if options.filename and options.split_size:
        split_by_seconds(options.filename, options.split_size)
    elif options.filename and options.manifest:
        split_by_manifest(options.filename, options.manifest)
    else:
        parser.print_help()
        raise SystemExit

if __name__ == '__main__':

    try:
        main()
    except Exception, e:
        print "Exception occured running main():"
        print str(e)

