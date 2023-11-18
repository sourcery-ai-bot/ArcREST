from __future__ import absolute_import
from __future__ import print_function
from ..packages.six.moves import urllib_parse as urlparse
from ..packages.six.moves.urllib.parse import urlencode
from .._abstract.abstract import BaseAGSServer
#import urlparse, urllib
import os
########################################################################
class Uploads(BaseAGSServer):
    """
    The uploads resource is the parent resource for upload related
    operations and resources. This resource is available only if the
    service or an extension supports the uploads capability. For Feature
    and Image Services, upload capability is enabled when editing is turned
    on. For Mobile and GP Services, upload capability can be explicitly
    enabled or disabled at publish time. For a Geodata Service, uploads is
    enabled when replication is turned on. If uploads is enabled for a
    service, it is recommended that the service be secured to allow only
    authenticated users access to this capability.
    """
    _securityHandler = None
    _url = None
    _proxy_port = None
    _proxy_url = None
    _initialize = None

    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 securityHandler=None,
                 initialize=False,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        self._url = url if url.lower().endswith('uploads') else f"{url}/uploads"
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    @property
    def info(self):
        """
        The info resource returns the maxUploadFileSize property of a
        service.
        """
        url = f"{self._url}/info"
        params = {
            "f" : "json"
        }
        return self._get(url=url, param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                           proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def upload(self, filePath, description=None):
        """
        This operation uploads an item to the server. Each uploaded item is
        identified by a unique itemID. Since this request uploads a file,
        it must be a multi-part request as per IETF RFC1867.
        All uploaded items are subjected to the deletion rules set on the
        upload directory by the administrator of the server. Additionally,
        the administrator can explicitly delete an item as each uploaded
        item shows up in the list of all the uploaded items in Site
        Directory.
        Users can provide arguments to the upload operation as query
        parameters. The parameter details are provided in the parameters
        listed below.
        Inputs:
           filePath - The file to be uploaded.
           description	- An optional description for the uploaded item.
        """
        params = {
            "f" : "json"}
        if description is not None:
            params['description'] = str(description)
        url = f"{self._url}/upload"
        files = {'file': filePath}
        return self._post(url=url,
                          param_dict=params,
                          files=files,
                          securityHandler=self._securityHandler,
                          proxy_url=self._proxy_url,
                          proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def delete(self, itemID):
        """
        This operation deletes an item.

        Inputs:
           itemID - unique ID of item
        """
        url = f"{self._url}/{itemID}/delete"
        params = {
            "f" : "json"
        }
        return self._post(url=url, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def download(self, itemID, savePath):
        """
        downloads an item to local disk

        Inputs:
           itemID - unique id of item to download
           savePath - folder to save the file in
        """
        if os.path.isdir(savePath) == False:
            os.makedirs(savePath)
        url = f"{self._url}/{itemID}/download"
        params = {
        }
        if len(params.keys()):
            url = f"{url}?{urlencode(params)}"
        return self._get(url=url,
                         param_dict=params,
                         out_folder=savePath,
                         securityHandler=self._securityHandler,
                         proxy_url=self._proxy_url,
                         proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def uploads(self):
        """
        returns all uploaded items for this service.
        """
        url = self._url
        params = {
            "f" : "json",

        }
        return self._get(url=url, param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                           proxy_port=self._proxy_port)







