#!/usr/bin/python3

import getopt
import re
import sys


def main(argv):
    # Get the input and output files from the command line args
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
        for opt, arg in opts:
            if opt == "-h":
                print("rb_convert.py -i <inputfile> -o <outputfile>")
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfile = arg
            elif opt in ("-o", "--ofile"):
                outputfile = arg
        # Convert the file
        convert_file(inputfile, outputfile)
    except (getopt.GetoptError, UnboundLocalError):
        print("Usage: rb_convert.py -i <inputfile> -o <outputfile>")
        sys.exit(2)


def convert_file(input_file, output_file):
    """Converts a Rekordbox-generated CUE file into something
    that other programs can read.

    Arguments:
        input_file {string} -- Path to the input file
        output_file {string} -- File to output
    """
    with open(input_file, "r") as input:
        with open(output_file, "w") as output:
            lines = input.readlines()
            for line_number, line in enumerate(lines):
                # The time string for a Rekordbox generated CUE file
                # is in HH:MM:SS. This needs to be converted into a
                # standard MM:SS:FF format so that other programs
                # can read it properly
                if "INDEX" in line:
                    # Convert the time
                    time = convert_time(line)
                    # Replace the old time with the new one
                    line = re.sub(
                        "([0-9][0-9]:[0-9][0-9]:[0-9][0-9])", time, line
                    )
                    output.write(line)
                # Rekordbox adds extra FILE references for each TRACK,
                # but only generates a single unsplit WAV file with
                # the recording. We only need to keep the first FILE
                # reference as that's the one that references the
                # WAV file it generates.
                elif "FILE" in line and line_number != 4:
                    pass
                # Write everything else straight to the output
                else:
                    output.write(line)


def convert_time(line):
    """Converts a HH:MM:SS timestamp into MM:SS:FF

    Arguments:
        line {string} -- Line from the CUE file
            containing the timestamp

    Returns:
        {string} -- New timestamp in MM:SS:FF format
    """
    # Search for the timestamp in the INDEX line
    timestamp = re.findall("([0-9][0-9]*)", line)
    # Delete the first match as this is the INDEX number
    del timestamp[0]
    # Convert the strings to ints so that they're easier to work with
    for index, string in enumerate(timestamp):
        timestamp[index] = int(string)
    # Create a list to store the new timestamp in
    new_timestamp = [0, 0, 0]
    # If the first part of the timestamp is 0 then just copy it across
    if timestamp[0] == 0:
        new_timestamp[0] = timestamp[1]
    # If the first part is higher than 0, convert the hour to minutes
    # and add it to the second figure
    elif timestamp[0] > 0:
        new_timestamp[0] = timestamp[1] + (timestamp[0] * 60)
    # Shift the third number across to the second column
    new_timestamp[1] = timestamp[2]
    # Always set the third column to 0
    new_timestamp[2] = 0
    # Loop through and convert each column back to a string
    # with a leading zero where needed
    for index, time in enumerate(new_timestamp):
        new_timestamp[index] = str(time).zfill(2)
    # Join the columns back together into a single
    # string with a ":" seperator
    new_timestamp = ":".join(new_timestamp)
    return new_timestamp


if __name__ == "__main__":
    main(sys.argv[1:])
