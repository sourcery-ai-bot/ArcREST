"""
This provides access to a server and it's services for non administrative
functions.  This allows developers to access a REST service just like a
user/developer would.
"""
from __future__ import absolute_import
from __future__ import print_function
from . import BaseAGSServer
from ..packages.six.moves.urllib_parse import urlparse

import json
from ._geoprocessing import GPService
from .mapservice import MapService
from .featureservice import FeatureService
from ._imageservice import ImageService
from ._mobileservice import MobileService
from ..geometryservice import GeometryService
from ._geocodeservice import GeocodeService
from ._geodataservice import GeoDataService
from ._networkservice import NetworkService
from ._globeservice import GlobeService
from ._streamservice import StreamService
__all__ = ['Server']
########################################################################
class Server(BaseAGSServer):
    """This object represents an ArcGIS Server instance"""
    _url = None
    _proxy_url = None
    _proxy_port = None
    _securityHandler = None
    _json = None
    _json_dict = None
    _folders = None
    _services = None
    _currentVersion = None
    _location = None
    _currentFolder = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initialize=False):
        """Constructor"""
        self._url = self._validateurl(url=url)
        self._location = self._url
        self._currentFolder = "root"
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        if initialize:
            self.__init()
    #----------------------------------------------------------------------
    def _validateurl(self, url):
        """assembles the server url"""
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if path:
            parts = path.split("/")
            url_types = ("admin", "manager", "rest")
            if any(i in parts for i in url_types):
                while parts.pop() not in url_types:
                    next
            elif "services" in parts:
                while parts.pop() not in "services":
                    next
            path = "/".join(parts)
        else:
            path = "arcgis"
        self._adminUrl = f"{parsed.scheme}://{parsed.netloc}/{path}/admin"
        return f"{parsed.scheme}://{parsed.netloc}/{path}/rest/services"
    #----------------------------------------------------------------------
    def __init(self, folder='root'):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        url = self.root if folder == "root" else self.location
        json_dict = self._get(url=url,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_port=self._proxy_port,
                                 proxy_url=self._proxy_url)
        self._json_dict = json_dict
        self._json = json.dumps(json_dict)
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                          not attr.startswith('_')]
        for k,v in json_dict.items():
            if k == "folders":
                pass
            elif k in attributes:
                setattr(self, f"_{k}", json_dict[k])
            else:
                print(f"{k} - attribute not implemented in ags.Server class.")
        json_dict = self._get(url=self.root,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_port=self._proxy_port,
                                 proxy_url=self._proxy_url)
        for k,v in json_dict.items():
            if k == 'folders':
                v.insert(0, 'root')
                setattr(self, f"_{k}", v)
    #----------------------------------------------------------------------
    @property
    def root(self):
        """gets the url of the class"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def admin(self):
        """points to the adminstrative side of ArcGIS Server"""
        if self._securityHandler is None:
            raise Exception("Cannot connect to adminstrative server without authentication")
        from ..manageags import AGSAdministration
        return AGSAdministration(url=self._adminUrl,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port,
                                 initialize=False)
    #----------------------------------------------------------------------
    @property
    def location(self):
        """returns the current url position in the server folder structure"""
        return self._location
    #----------------------------------------------------------------------
    def __str__(self):
        """returns object as raw string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        """iterates through json and returns values as [key, value]"""
        if self._json_dict is None:
            self._json_dict = {}
            self.__init()
        for k,v in self._json_dict.items():
            yield [k,v]
    #----------------------------------------------------------------------
    @property
    def currentVersion(self):
        """gets the current version of arcgis server"""
        if self._currentVersion is None:
            self.__init()
        return self._currentVersion
    #----------------------------------------------------------------------
    @property
    def self(self):
        """gets the logged in user"""
        params = {"f" : "json"}
        url = f'{self.root.replace("/services", "")}/self'
        return self._get(url=url,
                         param_dict=params,
                         securityHandler=self._securityHandler,
                         proxy_port=self._proxy_port,
                         proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def services(self):
        """gets the services in the current folder"""
        services = []
        if self._services is None:
            self.__init()
        for service in self._services:
            url = f"{self.root}/{service['name']}/{service['type']}"
            if service['type'] == "GPServer":
                services.append(GPService(url=url,
                                          securityHandler=self._securityHandler,
                                          proxy_url=self._proxy_url,
                                          proxy_port=self._proxy_port))
            elif service['type'] == "MapServer":
                services.append(MapService(url=url,
                                           securityHandler=self._securityHandler,
                                           proxy_url=self._proxy_url,
                                           proxy_port=self._proxy_port))
            elif service['type'] == "ImageServer":
                services.append(ImageService(url=url,
                                             securityHandler=self._securityHandler,
                                             proxy_url=self._proxy_url,
                                             proxy_port=self._proxy_port))
            elif service['type'] == "FeatureServer":
                if self.currentFolder == 'root':
                    serviceName = service['name']
                else:
                    serviceName = service['name'].split('/')[1]
                url = f"{self.location}/{serviceName}/{service['type']}"
                services.append(FeatureService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_url=self._proxy_url,
                                               proxy_port=self._proxy_port))
            elif service['type'] == "GeometryServer":
                url = f"{self.root}/{service['name']}/{service['type']}"
                services.append(GeometryService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_url=self._proxy_url,
                                               proxy_port=self._proxy_port))
            elif service['type'] == "MobileServer":
                services.append(MobileService(url=url,
                                              securityHandler=self._securityHandler,
                                              proxy_url=self._proxy_url,
                                              proxy_port=self._proxy_port))
            elif service['type'] == "NAServer":
                services.append(NetworkService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_port=self._proxy_port,
                                               proxy_url=self._proxy_url))
            elif service['type'] == "GeocodeServer":
                services.append(GeocodeService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_port=self._proxy_port,
                                               proxy_url=self._proxy_url))
            elif service['type'] == "GeoDataServer":
                services.append(GeoDataService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_port=self._proxy_port,
                                               proxy_url=self._proxy_url))
            elif service['type'] == "GlobeServer":
                services.append(GlobeService(url=url,
                                               securityHandler=self._securityHandler,
                                               proxy_port=self._proxy_port,
                                               proxy_url=self._proxy_url))
            elif service['type'] == "StreamServer":
                services.append(StreamService(url=url,
                                             securityHandler=self._securityHandler,
                                             proxy_port=self._proxy_port,
                                             proxy_url=self._proxy_url))
            elif service['type'] not in (
                "IndexGenerator",
                "IndexingLauncher",
                "SearchServer",
            ):
                print (service['type'], service['name'])
        return services
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """returns the folders on server"""
        if self._folders is None:
            self.__init(folder="root")
        return self._folders
    #----------------------------------------------------------------------
    @property
    def currentFolder(self):
        """gets/sets the current folder name"""
        return self._currentFolder
    #----------------------------------------------------------------------
    @currentFolder.setter
    def currentFolder(self, value):
        """gets/sets the current folder name"""
        if value in self.folders:
            if value.lower() != 'root':
                self._currentFolder = value
                self._location = f"{self.root}/{value}"
            else:
                self._currentFolder = value
                self._location = self.root
            self.__init(folder=value)

