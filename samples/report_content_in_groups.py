"""
   This sample shows how to create a list in json
   of all items in a group

   Python 2.x/3.x
   ArcREST 3.5,6
"""
from __future__ import print_function
from __future__ import absolute_import

import arcrest
import os
import json
from arcresthelper import orgtools, common
import csv
import sys
from arcresthelper.packages import six

def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback, inspect,sys
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror
def _unicode_convert(obj):
    """ converts unicode to anscii """
    if isinstance(obj, dict):
        return {_unicode_convert(key): _unicode_convert(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_unicode_convert(element) for element in obj]
    elif isinstance(obj, str):
        return obj 
    elif isinstance(obj, six.text_type):
        return obj.encode('utf-8')
    elif isinstance(obj, six.integer_types):
        return obj
    else:
        return obj

if __name__ == "__main__":
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
    groups = ["Demographic Content"] #Name of groups
    outputlocation = r"C:\TEMP"
    outputfilename = "group.json"
    outputitemID = "id.csv"
    try:

        orgt = orgtools.orgtools(securityinfo)

        groupRes = []
        if orgt.valid:
            fileName = os.path.join(outputlocation,outputfilename)
            csvFile = os.path.join(outputlocation,outputitemID)
            iconPath = os.path.join(outputlocation,"icons")
            if not os.path.exists(iconPath):
                os.makedirs(iconPath)

            if sys.version_info[0] == 2:
                access = 'wb+'
                kwargs = {}
            else:
                access = 'wt+'
                kwargs = {'newline':''}
            with open(fileName, "w") as file:
                with open(fileName, access, **kwargs) as csvFile:
                    idwriter = csv.writer(csvFile)
                    for groupName in groups:
                        results = orgt.getGroupContent(groupName=groupName,
                                                       onlyInOrg=True,
                                                       onlyInUser=True)

                        if results is not None:
                            for result in results:
                                idwriter.writerow([result['title'],result['id']])
                                thumbLocal = orgt.getThumbnailForItem(itemId=result['id'],
                                                                      fileName=result['title'],
                                                                  filePath=iconPath)
                                result['thumbnail']=thumbLocal
                                groupRes.append(result)

                    if groupRes:
                        print(f"{len(groupRes)} items found")
                        groupRes = _unicode_convert(groupRes)
                        file.write(json.dumps(groupRes, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
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