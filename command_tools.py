from datetime import datetime
import os, time
import numpy as np

def log_and_run(runfunc,path,logfile):
   if not logfile is None:
      startt = datetime.now()
      logfile.write("{0}: Job started for {1}\n"
                   .format(startt,path))
      logfile.flush()
   code = runfunc(path)
   if not logfile is None:
      now = datetime.now()
      logfile.write("{0}: Job finished for {1}; exit status: {2}; time elapsed: {3}\n"
                   .format(now,path,code,now-startt))
      logfile.flush()
   
def merge_list(filename_dict,keys):
   filename_list = []
   if keys is None:
      for value in filename_dict.values():
         filename_list += value
   else:
      for key in keys:
         filename_list += filename_dict[key]

   return filename_list

def commandrun(filename_dict,runfunc,logfile=None,keys=None):
   filename_list = merge_list(filename_dict,keys)
   
   for n, filename in enumerate(filename_list):
      print ("({0})".format(n),filename)
   command = input (">>> ")
   if command in ["a","all"]:
      for path in filename_list:
         log_and_run(runfunc,path,logfile)
   elif command=="" and len(filename_list)==1:
      path = filename_list[0]
      print ("Process the only file by default..")
      log_and_run(runfunc,path,logfile)
   else:
      tokens = command.split('/')
      index_str = [str(n) for n in range(len(filename_list))]
      for token in tokens:
         if token in index_str:
            path = filename_list[int(token)]
            log_and_run(runfunc,path,logfile)

def sort_mtime(inputlist):
   ctimelist = []
   mtimelist = []
   for filepath in inputlist:
      mtime = os.path.getmtime(filepath)
      mtimelist.append(mtime)
      ctimelist.append(time.ctime(mtime))
   sorted_idx = np.argsort(ctimelist)
   sorted_inputlist = [inputlist[i] for i in sorted_idx]
   sorted_ctimelist = [ctimelist[i] for i in sorted_idx]
   return sorted_inputlist, sorted_ctimelist

def command_listrun(filename_list, runfunc, descriptions=None ):
   
   if descriptions is None:
      descriptions = [""] * len(filename_list)

   pad = max([len(path) for path in filename_list])
   for n, (filepath, des) in enumerate(zip(filename_list,descriptions)):
      print (n,':', filepath.ljust(pad), des)
   command = input (">>> ")
   tokens = command.split('/')
   runpathlist = []
   index_str = [str(n) for n in range(len(filename_list))]
   for token in tokens:
      if token in index_str:
         runpathlist.append( filename_list[int(token)] )

   if len(runpathlist) > 0:
      runfunc (runpathlist)
