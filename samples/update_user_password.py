"""
   Update a users passwords

   version 3.5.x
   Python 2/3
"""

from __future__ import print_function
from arcresthelper import securityhandlerhelper
import arcrest

if __name__ == "__main__":

    username = ''# Username

    proxy_port = None
    proxy_url = None

    securityinfo = {
        'security_type': 'Portal',
        'username': "",
        'password': "",
        'org_url': "https://www.arcgis.com",
        'proxy_url': proxy_url,
        'proxy_port': proxy_port,
        'referer_url': None,
        'token_url': None,
        'certificatefile': None,
        'keyfile': None,
        'client_id': None,
        'secret_id': None,
    }
    shh = securityhandlerhelper.securityhandlerhelper(securityinfo=securityinfo)
    if shh.valid == False:
        print (shh.message)
    else:
        admin = arcrest.manageorg.Administration(securityHandler=shh.securityhandler, initialize=True)
        user = admin.community.users.user(username.strip())
        print (user.update(password="1234testtest"))
