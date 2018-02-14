import csv
import numpy as np
import cv2

# file.__doc__

# file(name[, mode[, buffering]]) -> file object  
# Open a file.
  
# The mode can be 'r', 'w' or 'a' for reading (default),\nwriting or appending.  
# The file will be created if it doesn't exist when opened for writing or appending; 
# it will be truncated when opened for writing.  Add a 'b' to the mode for binary files.
 
# Add a '+' to the mode to allow simultaneous reading and writing. 
# If the buffering argument is given, 0 means unbuffered, 1 means line buffered, and larger numbers specify the buffer size.  
# The preferred way to open a file is with the builtin open() function. 
# Add a 'U' to mode to open the file for input with universal newline support.  
# Any line ending in the input file will be seen as a '\\n' in Python.  
# Also, a file so opened gains the attribute 'newlines'; 
# the value for this attribute is one of None (no newline read yet), '\\r', '\\n', '\\r\\n' or a tuple containing all the newline types seen.  
# 'U' cannot be combined with 'w' or '+' mode. "

filename = 'C:/Users/dsinger/Documents/Visual Studio 2015/Projects/Masterthesis/files/simple.csv'
filename = 'simpler.csv'

# Here I create a simple .csv file with some entries.
with open(filename, 'wb') as csvfile:
    print 'File open.'
    writer = csv.writer(csvfile, delimiter = ',')
    data = [['Stock', 'Sales'],
            ['1000', '24'],
            ['120', '33'],
            ['23', '5']]
    writer.writerows(data)

# Now I open it again (in read mode) to look at it only and print its values.
with open(filename, 'rb') as csvfile:
    print 'File open.'
    reader = csv.reader(csvfile, delimiter = ',')
    print 'Reader open.'
    for row in reader:
        print row