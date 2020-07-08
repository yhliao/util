import os, re

def _check(value,spec,ref):
   refspec = ref[spec]
   if refspec is None:
      return True
   elif type(refspec) is list:
      for pattern in refspec:
         if re.fullmatch(pattern,value):
            return True
   else:
      if re.fullmatch(refspec,value):
         return True
   ## Otherwise
   return False

def check_rematchgroup(match,specs,ref):
   for i, spec in enumerate(specs):
      if not _check(match.group(i+1),spec,ref):
         return False
   return True

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
