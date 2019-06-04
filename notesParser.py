import os
import re









_keywords_ = ['Transport', 'Start', 'Run', '', 'Potential Total', 'Potential Matched', 'Actual Total' , 'Actual Moved',  'Actual Timeouts', 'Actual Timeouts Inc', 'Late', 'Errors']

date = "13-11-2017"
x = bool(re.match("^([1-9] |1[0-9]| 2[0-9]|3[0-1])(.|-)([1-9] |1[0-2])(.|-|)20[0-9][0-9]$",date))

print x

f = open('test.txt', 'w')
print f.write("Fuck")
f = open('C:\\Users\\ccole\\Documents\\Playground\\python_project\\log_extractor\\testNotes.txt', 'r')
print f.read()

