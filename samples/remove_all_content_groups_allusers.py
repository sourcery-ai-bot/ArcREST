"""
   This sample shows how to loop through all users
   and delete all their content and groups

   Python 2.x
   ArcREST 3.5
"""
from __future__ import print_function
import arcrest
from arcresthelper import resettools
from arcresthelper import common
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback, inspect, sys
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def main():
    proxy_port = None
    proxy_url = None

    securityinfo = {
        'security_type': 'Portal',
        'username': "",
        'password': "",
        'org_url': "http://www.arcgis.com",
        'proxy_url': proxy_url,
        'proxy_port': proxy_port,
        'referer_url': None,
        'token_url': None,
        'certificatefile': None,
        'keyfile': None,
        'client_id': None,
        'secret_id': None,
    }
    try:

        rst = resettools.resetTools(securityinfo=securityinfo)
        if rst.valid:

            users = rst.securityhandler.username# comma delimited list of users  ex: 'User1, User2'

            rst.removeUserData(users=users)
            rst.removeUserGroups(users=users)
        else:
            print (rst.message)
    except common.ArcRestHelperError as e:
        print(f"error in function: {e[0]['function']}")
        print(f"error on line: {e[0]['line']}")
        print(f"error in file name: {e[0]['filename']}")
        print(f"with error message: {e[0]['synerror']}")
        if 'arcpyError' in e[0]:
            print(f"with arcpy message: {e[0]['arcpyError']}")
    except:
        line, filename, synerror = trace()
        print(f"error on line: {line}")
        print(f"error in file name: {filename}")
        print(f"with error message: {synerror}")

if __name__ == "__main__":
    main()
