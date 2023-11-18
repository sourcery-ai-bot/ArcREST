"""
   This sample shows how to add rows to an AGS based service
   version 3.5.4
   Python 2
"""
from __future__ import print_function
from __future__ import absolute_import
import arcrest
from arcresthelper import featureservicetools
from arcresthelper import common

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

def main():
    proxy_port = None
    proxy_url = None

    securityinfo = {
        'security_type': 'AGS',
        'username': "",
        'password': "",
        'org_url': "",
        'proxy_url': proxy_url,
        'proxy_port': proxy_port,
        'referer_url': None,
        'token_url': None,
        'certificatefile': None,
        'keyfile': None,
        'client_id': None,
        'secret_id': None,
    }
    pathToFeatureClass = r""#local path to feature class to load
    fs_url = ''#url to layer, not service, make sure it ends with a \Number

    try:

        fst = featureservicetools.featureservicetools(securityinfo)
        if fst.valid == False:
            print (fst.message)
        else:
            results =  fst.AddFeaturesToFeatureLayer(url=fs_url, pathToFeatureClass=pathToFeatureClass,
                                                      chunksize=2000)
            if 'addResults' in results:
                print(f"{len(results['addResults'])} features processed")
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