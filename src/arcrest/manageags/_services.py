from __future__ import absolute_import
from __future__ import print_function
from .._abstract.abstract import BaseAGSServer
from ..packages.six.moves.urllib_parse import urlparse
from .parameters import Extension
import os
import json
import tempfile
import xml.etree.ElementTree as ET
########################################################################
class Services(BaseAGSServer):
    """ returns information about the services on AGS """
    _currentURL = None
    _url = None
    _securityHandler = None
    _folderName = None
    _folders = None
    _foldersDetail = None
    _folderDetail = None
    _webEncrypted = None
    _description = None
    _isDefault = None
    _services = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, securityHandler,
                 proxy_url=None, proxy_port=None,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               token_url - url to generate token
               username - admin username
               password - admin password
        """
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port
        self._url = url
        self._currentURL = url
        self._securityHandler = securityHandler
        if initialize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """ populates server admin information """
        params = {
            "f" : "json"
        }
        json_dict = self._get(url=self._currentURL,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        self._json = json.dumps(json_dict)
        attributes = [attr for attr in dir(self)
                    if not attr.startswith('__') and \
                        not attr.startswith('_')]
        for k,v in json_dict.items():
            if k in attributes:
                setattr(self, f"_{k}", json_dict[k])
            else:
                print( k, " - attribute not implemented manageags.services.")
            del k
            del v
    #----------------------------------------------------------------------
    def __str__(self):
        """returns the object as a string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    @property
    def webEncrypted(self):
        """ returns if the server is web encrypted """
        if self._webEncrypted is None:
            self.__init()
        return self._webEncrypted
    #----------------------------------------------------------------------
    @property
    def folderName(self):
        """ returns current folder """
        return self._folderName
    #----------------------------------------------------------------------
    @folderName.setter
    def folderName(self, folder):
        """gets/set the current folder"""

        if folder in ["", "/"]:
            self._currentURL = self._url
            self._services = None
            self._description = None
            self._folderName = None
            self._webEncrypted = None
            self.__init()
            self._folderName = folder
        elif folder in self.folders:
            self._currentURL = f"{self._url}/{folder}"
            self._services = None
            self._description = None
            self._folderName = None
            self._webEncrypted = None
            self.__init()
            self._folderName = folder
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """ returns a list of all folders """
        if self._folders is None:
            self.__init()
        if "/" not in self._folders:
            self._folders.append("/")
        return self._folders
    #----------------------------------------------------------------------
    @property
    def foldersDetail(self):
        """returns the folder's details"""
        if self._foldersDetail is None:
            self.__init()
        return self._foldersDetail
    #----------------------------------------------------------------------
    @property
    def description(self):
        """ returns the decscription """
        if self._description is None:
            self.__init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def isDefault(self):
        """ returns the is default property """
        if self._isDefault is None:
            self.__init()
        return self._isDefault
    #----------------------------------------------------------------------
    @property
    def services(self):
        """ returns the services in the current folder """
        self._services = []
        params = {
                    "f" : "json"
                }
        json_dict = self._get(url=self._currentURL,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        if "services" in json_dict.keys():
            for s in json_dict['services']:
                uURL = f"{self._currentURL}/{s['serviceName']}.{s['type']}"
                self._services.append(
                    AGSService(url=uURL,
                               securityHandler=self._securityHandler,
                               proxy_url=self._proxy_url,
                               proxy_port=self._proxy_port)
                )
        return self._services
    #----------------------------------------------------------------------
    def find_services(self, service_type="*"):
        """
            returns a list of a particular service type on AGS
            Input:
              service_type - Type of service to find.  The allowed types
                             are: ("GPSERVER", "GLOBESERVER", "MAPSERVER",
                             "GEOMETRYSERVER", "IMAGESERVER",
                             "SEARCHSERVER", "GEODATASERVER",
                             "GEOCODESERVER", "*").  The default is *
                             meaning find all service names.
            Output:
              returns a list of service names as <folder>/<name>.<type>
        """
        allowed_service_types = ("GPSERVER", "GLOBESERVER", "MAPSERVER",
                                 "GEOMETRYSERVER", "IMAGESERVER",
                                 "SEARCHSERVER", "GEODATASERVER",
                                 "GEOCODESERVER", "*")
        lower_types = [l.lower() for l in service_type.split(',')]
        for v in lower_types:
            if v.upper() not in allowed_service_types:
                return {"message": f"{v} is not an allowed service type."}
        params = {
            "f" : "json"
        }
        type_services = []
        folders = self.folders
        baseURL = self._url
        for folder in folders:
            url = baseURL if folder == "/" else f"{baseURL}/{folder}"
            res = self._get(url, params,
                               securityHandler=self._securityHandler,
                               proxy_url=self._proxy_url,
                               proxy_port=self._proxy_port)
            if "services" in res:
                for service in res['services']:
                    if service_type == "*":
                        service['URL'] = f"{url}/{service['serviceName']}.{service['type']}"
                        type_services.append(service)
                    if service['type'].lower() in lower_types:
                        service['URL'] = f"{url}/{service['serviceName']}.{service_type}"
                        type_services.append(service)
                    del service
            del res
            del folder
        return type_services
    #----------------------------------------------------------------------
    def addFolderPermission(self, principal, isAllowed=True, folder=None):
        """
           Assigns a new permission to a role (principal). The permission
           on a parent resource is automatically inherited by all child
           resources
           Input:
              principal - name of role to assign/disassign accesss
              isAllowed -  boolean which allows access
           Output:
              JSON message as dictionary
        """
        if folder is not None:
            uURL = f"{self._url}/{folder}//permissions/add"
        else:
            uURL = f"{self._url}/permissions/add"
        params = {
            "f" : "json",
            "principal" : principal,
            "isAllowed" : isAllowed
        }
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def listFolderPermissions(self,folderName):
        """
           Lists principals which have permissions for the folder.
           Input:
              folderName - name of the folder to list permissions for
           Output:
              JSON Message as Dictionary
        """
        uURL = f"{self._url}/{folderName}/permissions"
        params = {
            "f" : "json",
        }
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def cleanPermissions(self, principal):
        """
           Cleans all permissions that have been assigned to a role
           (principal). This is typically used when a role is deleted.
           Input:
              principal - name of the role to clean
           Output:
              JSON Message as Dictionary
        """
        uURL = f"{self._url}/permissions/clean"
        params = {
            "f" : "json",
            "principal" : principal
        }
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def createFolder(self, folderName, description=""):
        """
           Creates a unique folder name on AGS
           Inputs:
              folderName - name of folder on AGS
              description - describes the folder
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "folderName" : folderName,
            "description" : description
        }
        uURL = f"{self._url}/createFolder"
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def deleteFolder(self, folderName):
        """
           deletes a folder on AGS
           Inputs:
              folderName - name of folder to remove
           Output:
              JSON message as dictionary
        """
        if folderName in self.folders:
            uURL = f"{self._url}/{folderName}/deleteFolder"
            params = {
                "f" : "json"
            }
            return self._post(url=uURL, param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        else:
            return {"error" : "folder does not exist"}
    #----------------------------------------------------------------------
    def deleteService(self, serviceName, serviceType, folder=None):
        """
           deletes a service from AGS
           Inputs:
              serviceName - name of the service
              serviceType - type of the service
              folder - name of the folder the service resides, leave None
                       for root.
           Output:
              JSON message as dictionary
        """
        if folder is None:
            uURL = f"{self._url}/{serviceName}.{serviceType}/delete"
        else:
            uURL = f"{self._url}/{folder}/{serviceName}.{serviceType}/delete"
        params = {
            "f" : "json"
        }
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    def service_report(self, folder=None):
        """
           provides a report on all items in a given folder
           Inputs:
              folder - folder to report on given services. None means root
        """
        items = ["description", "status",
                 "instances", "iteminfo",
                 "properties"]
        if folder is None:
            uURL = f"{self._url}/report"
        else:
            uURL = f"{self._url}/{folder}/report"
        params = {
            "f" : "json",
            "parameters" : items
        }
        return self._get(url=uURL, param_dict=params,
                            securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def types(self):
        """ returns the allowed services types """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/types"
        return self._get(url=uURL,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def rename_service(self, serviceName, serviceType,
                       serviceNewName, folder=None):
        """
           Renames a published AGS Service
           Inputs:
              serviceName - old service name
              serviceType - type of service
              serviceNewName - new service name
              folder - location of where the service lives, none means
                       root folder.
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "serviceName" : serviceName,
            "serviceType" : serviceType,
            "serviceNewName" : serviceNewName
        }
        if folder is None:
            uURL = f"{self._url}/renameService"
        else:
            uURL = f"{self._url}/{folder}/renameService"
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def createService(self, service):
        """
        Creates a new GIS service in the folder. A service is created by
        submitting a JSON representation of the service to this operation.
        """
        url = f"{self._url}/createService"
        params = {
            "f" : "json"
        }
        if isinstance(service, str):
            params['service'] = service
        elif isinstance(service, dict):
            params['service'] = json.dumps(service)
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def stopServices(self, services ):
        """
        Stops serveral services on a single server
        Inputs:
           services - is a list of dictionary objects. Each dictionary
                      object is defined as:
                        folderName - The name of the folder containing the
                        service, for example, "Planning". If the service
                        resides in the root folder, leave the folder
                        property blank ("folderName": "").
                        serviceName - The name of the service, for example,
                        "FireHydrants".
                        type - The service type, for example, "MapServer".
                     Example:
                        [{
                          "folderName" : "",
                          "serviceName" : "SampleWorldCities",
                          "type" : "MapServer"
                        }]
        """
        url = f"{self._url}/stopServices"
        if isinstance(services, dict):
            services = [services]
        elif isinstance(services, (list, tuple)):
            services = list(services)
        else:
            Exception("Invalid input for parameter services")
        params = {
            "f" : "json",
            "services" : {
                "services":services
            }
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def startServices(self, services ):
        """
        starts serveral services on a single server
        Inputs:
           services - is a list of dictionary objects. Each dictionary
                      object is defined as:
                        folderName - The name of the folder containing the
                        service, for example, "Planning". If the service
                        resides in the root folder, leave the folder
                        property blank ("folderName": "").
                        serviceName - The name of the service, for example,
                        "FireHydrants".
                        type - The service type, for example, "MapServer".
                     Example:
                        [{
                          "folderName" : "",
                          "serviceName" : "SampleWorldCities",
                          "type" : "MapServer"
                        }]
        """
        url = f"{self._url}/startServices"
        if isinstance(services, dict):
            services = [services]
        elif isinstance(services, (list, tuple)):
            services = list(services)
        else:
            Exception("Invalid input for parameter services")
        params = {
            "f" : "json",
            "services" : {
                "services":services
            }
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def editFolder(self, description, webEncrypted=False):
        """
        This operation allows you to change the description of an existing
        folder or change the web encrypted property.
        The web encrypted property indicates if all the services contained
        in the folder are only accessible over a secure channel (SSL). When
        setting this property to true, you also need to enable the virtual
        directory security in the security configuration.

        Inputs:
           description - a description of the folder
           webEncrypted - boolean to indicate if the services are
            accessible over SSL only.
        """
        url = f"{self._url}/editFolder"
        params = {
            "f": "json",
            "webEncrypted": webEncrypted,
            "description": f"{description}",
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def exists(self, folderName, serviceName=None, serviceType=None):
        """
        This operation allows you to check whether a folder or a service
        exists. To test if a folder exists, supply only a folderName. To
        test if a service exists in a root folder, supply both serviceName
        and serviceType with folderName=None. To test if a service exists
        in a folder, supply all three parameters.

        Inputs:
           folderName - a folder name
           serviceName - a service name
           serviceType - a service type. Allowed values:
                "GPSERVER", "GLOBESERVER", "MAPSERVER",
                "GEOMETRYSERVER", "IMAGESERVER", "SEARCHSERVER",
                "GEODATASERVER", "GEOCODESERVER"
        """

        url = f"{self._url}/exists"
        params = {
            "f" : "json",
            "folderName" : folderName,
            "serviceName" : serviceName,
            "type" : serviceType
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)

########################################################################
class AGSService(BaseAGSServer):
    """ Defines a AGS Admin Service """
    _frameworkProperties = None
    _proxy_port = None
    _proxy_url = None
    _securityHandler = None
    _recycleInterval = None
    _instancesPerContainer = None
    _maxWaitTime = None
    _extensions = None
    _minInstancesPerNode = None
    _maxIdleTime = None
    _maxUsageTime = None
    _allowedUploadFileTypes = None
    _datasets = None
    _properties = None
    _recycleStartTime = None
    _clusterName = None
    _description = None
    _isDefault = None
    _type = None
    _serviceName = None
    _isolationLevel = None
    _capabilities = None
    _loadBalancing = None
    _configuredState = None
    _maxStartupTime = None
    _private = None
    _maxUploadFileSize = None
    _keepAliveInterval = None
    _maxInstancesPerNode = None
    _json = None
    _json_dict = None
    _interceptor = None
    _provider = None
    _portalProperties = None
    _jsonProperties = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 securityHandler,
                 proxy_url=None, proxy_port=None,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               securityHandler - manages site security
               proxy_url - url of proxy
               proxy_port - port value of proxy
               initialize - fills all the properties at object creation is
                            true
        """
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port
        self._url = url
        self._currentURL = url
        self._securityHandler = securityHandler
        if initialize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """ populates server admin information """
        params = {
            "f" : "json"
        }
        json_dict = self._get(url=self._currentURL,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        self._json = json.dumps(json_dict)
        self._json_dict = json_dict
        attributes = [attr for attr in dir(self)
                    if not attr.startswith('__') and \
                        not attr.startswith('_')]
        for k,v in json_dict.items():
            if k.lower() == "extensions":
                self._extensions = []
                for ext in v:
                    self._extensions.append(Extension.fromJSON(ext))
                    del ext
            elif k in attributes:
                setattr(self, f"_{k}", json_dict[k])
            else:
                print( k, " - attribute not implemented in manageags.AGSService.")
            del k
            del v
    #----------------------------------------------------------------------
    def refreshProperties(self):
        """refreshes the object's values by re-querying the service"""
        self.__init()
    #----------------------------------------------------------------------
    def __str__(self):
        """returns a string of the object"""
        if self._json is None:
            self.__init()
            return self._json
        else:
            val = {"serviceName": self._serviceName,
                   "type": self._type,
                   "description": self._description,
                   "capabilities": self._capabilities,
                   "provider": self._provider,
                   "interceptor": self._interceptor,
                   "clusterName": self._clusterName,
                   "minInstancesPerNode": self._minInstancesPerNode,
                   "maxInstancesPerNode": self._maxInstancesPerNode,
                   "instancesPerContainer": self._instancesPerContainer,
                   "maxWaitTime": self._maxWaitTime,
                   "maxStartupTime": self._maxStartupTime,
                   "maxIdleTime": self._maxIdleTime,
                   "maxUsageTime": self._maxUsageTime,
                   "loadBalancing": self._loadBalancing,
                   "isolationLevel": self._isolationLevel,
                   "configuredState": self._configuredState,
                   "recycleInterval": self._recycleInterval,
                   "recycleStartTime": self._recycleStartTime,
                   "keepAliveInterval": self._keepAliveInterval,
                   "private": self._private,
                   "isDefault": self._isDefault,
                   "maxUploadFileSize": self._maxUploadFileSize,
                   "allowedUploadFileTypes": self._allowedUploadFileTypes,
                   "properties": self._properties,
                   "extensions": [e.value for e in self.extensions],
                   "datasets": self._datasets,
                   }
            if self._jsonProperties is not None:
                val["jsonProperties"] = self._jsonProperties
        return json.dumps(val)
    #----------------------------------------------------------------------
    def __iter__(self):
        """class iterator which yields a key/value pair"""
        if self._json_dict is None:
            self.__init()
        yield from self._json_dict.items()
    #----------------------------------------------------------------------
    def jsonProperties(self):
        """returns the jsonProperties"""
        if self._jsonProperties is None:
            self.__init()
        return self._jsonProperties
    #----------------------------------------------------------------------
    @property
    def frameworkProperties(self):
        """returns the framework properties for an AGS instance"""
        if self._frameworkProperties is None:
            self.__init()
        return self._frameworkProperties
    #----------------------------------------------------------------------
    @property
    def portalProperties(self):
        """returns the service's portal properties"""
        if self._portalProperties is None:
            self.__init()
        return self._portalProperties
    #----------------------------------------------------------------------
    @property
    def interceptor(self):
        """returns the interceptor property"""
        if self._interceptor is None:
            self.__init()
        return self._interceptor
    #----------------------------------------------------------------------
    @property
    def provider(self):
        """returns the provider for the service"""
        if self._provider is None:
            self.__init()
        return self._provider
    #----------------------------------------------------------------------
    @property
    def recycleInterval(self):
        if self._recycleInterval is None:
            self.__init()
        return self._recycleInterval
    #----------------------------------------------------------------------
    @property
    def instancesPerContainer(self):
        if self._instancesPerContainer is None:
            self.__init()
        return self._instancesPerContainer
    #----------------------------------------------------------------------
    @property
    def maxWaitTime(self):
        if self._maxWaitTime is None:
            self.__init()
        return self._maxWaitTime
    #----------------------------------------------------------------------
    @property
    def extensions(self):
        if self._extensions is None:
            self.__init()
        return self._extensions
    #----------------------------------------------------------------------
    def modifyExtensions(self,
                         extensionObjects=[]):
        """
        enables/disables a service extension type based on the name
        """

        if len(extensionObjects) > 0 and \
           isinstance(extensionObjects[0], Extension):
            self._extensions = extensionObjects
            res = self.edit(str(self))
            self._json = None
            self.__init()
            return res
    #----------------------------------------------------------------------
    @property
    def minInstancesPerNode(self):
        if self._minInstancesPerNode is None:
            self.__init()
        return self._minInstancesPerNode
    #----------------------------------------------------------------------
    @property
    def maxIdleTime(self):
        if self._maxIdleTime is None:
            self.__init()
        return self._maxIdleTime
    #----------------------------------------------------------------------
    @property
    def maxUsageTime(self):
        if self._maxUsageTime is None:
            self.__init()
        return self._maxUsageTime
    #----------------------------------------------------------------------
    @property
    def allowedUploadFileTypes(self):
        if self._allowedUploadFileTypes is None:
            self.__init()
        return self._allowedUploadFileTypes
    #----------------------------------------------------------------------
    @property
    def datasets(self):
        if self._datasets is None:
            self.__init()
        return self._datasets
    #----------------------------------------------------------------------
    @property
    def properties(self):
        if self._properties is None:
            self.__init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def recycleStartTime(self):
        if self._recycleStartTime is None:
            self.__init()
        return self._recycleStartTime
    #----------------------------------------------------------------------
    @property
    def clusterName(self):
        if self._clusterName is None:
            self.__init()
        return self._clusterName
    #----------------------------------------------------------------------
    @property
    def description(self):
        if self._description is None:
            self.__init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def isDefault(self):
        if self._isDefault is None:
            self.__init()
        return self._isDefault
    #----------------------------------------------------------------------
    @property
    def type(self):
        if self._type is None:
            self.__init()
        return self._type
    #----------------------------------------------------------------------
    @property
    def maxUploadFileSize(self):
        if self._maxUploadFileSize is None:
            self.__init()
        return self._maxUploadFileSize
    #----------------------------------------------------------------------
    @property
    def keepAliveInterval(self):
        if self._keepAliveInterval is None:
            self.__init()
        return self._keepAliveInterval
    #----------------------------------------------------------------------
    @property
    def maxInstancesPerNode(self):
        if self._maxInstancesPerNode is None:
            self.__init()
        return self._maxInstancesPerNode
    #----------------------------------------------------------------------
    @property
    def private(self):
        if self._private is None:
            self.__init()
        return self._private
    #----------------------------------------------------------------------
    @property
    def maxStartupTime(self):
        if self._maxStartupTime is None:
            self.__init()
        return self._maxStartupTime
    #----------------------------------------------------------------------
    @property
    def loadBalancing(self):
        if self._loadBalancing is None:
            self.__init()
        return self._loadBalancing
    #----------------------------------------------------------------------
    @property
    def configuredState(self):
        if self._configuredState is None:
            self.__init()
        return self._configuredState
    #----------------------------------------------------------------------
    @property
    def capabilities(self):
        if self._capabilities is None:
            self.__init()
        return self._capabilities
    #----------------------------------------------------------------------
    @property
    def isolationLevel(self):
        if self._isolationLevel is None:
            self.__init()
        return self._isolationLevel
    #----------------------------------------------------------------------
    @property
    def serviceName(self):
        if self._serviceName is None:
            self.__init()
        return self._serviceName
    #----------------------------------------------------------------------
    def start_service(self):
        """ starts the specific service """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/start"
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def stop_service(self):
        """ stops the current service """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/stop"
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def restart_services(self):
        """ restarts the current service """
        self.stop_service()
        self.start_service()
        return {'status': 'success'}
    #----------------------------------------------------------------------
    def delete_service(self):
        """deletes a service from arcgis server"""
        params = {
            "f" : "json",
        }
        uURL = f"{self._url}/delete"
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the status of the service """
        params = {
            "f" : "json",
        }
        uURL = f"{self._url}/status"
        return self._get(url=uURL, param_dict=params,
                            securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def statistics(self):
        """ returns the stats for the service """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/statistics"
        return self._get(url=uURL, param_dict=params,
                            securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def permissions(self):
        """ returns the permissions for the service """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/permissions"
        return self._get(url=uURL, param_dict=params,
                            securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def iteminfo(self):
        """ returns the item information """
        params = {
            "f" : "json"
        }
        uURL = f"{self._url}/iteminfo"
        return self._get(url=uURL, param_dict=params,
                            securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def itemInfoUpload(self, folder, filePath):
        """
        Allows for the upload of new itemInfo files such as metadata.xml
        Inputs:
           folder - folder on ArcGIS Server
           filePath - full path of the file to upload
        Output:
           json as dictionary
        """
        url = f"{self._url}/iteminfo/upload"
        params = {
            "f" : "json",
            "folder" : folder
        }
        files = {'file': filePath}
        return self._post(url=url,
                          param_dict=params,
                          files=files,
                          securityHandler=self._securityHandler,
                          proxy_url=self._proxy_url,
                          proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def editItemInfo(self, json_dict):
        """
        Allows for the direct edit of the service's item's information.
        To get the current item information, pull the data by calling
        iteminfo property.  This will return the default template then pass
        this object back into the editItemInfo() as a dictionary.

        Inputs:
           json_dict - iteminfo dictionary.
        Output:
           json as dictionary
        """
        url = f"{self._url}/iteminfo/edit"
        params = {
            "f" : "json",
            "serviceItemInfo" : json.dumps(json_dict)
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def serviceManifest(self, fileType="json"):
        """
        The service manifest resource documents the data and other
        resources that define the service origins and power the service.
        This resource will tell you underlying databases and their location
        along with other supplementary files that make up the service.

        Inputs:
           fileType - this can be json or xml. json returns the
            manifest.json file. xml returns the manifest.xml file. These
            files are stored at \arcgisserver\directories\arcgissystem\
            arcgisinput\%servicename%.%servicetype%\extracted folder.

        Outputs:
            Python dictionary if fileType is json and Python object of
            xml.etree.ElementTree.ElementTree type if fileType is xml.
        """

        url = f"{self._url}/iteminfo/manifest/manifest.{fileType}"
        params = {}
        f = self._get(url=url,
                      param_dict=params,
                      securityHandler=self._securityHandler,
                      proxy_url=self._proxy_url,
                      proxy_port=self._proxy_port,
                      out_folder=tempfile.gettempdir(),
                      file_name=os.path.basename(url))
        if fileType == 'json':
            return f
        if fileType == 'xml':
            return ET.ElementTree(ET.fromstring(f))
    #----------------------------------------------------------------------
    def addPermission(self, principal, isAllowed=True):
        """
           Assigns a new permission to a role (principal). The permission
           on a parent resource is automatically inherited by all child
           resources.
           Inputs:
              principal - role to be assigned
              isAllowed - access of resource by boolean
           Output:
              JSON message as dictionary
        """
        uURL = f"{self._url}/permissions/add"
        params = {
            "f" : "json",
            "principal" : principal,
            "isAllowed" : isAllowed
        }
        return self._post(url=uURL, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def edit(self, service):
        """
        To edit a service, you need to submit the complete JSON
        representation of the service, which includes the updates to the
        service properties. Editing a service causes the service to be
        restarted with updated properties.
        """
        url = f"{self._url}/edit"
        params = {
            "f" : "json"
        }
        if isinstance(service, str):
            params['service'] = service
        elif isinstance(service, dict):
            params['service'] = json.dumps(service)
        return self._post(url=url, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
