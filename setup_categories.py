
import csv
from tinydb import TinyDB, Query

with open('categories.csv','rb') as f:
  reader = csv.reader(f)
  line_items = list(reader)

# first row is the header
headers=line_items[0]
del line_items[0]

db = TinyDB('./categories.json')
for num,var in enumerate(line_items):
  print(dict(zip(headers,var)))
  db.insert(dict(zip(headers,var)))
  


