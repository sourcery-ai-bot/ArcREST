from __future__ import absolute_import
from __future__ import print_function
from .._abstract.abstract import BaseAGSServer
import os
########################################################################
class Uploads(BaseAGSServer):
    """
    This resource is a collection of all the items that have been uploaded
    to the server.
    See: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Uploads/02r3000001qr000000/
    """
    _uploads = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _url = None

    #----------------------------------------------------------------------
    def __init__(self, url, securityHandler,
                 proxy_url=None, proxy_port=None,
                 initialize=False):
        """Constructor"""
        self._url = f"{url}/uploads" if url.lower().find("uploads") < -1 else url
        self._securityHandler = securityHandler
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url

    #----------------------------------------------------------------------
    @property
    def uploads(self):
        """
        returns a collection of all the items that have been uploaded to
        the server.
        """
        params = {
            "f" :"json"
        }
        return self._get(url=self._url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)

    #----------------------------------------------------------------------
    def deleteItem(self, itemId):
        """
           Deletes the uploaded item and its configuration.
           Inputs:
              itemId - unique ID of the item
        """
        url = f"{self._url}/{itemId}/delete"
        params = {
            "f" : "json"
        }
        return self._post(url=url, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def item(self, itemId):
        """
        This resource represents an item that has been uploaded to the
        server. Various workflows upload items and then process them on the
        server. For example, when publishing a GIS service from ArcGIS for
        Desktop or ArcGIS Server Manager, the application first uploads the
        service definition (.SD) to the server and then invokes the
        publishing geoprocessing tool to publish the service.
        Each uploaded item is identified by a unique name (itemID). The
        pathOnServer property locates the specific item in the ArcGIS
        Server system directory.
        The committed parameter is set to true once the upload of
        individual parts is complete.
        """
        url = f"{self._url}/{itemId}"
        params = {
            "f" : "json"
        }
        return self._get(url=url, param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def uploadItem(self, filePath, description):
        """
        This operation uploads an item to the server. Each uploaded item is 
        identified by a unique itemID. Since this request uploads a file, it 
        must be a multi-part request as per IETF RFC1867. 
        
        Inputs:
            filePath - the file to be uploaded.
            description - optional description for the uploaded item.
        """
        import urlparse
        url = f"{self._url}/upload"
        params = {
            "f" : "json"
        }
        files = {'itemFile': filePath}
        return self._post(url=url,
                          param_dict=params,
                          files=files,
                          securityHandler=self._securityHandler,
                          proxy_url=self._proxy_url,
                          proxy_port=self._proxy_port)
