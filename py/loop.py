'''
Created on 2017/05/04

@author: go
'''

csv_text = u"""smokey,Linux 3.0-ARCH,x86
12345678901,12345 1234567890123,123
12345678901,1234567890123456789,12345
11 bytes,19 bytes,5 byt
test line:,"Some \"\"comma, quote\"\"",foo
skylight,Linux 3.0-ARCH,x86
polaris,Linux 3.0-ARCH,amd64
asgard,Windows 6.1.7600,amd64
galileo,Windows 6.2.8102,x86
kepler,Windows 6.2.8123,amd64
wrfbox,Windows 6.2.8133,amd64
"""

import argparse
import csv
import io

import six

"""
parser = argparse.ArgumentParser()
parser.add_argument("csv_file_path")
parser.add_argument("--encoding", default="utf_8")
options = parser.parse_args()
"""

csv_reader = csv.reader(
    io.open("sample.csv", "r", encoding="utf-8"),
    delimiter=",",
    quotechar='"'
)

print("--- header ---\n{}\n".format(six.next(csv_reader)))
print("--- data ---")
for row in csv_reader:
    print(row)
