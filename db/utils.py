'''
Created on Jul 24, 2015

@author: abhinav
'''


def getTagsFromString(s,toLower=True):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            t = j.strip()
            if(not t):#empty not tolerated 
                continue
            t.replace(" ","-")
            t.replace("_","-")
            if(toLower):
                t = t.lower()
            ret.append(t)
    return ret


def getListFromString(s,toLower=False):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            t = j.strip()
            if(not t):
                continue 
            if(toLower):
                t = t.lower()
            ret.append(t)
    return ret

