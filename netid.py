import csv
import os

f = open('netids.raw', 'r')
if os.path.exists('netids.txt'):
    os.remove('netids.txt')
fo = open('netids.txt', 'w+')

for line in f:
    for id in line.strip().split():
        fo.write(id+'\n')

f.close()
fo.close()
