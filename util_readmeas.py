import csv
import numpy as np

## Simple function parsing measurement csv file into data dict
def parse_meascsv(measfilename,dbg=False):
    try:
       with open (measfilename,'r') as csvfile:
           csvreader = csv.reader(csvfile)
           for n, row in enumerate(csvreader):
               if row[0] == 'DataName':
                   DataName = [t.strip(' ') for t in row[1:]]
                   DataValue = [[] for dn in DataName]
               if row[0] == 'DataValue':
                   assert not DataValue is None, \
                       ("DataValue should not appear before DataName")
                   for datalist, value in zip(DataValue,row[1:]):
                       value = value.strip(' ')
                       try:
                          datalist.append(float(value))
                       except:
                          if dbg:
                             print ("parse_meascsv: Warning")
                             print ("string value is :", value)
                             print ("The entire row (on line {0}) is:".format(n), row)
                          if value == "":
                             datalist.append(None)
                          else:
                             raise ValueError
           DataDict = {dn: np.array(dv) for dn, dv in zip(DataName,DataValue)}
    except Exception as inst:
       print ("Error parsing file" + measfilename)
       input ("Press Any Key to edit the file:")
       import subprocess
       subprocess.call(["vim",measfilename])
       raise inst 

    return DataDict

def split_data(datadict,indexfield,verbose=False):
   indexdata = datadict[indexfield]
   index = np.unique(indexdata)
   roundedindex = np.round(index,decimals=5)
   if np.any(index != roundedindex) and verbose:
      print ("split_data: warning...", 
            index, "rounded to", roundedindex, 
            "for easy key lookup")
   returndict = {}
   for ridx, idx in zip(roundedindex,index):
      selectidx  = (idx == indexdata)
      selectdict = dict([(key,value[selectidx]) 
                     for key, value in datadict.items()])
      returndict[ridx] = selectdict
   return returndict
## meassheet is a xlrd.sheet object containing one measurement set
def parse_meassheet(meassheet,skiprows=0):
    DataDict = {}
    for i in range(meassheet.ncols):
        col_val = meassheet.col_values(i)
        dataname  = str(col_val[skiprows])
        datavalue = np.array(col_val[skiprows+1:])
        DataDict[dataname] = datavalue
    return DataDict

## Split forward and reverse x (e.g. VG) sweep
def split_fnr_dict(ddict,x,*yargs):
    return split_fnr(ddict[x],*[ddict[y] for y in yargs])

def split_fnr(x, *yargs):
    dx = np.diff(x)
    for_idx = np.concatenate([[True],dx>0])
    rev_idx = np.concatenate([dx<0,[True]])

    return_for = [x[for_idx]] + [y[for_idx] for y in yargs]
    return_rev = [np.flip(x[rev_idx],axis=0)] + \
                 [np.flip(y[rev_idx],axis=0) for y in yargs]
    return return_for, return_rev
