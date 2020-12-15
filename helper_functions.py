
def list2d_search(search_str, dat):
    for sublist in dat:
        if search_str in sublist:
            return sublist


def process_chase_csv(currdata):
    dat = []
    firstrow = True
    for row in currdata:
        # the first row is always header, skip it
        if firstrow:
            firstrow = False
            continue
        dat.append([row[0], row[2], row[3], row[4], row[5]])
    return dat


def process_boa_csv(currdata):
    dat = []
    for row in currdata:
        dat.append([row[0], row[2], "", "", row[4]])
    return dat


#def fix_category(row):
