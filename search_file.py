import os, time, re

def collect_level(resultlist,root,level):
   entries = os.listdir(root)
   for entry in entries:
      filepath = os.path.join(root,entry)
      if level == 0:
         resultlist.append(filepath)
      else:
         if os.path.isdir(filepath):
            collect_level(resultlist,filepath,level-1)

def filter_pattern(inputlist,patternlist):
   resultlist = []
   for item in inputlist:
      keep = True
      for pattern in patternlist:
         if not re.search(pattern,item):
            keep = False
      if keep:
         resultlist.append(item)
         
   return resultlist

def search_and_filter(root,level,patternlist):
   resultlist = []
   collect_level(resultlist,root,level)
   resultlist = filter_pattern(resultlist,patternlist)
   return resultlist

