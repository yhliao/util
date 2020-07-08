
class XLScolWriter:
    def __init__(self,sheet):
        self.sheet = sheet
        self.coln  = 0
    def write_col(self,data,colname=""):
        rown = 0
        if colname != "":
            self.sheet.write(rown,self.coln,colname)
            rown += 1

        for d in data:
            self.sheet.write(rown,self.coln,d)
            rown += 1
        self.coln += 1
