import os, re

def _check(flag,value,spec,ref):
   refspec = ref[spec]
   if refspec is None:
      return flag
   elif type(refspec) is list:
      if not value in refspec:
         return False
      else:
         return flag
   else:
      if not value==refspec:
         return False
      else:
         return flag

def check_rematchgroup(match,specs,ref):
   flag = True
   for i, spec in enumerate(specs):
      flag = _check(flag,match.group(i+1),spec,ref)
   return flag

def match_path_pplog(pplogfile,regex,specs,ref,suffix,groupspec=[1]):
   returndict = {}

   with open(pplogfile) as pplog:
      pattern = re.compile(regex)
      for line in pplog:
         fileprefix = line.strip("\n")
         match = pattern.fullmatch(fileprefix)
         if match:
            runflag = check_rematchgroup(match,specs,ref)
            if runflag:
               fullpath = fileprefix + suffix
               if os.path.isfile(fullpath):
                  key = "/".join([match.group(i) for i in groupspec])
                  try:
                     listtoupdate = returndict[key]
                  except:
                     listtoupdate = []
                     returndict[key] = listtoupdate
                  listtoupdate.append(fullpath)
   return returndict
