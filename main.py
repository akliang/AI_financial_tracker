
# on my laptop, the path to Python is incomplete and it cant find where pip packages are installed
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

import csv
import tinydb
import tinydb.operations
import datetime
import operator
import plotly
import plotly.graph_objs as go
import hashlib

def main():
  if len(sys.argv)==1:
    print("Needs an input file as an input parameter")
    exit()

  # some newlines to look prettier
  print('\n'*2)
  print("### Script output and debug information ###")

  # set up categories
  print("Setting up categories...")
  catdb = import_csv('./categories.csv','./categories.json','catdb',True)

  # import each input file
  ### old style: delete the db and import only the input files
  #for d,f in enumerate(sys.argv[1:]):
  #  if d==0:
  #    purge=True
  #  else:
  #    purge=False
  #  print("Reading in file %s..." % f)
  #  mtdb  = import_csv(f,'./moneytracker.json','mtdb',purge)
  ### new style, keep appending new data to a master db
  for f in (sys.argv[1:]):
    print("Reading in file %s..." % f)
    mtdb  = import_csv(f,'./moneytracker.json','mtdb')

  # change the dollar amounts to float
  # todo: find a db-friendly way to do this
  # (currently done as a hack in import_csv)

  # remove positive-value entries
  mtdb.remove(tinydb.Query().amount > 0)

  # assign categories to each item and report errors
  for cat in catdb:
    # detect and record multiple-tagging
    for f in mtdb.search( (tinydb.Query().description.search(cat['item'])) & (tinydb.Query().tag.exists()) ):
      if f['tag']!=cat['tag']:  # truly a clash, not just an old entry
        print("Double tag:     %-8s %-15s %-15s %s" % (f['amount'],f['tag'],cat['tag'],f['description']))
    # add category tag to all entries that dont already have a tag assigned
    mtdb.update(tinydb.operations.set('tag',cat['tag']), (tinydb.Query().description.search(cat['item'])) & ~(tinydb.Query().tag.exists()) )
  for f in mtdb.search(~ tinydb.Query().tag.exists()):
    print("Untagged entry: %-40s %s" % (f['amount'],f['description']))


  print_output(mtdb)
# end main


def print_output(mtdb):
  # build uniqe list of tags used in db
  uniqtags = set(f['tag'] for f in mtdb.search(tinydb.Query().tag.exists()))

  # build list of dates
  uniqdays=[f['transdate'] for f in mtdb.all()]
  uniqdays=set(uniqdays)  # get unique values
  uniqdays=list(uniqdays)  # convert it back into list, because order matters
  uniqdays=sorted(uniqdays,key=lambda x:datetime.datetime.strptime(x,'%m/%d/%Y'))

  #### output fun statistics ####
  print('\n'*2)

  print("### overall statistics ###")
  resrow=[]
  sumtot=0
  for f in mtdb.all():
    sumtot+=f['amount']
  # round sumtot to nearest cent
  sumtot="%0.2f" % sumtot
  sumtot=float(sumtot)
  resrow.append(['Total amount spent',sumtot])
  resrow.append(['Number of items',len(mtdb)])
  resrow.append(['Average amount per item',"%0.2f" % (sumtot/len(mtdb))])
  resrow.append(['Start date',uniqdays[0]])
  resrow.append(['End date',uniqdays[-1]])
  for f in resrow:
    print("%-30s: %10s" % (f[0],f[1]))
  save_csv(resrow,"overview.csv")

  # total sum per category
  print("")
  print("### spending by category ###")
  resrow=[]
  for tag in uniqtags:
    sumtot = 0
    for f in mtdb.search(tinydb.Query().tag == tag):
      sumtot += f['amount']
    numf=mtdb.count(tinydb.Query().tag == tag)
    resrow.append([tag,sumtot,numf,sumtot/numf])
  # sort by sumtot
  for f in sorted(resrow, key=operator.itemgetter(1)):
    print("%-15s: %10.2f (number of items: %3d, avg spend per item: %10.2f)" % (f[0],f[1],f[2],f[3]))
  save_csv(resrow,"spending_per_category.csv")

  # money spent per day
  plusfac=-50
  print("")
  print("### spending by day ###")
  resrow=[]
  for tag in uniqdays:
    sumtot = 0
    for f in mtdb.search(tinydb.Query().transdate == tag):
      sumtot += f['amount']
    resrow.append([tag,sumtot])

    #sys.stdout.write("%-10s: %8.2f   " % (tag,sumtot))
    #sys.stdout.flush()
    #print("+"*(int(sumtot/plusfac)))
  for f in resrow:
    sys.stdout.write("%-10s: %8.2f   " % (f[0],f[1]))
    sys.stdout.flush()
    print("+"*(int(f[1]/plusfac)))
  save_csv(resrow,"spending_per_day.csv")

  # highest spend per category
  print("")
  print("### highest spending per category ###")
  resrow=[]
  sumtot=0
  for tag in uniqtags:
    min=0
    str=''
    for f in mtdb.search(tinydb.Query().tag == tag):
      if f['amount']<min:
        min=f['amount']
        str=f
    #print("tag: %15s  item: %30s  amount: %0.2f" % (str['tag'],str['description'],str['amount']))
    resrow.append([str['tag'],str['description'],str['amount']])
    sumtot+=str['amount']
  print("%-15s %-30s %s" % ("==tag==","==description==","==amount=="))
  for f in sorted(resrow, key=operator.itemgetter(2)):
    print("%-15s %-30s %8.2f" % (f[0],f[1],f[2]))
  print("%-46s %8.2f" % ("--- total ---",sumtot))
  save_csv(resrow,"highest_spend_per_category.csv")

  # list items over a certain threshold
  threshold=-100
  print("")
  print("### items over %0.2f ###" % (threshold))
  resrow=[]
  sumtot=0
  for f in mtdb.search(tinydb.Query().tag.exists()):
    if (f['amount']<=threshold):
      resrow.append([f['tag'],f['description'],f['amount']])
      #print("tag: %15s  item: %30s  amount: %0.2f" % (f['tag'],f['description'],f['amount']))
      sumtot+=f['amount']
  print("%-15s %-30s %s" % ("==tag==","==description==","==amount=="))
  for f in sorted(resrow, key=operator.itemgetter(2)):
    print("%-15s %-30s %8.2f" % (f[0],f[1],f[2]))
  print("%-46s %8.2f" % ("--- total ---",sumtot))
  save_csv(resrow,"items_over_spend_threshold.csv")
  plot_py("spending_per_category.csv","spending_per_day.csv","highest_spend_per_category.csv","items_over_spend_threshold.csv")
# end print_output



def import_csv(file,db_name,db_handle,purge = False):
  debug=True

  with open(file,'rt') as f:
    reader = csv.reader(f)
    line_items = list(reader)

  # first row is the header
  headers=line_items[0]
  del line_items[0]

  # convert everything to lower case
  headers=[k.lower() for k in headers]
  line_items=[[k.lower() for k in i] for i in line_items]

  # remove spaces in header
  headers=[k.replace(' ','') for k in headers]

  db_handle = tinydb.TinyDB(db_name)
  if purge==True:
    db_handle.purge()

  isData=False
  if (len(line_items[0])>2):
    isData=True
    headers.append('hash')

  ins_cnt=0
  skip_cnt=0
  for var in line_items:
    if isData:
      # this means the csv file is data, not the categories file
      # do some special operations

      # generate a hash string
      hashstr=''.join(var)
      hashstr=hashlib.sha256(hashstr.encode('utf-8')).hexdigest()

      # convert the dollar value to float
      var[4]=float(var[4])

      # check if already in database
      if len(db_handle)>0:
        if db_handle.count(tinydb.Query().hash == hashstr) > 0:
          skip_cnt += 1
          if debug:
            for err in db_handle.search(tinydb.Query().hash == hashstr):
              print(err)
          continue

      # append hash to var
      var.append(hashstr)

    db_handle.insert(dict(zip(headers,var)))
    ins_cnt += 1

  print("Number of records inserted: %d" % (ins_cnt))
  print("Number of records skipped: %d\n" % (skip_cnt))

  return db_handle
# end import_csv


def save_csv(input_list,outfile):
  with open(outfile,'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerows(input_list)
# end save_csv

def plot_py(input_csv,*args):
  fig = plotly.tools.make_subplots(rows=len(args)+1,cols=1)

  # read the input as a 2D list
  with open(input_csv,'rt') as f:
    reader = csv.reader(f)
    line_items = list(reader)
  trace1=go.Scatter( x=[item[0] for item in line_items], y=[item[1] for item in line_items] )
  fig.append_trace(trace1,1,1)

  for argi,arg in enumerate(args):
    with open(arg,'rt') as f:
      reader = csv.reader(f)
      line_items = list(reader)
    trace2=go.Scatter( x=[item[0] for item in line_items], y=[item[1] for item in line_items] )
    fig.append_trace(trace2,argi+2,1)

  plotly.offline.plot(fig)

# end plot_py

if __name__ == "__main__":
  main()

