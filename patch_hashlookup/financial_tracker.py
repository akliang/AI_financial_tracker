
import os
import csv
import hashlib
import helper_functions as hf

data_folder = "./2020_data"
cache_folder = "./cache"

alldat = []
for filename in os.listdir(data_folder):
    currfile = "%s/%s" % (data_folder, filename)
    with open(currfile) as csv_file:
        currdata = csv.reader(csv_file)
        # grab the first row to detect which formatter to use
        for row in currdata:
            if row[0] == "Transaction Date":
                dat = hf.process_chase_csv(currdata)
            elif row[0] == "Posted Date":
                dat = hf.process_boa_csv(currdata)
            else:
                print("Error: unrecognized CSV file")
                exit(5)
            break
    # add the newly processed dat to alldat
    alldat.extend(dat)

# read in the data patch
with open('%s/data_patch.csv' % cache_folder, 'r') as data_patch_csv:
    data_patch = list(csv.reader(data_patch_csv))

# assign (correct) tags to every entry
dat = []
dp_stop = False
with open('final_data.csv', 'w', newline='') as final_data_csv:
    csv_writer = csv.writer(final_data_csv, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in alldat:
        if (row[2] == "") or (row[3] == ""):
            row_hash = hashlib.md5(str(row[1]).encode('utf-8')).hexdigest()
            # check if this hash exists in the patch
            res = hf.list2d_search(row_hash, data_patch)
            if res:
                # if the data patch isnt completed, then warn the user at the end
                if (res[1] == "") or (res[2] == ""):
                    dp_stop = True
                row[2] = res[1]
                row[3] = res[2]
            else:
                dp_stop = True
                with open('%s/data_patch.csv' % cache_folder, 'a', newline='') as data_patch_csv:
                    dp_csv_writer = csv.writer(data_patch_csv, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    dp_csv_writer.writerow([row[1], '', '', row_hash])
        csv_writer.writerow(row)

if dp_stop:
    print('Warning: uncategorized items added to data patch... please fix and run again')

print("Financial tracker script - Done!")
