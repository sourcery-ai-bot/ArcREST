
"""
   This sample shows how to loop through the folders
   and print their titles

   Python 2/3
   ArcREST version 3.5.x
"""

from __future__ import print_function
from arcrest.security import AGOLTokenSecurityHandler
import arcrest

if __name__ == "__main__":
    username = ""#Username
    password = ""#password
    proxy_port = None
    proxy_url = None

    agolSH = AGOLTokenSecurityHandler(username=username,
                                      password=password)


    admin = arcrest.manageorg.Administration(securityHandler=agolSH)
    content = admin.content
    user = content.users.user()

    for folder in user.folders:
        title = folder['title']
        print(f"Analyzing {title}")
        user.currentFolder = title
        print(f"Current folder is {user.currentFolder}")
        print(f"Current folder has {len(user.items)} items")