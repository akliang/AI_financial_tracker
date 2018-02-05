
import csv

with open('test.csv','rb') as f:
  reader = csv.reader(f)
  line_items = list(reader)

# first row is the header
headers=line_items[0]
del line_items[0]

headers=[k.lower() for k in headers]
line_items=[[k.lower() for k in i] for i in line_items]

print headers
print line_items

