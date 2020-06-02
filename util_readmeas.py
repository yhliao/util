import csv
import numpy as np

## Simple function parsing measurement csv file into data dict
def parse_meascsv(measfilename):
    try:
       with open (measfilename,'r') as csvfile:
           csvreader = csv.reader(csvfile)
           for row in csvreader:
               if row[0] == 'DataName':
                   DataName = [t.strip(' ') for t in row[1:]]
                   DataValue = [[] for dn in DataName]
               if row[0] == 'DataValue':
                   assert not DataValue is None, \
                       ("DataValue should not appear before DataName")
                   for datalist, value in zip(DataValue,row[1:]):
                       try:
                          datalist.append(float(value.strip(' ')))
                       except:
                          print ("Error Encountered")
                          print (DataName)
                          print (DataValue)
                          print (value)
                          raise ValueError
           DataDict = {dn: np.array(dv) for dn, dv in zip(DataName,DataValue)}
    except Exception as inst:
       print ("Error parsing file" + measfilename)
       import subprocess
       subprocess.call(["vim",measfilename])
       raise inst 

    return DataDict

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
