'''
Created on Jul 25, 2015

@author: abhinav
'''
from server.router_server import routerServer
from server.utils import serverSecretFunc, responseFinish
from server.constants import OK
from db.admin.server import Servers
from server import configuration
import tornado
from server.logging import logger

    
@serverSecretFunc
def reloadServerMap(response):
    routerServer.reloadServers()
    responseFinish(response, {"code":OK})

@serverSecretFunc
def getAllActiveServers(response):
    responseFinish(response, {"servers": {server.serverId: server.addr for server in routerServer.servers.values()}})


@serverSecretFunc
def resetAllServerMaps(response):
    secretKey = response.get_argument("secretKey")
    ret =""
    servers = Servers.getAllServers(configuration.serverGroup)
    http_client = tornado.httpclient.AsyncHTTPClient()
            
    for server in servers:#while starting inform all other local servers to update this map
        try:
            ret+="updating .."+server.serverId+"\n"
            ret+=(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey)+"\n"
            http_client.fetch(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey, lambda response: logger.info(response), method='GET') #Send it off!
            ret+="####\n"
        except:
            ret+="Error...\n"
        response.write(ret)
        ret=""

    responseFinish(response, {"code":OK})



