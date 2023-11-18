from __future__ import absolute_import
from __future__ import print_function
from ..packages import six
from ..web._base import BaseWebOperations
_url = None
_securityHandler = None
_proxy_url = None
_proxy_port = None
_referer_url = None
class search(BaseWebOperations):
    def __init__(self, url=None, securityHandler=None, proxy_url=None, proxy_port=None):
        """Constructor"""

        if url is None and securityHandler is not None:
            url = f"{securityHandler.org_url}/sharing/rest"
        if proxy_url is None and securityHandler is not None:
            self._proxy_url = securityHandler.proxy_url
        else:
            self._proxy_url = proxy_url
        if proxy_port is None and securityHandler is not None:
            self._proxy_port = securityHandler.proxy_port
        else:
            self._proxy_port = proxy_port

        if url is None or url == '':
            raise AttributeError("URL or Security Hanlder needs to be specified")

        self._url = url if url.lower().find("/search") > -1 else f"{url}/search"
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url


    #----------------------------------------------------------------------
    def findItem(self, title, itemType,username=None,searchorg=False):
        title = title.replace(":"," ")

        if username is None:
            username = self._securityHandler.username
        if searchorg == True:
            params = {'f': 'json',
               'q': title}
            #'q': "(title:\""+ title}
        else:
            params = {'f': 'json', 'q': f"{title} owner:{username}"}
        if itemType is not None:
            #
            # Find the itemID of whats being updated
            #
            types = [
                  'Application',
                  'ArcPad Package',
                  'Basemap Package',
                  'Code Attachment',
                  'Code Sample',
                  'Color Set',
                  'Desktop Add In',
                  'Desktop Application Template',
                  'Desktop Style',
                  'Explorer Add In',
                  'Explorer Layer',
                  'Explorer Map',
                  'Feature Collection Template',
                  'Feature Collection',
                  'Feature Service',
                  'Featured Items',
                  'File Geodatabase',
                  'Geodata Service',
                  'Geoprocessing Package',
                  'Geoprocessing Sample',
                  'Globe Document',
                  'Image',
                  'Image Service',
                  'KML',
                  'Layer Package',
                  'Layer',
                  'Layout',
                  'Locator Package',
                  'Map Document',
                  'Map Service',
                  'Map Template',
                  'Mobile Basemap Package',
                  'Mobile Map Package',
                  'Pro Map',
                  'Project Package',
                  'Project Template',
                  'Published Map',
                  'Scene Document',
                  'Scene Package',
                  'Scene Service',
                  'Stream Service',
                  'Symbol Set',
                  'Tile Package',
                  'Windows Mobile Package',
                  'Windows Viewer Add In',
                  'Windows Viewer Configuration',
                  'WMS',
                  'Workflow Manager Package',
                  'Web Mapping Application',
                  'Web Map']
            if isinstance(itemType,list):
                typstr = None
                for ty in itemType:
                    if typstr is None:
                        typstr = " (type:\"" + ty + "\""
                    else:
                        typstr = typstr + " OR type:\"" + ty + "\""
                    if ty in types:
                        types.remove(ty)
                typstr = f"{typstr})"
                params['q'] = params['q'] + typstr

            else:
                if itemType in types:
                    types.remove(itemType)
                params['q'] = params['q'] + " (type:\"" + itemType + "\")"

                #itemType = ""
                #for ty in types:
                    #itemType = itemType + " -type:\"" + ty + "\""
                #params['q'] = params['q'] + itemType

        return self._get(
            url=self._url,
            securityHandler=self._securityHandler,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port,
        )
