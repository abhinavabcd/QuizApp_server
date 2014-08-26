'''
Created on Jun 19, 2014

@author: abhinav2
'''

import random
import string
from Constants import *

def generateKey(N=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))

def timedelta_to_int(td):
    return (td.seconds + td.days * 86400)
 
def toUtcTimestamp(dt):
    try:
        td = dt - EPOCH_DATETIME
        # return td.total_seconds()
        return  (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 
    except:
        return 0
  

