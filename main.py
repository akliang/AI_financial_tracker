
import csv
from tinydb import TinyDB,where,Query

with open('test.csv','rb') as f:
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
  mtdb.insert(dict(zip(headers,var)))

# scan for categories
catdb = TinyDB('./categories.json')
for cat in catdb:
  print(cat['item'])
  print mtdb.search(Query().description.search(cat['item']))




