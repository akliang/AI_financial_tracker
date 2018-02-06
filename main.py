
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

import csv
from tinydb import TinyDB,where,Query
from tinydb.operations import add,set


# set up categories
with open('categories.csv','rb') as f:
  reader = csv.reader(f)
  line_items = list(reader)

# first row is the header
headers=line_items[0]
del line_items[0]

# convert everything to lower case
headers=[k.lower() for k in headers]
line_items=[[k.lower() for k in i] for i in line_items]

catdb = TinyDB('./categories.json')
catdb.purge()
for num,var in enumerate(line_items):
  catdb.insert(dict(zip(headers,var)))



#with open('test.csv','rb') as f:
with open('full.csv','rb') as f:
  reader = csv.reader(f)
  line_items = list(reader)

# first row is the header
headers=line_items[0]
del line_items[0]

# convert everything to lower case
headers=[k.lower() for k in headers]
line_items=[[k.lower() for k in i] for i in line_items]

# build the current database
mtdb = TinyDB('./moneytracker.json')
mtdb.purge()
for num,var in enumerate(line_items):
  var[4]=float(var[4])
  mtdb.insert(dict(zip(headers,var)))

# remove positive-value entries
mtdb.remove(Query().amount > 0)

# scan for categories
for cat in catdb:
  # detect and record multiple-tagging
  for f in mtdb.search( (Query().description.search(cat['item'])) & (Query().tag.exists()) ):
    print "Double tag:     %-8s %-15s %-15s %s" % (f['amount'],f['tag'],cat['tag'],f['description'])
  mtdb.update(set('tag',cat['tag']),Query().description.search(cat['item']))

for f in mtdb.search(~ Query().tag.exists()):
  print "Untagged entry: %-40s %s" % (f['amount'],f['description'])


