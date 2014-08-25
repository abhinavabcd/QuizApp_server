'''
Created on Jun 19, 2014

@author: abhinav2
'''

import random
import string
import datetime

####################config variables 
HTTP_PORT=8084
# status codes for web requests
NOT_ACTIVATED = 104
ACTIVATED = 105
NOT_AUTHORIZED = 106
OK =200
OK_AUTH=202
USER_EXISTS=203
USER_NOT_EXISTS = 204
USER_SAVED = 205
OK_IMMUTABLE = 206
OK_FEED = 207
OK_INIT = 208
FAILED=300
DUPLICATE_USER = 301
CAN_UPGRADE=212
ALLOWED=211
CAN_UPGRADE_RECHARGE = 213
REG_SAVED = 214
OK_USER_INFO =215
OK_NAME=216
NO_NAME_FOUND = 217
RATING_OK = 220;

OK_DETAILS = 501
NOT_FOUND=404   
OK_QUESTIONS = 502
OK_QUESTION = 503
OK_SERVER_DETAILS = 504
OK_UPDATES = 505
FACEBOOK_USER_SAVED = 506
GPLUS_USER_SAVED = 507

################################# dict values/commands for payload type definition
USER_ANSWERED_QUESTION = 1
GET_NEXT_QUESTION = 2
STARTING_QUESTIONS = 3
ANNOUNCING_WINNER = 4
USER_DISCONNECTED = 5
NEXT_QUESTION =6
START_QUESTIONS = 7
STATUS_WHAT_USER_GOT = 8

#################################dict keys
QUESTIONS = 1
CURRENT_QUESTION = 2
MESSAGE_TYPE = 3
QUESTION_ID = 4
WHAT_USER_HAS_GOT = 5
N_CURRENT_QUESTION_ANSWERED = 6
USER_ANSWER = 7
USERS=8


#preference strigns
PREF_IMMUTABLES_COUNT = "immutables_count"
###########Notification types

DONT_KNOW = 0
NOTIFICATION_COOL_DOWN = 1
NOTIFICATION_NEW_UNLOCKED = 2
NOTIFICATION_GCM_GENERAL_FROM_SERVER =3
NOTIFICATION_GCM_USER_IMMUTABLE =4


AUTH_WHATSAPP_PHONENUMBER ="+917680971071"
USER_ACTIVATION_MESSAGE = "Please send the above activation code to "+AUTH_WHATSAPP_PHONENUMBER+" from your whatsapp to get activated."
EPOCH_DATETIME = datetime.datetime(1970,1,1)

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
     
  
  
  
  
secret_auth="asdsadkjhsakjdhjksad"
GCM_API_KEY = "AIzaSyCEhpQRBHfeAsdYS85VlcrsB7XQADbEWNw"
GCM_HEADERS ={'Content-Type':'application/json',
              'Authorization':'key='+GCM_API_KEY
        }

IS_TEST_BUILD = True
ONE_DAY= datetime.timedelta(days = 1)
MAX_FREE_MESSAGES_PER_DAY = 50 if IS_TEST_BUILD else 8
MAX_MESSAGES_LIMIT_PER_DAY = 50 if IS_TEST_BUILD else 15
MESSAGE_RECHARGE_TIME = timedelta_to_int(datetime.timedelta(hours = 1)) if not IS_TEST_BUILD else  timedelta_to_int(datetime.timedelta(minutes = 5))