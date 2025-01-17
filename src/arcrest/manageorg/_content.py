from __future__ import absolute_import
from __future__ import print_function
from ..packages import six
from ..packages.six.moves import urllib_parse as urlparse
from ..security import OAuthSecurityHandler, AGOLTokenSecurityHandler, PortalTokenSecurityHandler
from .._abstract.abstract import BaseAGOLClass
from ._parameters import ItemParameter, BaseParameters, AnalyzeParameters, PublishCSVParameters
from ._community import Group as CommunityGroup
import json
import os
import mmap
import tempfile
import time
from os.path import splitext, basename

########################################################################
class Content(BaseAGOLClass):
    """
    The Portal Content Root operation consists of items, user and group
    content, and feature operations. It is a placeholder URI in that there
    is no response available at this URI. It acts as a root to its child
    resources and operations. All resources and operations (other than
    publicly accessible items) under this URI require an authenticated
    user (or a user token).
    """
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    #----------------------------------------------------------------------
    def __init__(self, url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        self._url = f"{url}/content" if url.lower().find("/content") < 0 else url
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    def __str__(self):
        """returns object as string"""
        return ""
    #----------------------------------------------------------------------
    def __iter__(self):
        """iterates over raw json and returns [key, values]"""
        a = {}
        for k,v in a.items():
            yield [k,v]
    #----------------------------------------------------------------------
    @property
    def root(self):
        """gets the class url"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def users(self):
        """
        Provides access to all user resources
        """
        return Users(
            url=f"{self.root}/users",
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port,
        )
    #----------------------------------------------------------------------
    def getItem(self, itemId):
        """gets the refernce to the Items class which manages content on a
        given AGOL or Portal site.
        """
        url = f"{self.root}/items/{itemId}"
        return Item(url=url,
                    securityHandler=self._securityHandler,
                    proxy_url=self._proxy_url,
                    proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    @property
    def FeatureContent(self):
        """Feature Content class id the parent resource for feature
        operations such as Analyze and Generate."""
        return FeatureContent(
            url=f"{self.root}/features",
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port,
        )

    #----------------------------------------------------------------------
    def group(self, groupId):
        """
        The group's content provides access to the items that are shared
        with the group.
        Group items are stored by reference and are not physically stored
        in a group. Rather, they are stored as links to the original item
        in the item resource (/content/items/<itemId>).
        Available only to the users of the group and the administrator of
        the organization to which the group belongs, if any.

        Inputs:
           groupId - unique group identifier
        """
        url = f"{self._url}/groups/{groupId}"
        return Group(groupId=groupId,
                      contentURL=url,
                      securityHandler=self._securityHandler,
                      proxy_url=self._proxy_url,
                      proxy_port=self._proxy_port)

########################################################################
class Users(BaseAGOLClass):
    """Users allows for the mangements of User content.  This is just a
    class that allows for direct access into users content.
    """
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _json = ""
    _json_dict = {}

    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initalize=False):
        """Constructor"""
        self._url = url
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    @property
    def root(self):
        """returns the base url"""
        return self._url
    #----------------------------------------------------------------------
    def __str__(self):
        """returns raw JSON response as string"""
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        #TODO Implement Iterator for users

        """returns properties (key/values) from the JSON response"""
        yield None
        #if self._json_dict is None:
            #self.__init()
        #for k,v in self._json_dict.items():
            #yield [k,v]
    #----------------------------------------------------------------------
    def __getUsername(self):
        """tries to parse the user name from various objects"""

        if isinstance(self._securityHandler, (AGOLTokenSecurityHandler,
                                              PortalTokenSecurityHandler)):
            return self._securityHandler._username
        elif self._securityHandler is not None and \
               hasattr(self._securityHandler, "org_url") and \
               self._securityHandler.org_url is not None:
            from .administration import Administration
            user = Administration(url=self._securityHandler.org_url,
                                  securityHandler=self._securityHandler,
                                  proxy_url=self._proxy_url,
                                  proxy_port=self._proxy_port).portals.portalSelf.user
            return user['username']
        else:
            from .administration import Administration
            url = self._url.lower().split('/content/')[0]
            user = Administration(url=url,
                                  securityHandler=self._securityHandler,
                                  proxy_url=self._proxy_url,
                                  proxy_port=self._proxy_port).portals.portalSelf.user
            return user['username']

    #----------------------------------------------------------------------
    def user(self, username=None):
        """gets the user's content.  If None is passed, the current user is
        used.

        Input:
         username - name of the login for a given user on a site.
        """
        if username is None:
            username = self.__getUsername()

        url = f"{self.root}/{username}"
        return User(url=url,
                    securityHandler=self._securityHandler,
                    proxy_url=self._proxy_url,
                    proxy_port=self._proxy_port,
                    initalize=True)
########################################################################
class Item(BaseAGOLClass):
    """represents a public view of a given item"""
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    _json_dict = None
    _extent = None
    _culture = None
    _owner = None
    _commentsEnabled = None
    _guid = None
    _numRatings = None
    _numComments = None
    _size = None
    _appCategories = None
    _access = None
    _title = None
    _screenshots = None
    _id = None
    _languages = None
    _snippet = None
    _listed = None
    _largeThumbnail = None
    _type = None
    _thumbnail = None
    _industries = None
    _description = None
    _tags = None
    _typeKeywords = None
    _avgRating = None
    _banner = None
    _properties = None
    _ownerFolder = None
    _name = None
    _licenseInfo = None
    _created = None
    _url = None
    _documentation = None
    _modified = None
    _spatialReference = None
    _protected = None
    _numViews = None
    _accessInformation = None
    _orgId = None
    _itemControl = None
    _sourceUrl = None
    _itemType = None
    _uploaded = None
    _lastModified = None
    _item = None
    _privateUrl = None
    _proxyFilter = None
    _categories = None
    #----------------------------------------------------------------------
    def __init__(self,url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initalize=False):
        """Constructor"""
        self._curl = url
        self._securityHandler = securityHandler
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port
        if initalize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        json_dict = self._get(url=self._curl,
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
            if k in attributes:
                setattr(self, f"_{k}", json_dict[k])
            else:
                print( k, " - attribute not implemented in Item class.")

    def orgId(self):
        '''gets the property value for orgId'''
        if self._orgId is None:
            self.__init()
        return self._orgId
    #----------------------------------------------------------------------
    @property
    def categories(self):
        """returns information about the proxy filter"""
        if self._categories is None:
            self.__init()
        return self._categories
    #----------------------------------------------------------------------
    @property
    def proxyFilter(self):
        """returns information about the proxy filter"""
        if self._proxyFilter is None:
            self.__init()
        return self._proxyFilter
    #----------------------------------------------------------------------
    @property
    def itemType(self):
        '''gets the property value for itemType'''
        if self._itemType is None:
            self.__init()
        return self._itemType
    #----------------------------------------------------------------------
    @property
    def uploaded(self):
        '''gets the property value for uploaded'''
        if self._uploaded is None:
            self.__init()
        return self._uploaded
    #----------------------------------------------------------------------
    @property
    def lastModified(self):
        '''gets the property value for lastModified'''
        if self._lastModified is None:
            self.__init()
        return self._lastModified
    #----------------------------------------------------------------------
    @property
    def item(self):
        '''gets the property value for item'''
        if self._item is None:
            self.__init()
        return self._item
    #----------------------------------------------------------------------
    @property
    def privateUrl(self):
        '''gets the property value for privateUrl'''
        if self._privateUrl is None:
            self.__init()
        return self._privateUrl
    #----------------------------------------------------------------------
    def itemControl(self):
        '''gets the property value for itemControl'''
        if self._itemControl is None:
            self.__init()
        return self._itemControl
    #----------------------------------------------------------------------
    @property
    def extent(self):
        '''gets the property value for extent'''
        if self._extent is None:
            self.__init()
        return self._extent

    #----------------------------------------------------------------------
    @property
    def culture(self):
        '''gets the property value for culture'''
        if self._culture is None:
            self.__init()
        return self._culture

    #----------------------------------------------------------------------
    @property
    def owner(self):
        '''gets the property value for owner'''
        if self._owner is None:
            self.__init()
        return self._owner

    #----------------------------------------------------------------------
    @property
    def commentsEnabled(self):
        '''gets the property value for commentsEnabled'''
        if self._commentsEnabled is None:
            self.__init()
        return self._commentsEnabled

    #----------------------------------------------------------------------
    @property
    def guid(self):
        '''gets the property value for guid'''
        if self._guid is None:
            self.__init()
        return self._guid

    #----------------------------------------------------------------------
    @property
    def numRatings(self):
        '''gets the property value for numRatings'''
        if self._numRatings is None:
            self.__init()
        return self._numRatings

    #----------------------------------------------------------------------
    @property
    def numComments(self):
        '''gets the property value for numComments'''
        if self._numComments is None:
            self.__init()
        return self._numComments

    #----------------------------------------------------------------------
    @property
    def size(self):
        '''gets the property value for size'''
        if self._size is None:
            self.__init()
        return self._size

    #----------------------------------------------------------------------
    @property
    def appCategories(self):
        '''gets the property value for appCategories'''
        if self._appCategories is None:
            self.__init()
        return self._appCategories

    #----------------------------------------------------------------------
    @property
    def access(self):
        '''gets the property value for access'''
        if self._access is None:
            self.__init()
        return self._access

    #----------------------------------------------------------------------
    @property
    def title(self):
        '''gets the property value for title'''
        if self._title is None:
            self.__init()
        return self._title

    #----------------------------------------------------------------------
    @property
    def screenshots(self):
        '''gets the property value for screenshots'''
        if self._screenshots is None:
            self.__init()
        return self._screenshots

    #----------------------------------------------------------------------
    @property
    def id(self):
        '''gets the property value for id'''
        if self._id is None:
            self.__init()
        return self._id

    #----------------------------------------------------------------------
    @property
    def languages(self):
        '''gets the property value for languages'''
        if self._languages is None:
            self.__init()
        return self._languages

    #----------------------------------------------------------------------
    @property
    def snippet(self):
        '''gets the property value for snippet'''
        if self._snippet is None:
            self.__init()
        return self._snippet

    #----------------------------------------------------------------------
    @property
    def listed(self):
        '''gets the property value for listed'''
        if self._listed is None:
            self.__init()
        return self._listed

    #----------------------------------------------------------------------
    @property
    def largeThumbnail(self):
        '''gets the property value for largeThumbnail'''
        if self._largeThumbnail is None:
            self.__init()
        return self._largeThumbnail

    #----------------------------------------------------------------------
    @property
    def type(self):
        '''gets the property value for type'''
        if self._type is None:
            self.__init()
        return self._type

    #----------------------------------------------------------------------
    @property
    def thumbnail(self):
        '''gets the property value for thumbnail'''
        if self._thumbnail is None:
            self.__init()
        return self._thumbnail
    #----------------------------------------------------------------------
    def saveThumbnail(self,fileName,filePath):
        """ URL to the thumbnail used for the item """
        if self._thumbnail is None:
            self.__init()
        if self._thumbnail is not None:
            imgUrl = f"{self.root}/info/{self._thumbnail}"
            onlineFileName, file_ext = splitext(self._thumbnail)
            fileNameSafe = "".join(x for x in fileName if x.isalnum()) + file_ext
            param_dict = {}
            return self._get(
                url=imgUrl,
                param_dict=param_dict,
                securityHandler=self._securityHandler,
                proxy_url=self._proxy_url,
                proxy_port=self._proxy_port,
                out_folder=filePath,
                file_name=fileNameSafe,
            )
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def industries(self):
        '''gets the property value for industries'''
        if self._industries is None:
            self.__init()
        return self._industries

    #----------------------------------------------------------------------
    @property
    def description(self):
        '''gets the property value for description'''
        if self._description is None:
            self.__init()
        return self._description

    #----------------------------------------------------------------------
    @property
    def tags(self):
        '''gets the property value for tags'''
        if self._tags is None:
            self.__init()
        return self._tags

    #----------------------------------------------------------------------
    @property
    def typeKeywords(self):
        '''gets the property value for typeKeywords'''
        if self._typeKeywords is None:
            self.__init()
        return self._typeKeywords

    #----------------------------------------------------------------------
    @property
    def avgRating(self):
        '''gets the property value for avgRating'''
        if self._avgRating is None:
            self.__init()
        return self._avgRating

    #----------------------------------------------------------------------
    @property
    def banner(self):
        '''gets the property value for banner'''
        if self._banner is None:
            self.__init()
        return self._banner

    #----------------------------------------------------------------------
    @property
    def properties(self):
        '''gets the property value for properties'''
        if self._properties is None:
            self.__init()
        return self._properties

    #----------------------------------------------------------------------
    @property
    def ownerFolder(self):
        '''gets the property value for ownerFolder'''
        if self._ownerFolder is None:
            self.__init()
        return self._ownerFolder

    #----------------------------------------------------------------------
    @property
    def name(self):
        '''gets the property value for name'''
        if self._name is None:
            self.__init()
        return self._name

    #----------------------------------------------------------------------
    @property
    def licenseInfo(self):
        '''gets the property value for licenseInfo'''
        if self._licenseInfo is None:
            self.__init()
        return self._licenseInfo

    #----------------------------------------------------------------------
    @property
    def created(self):
        '''gets the property value for created'''
        if self._created is None:
            self.__init()
        return self._created

    #----------------------------------------------------------------------
    @property
    def url(self):
        '''gets the property value for url'''
        if self._url is None:
            self.__init()
        return self._url

    #----------------------------------------------------------------------
    @property
    def documentation(self):
        '''gets the property value for documentation'''
        if self._documentation is None:
            self.__init()
        return self._documentation

    #----------------------------------------------------------------------
    @property
    def modified(self):
        '''gets the property value for modified'''
        if self._modified is None:
            self.__init()
        return self._modified

    #----------------------------------------------------------------------
    @property
    def spatialReference(self):
        '''gets the property value for spatialReference'''
        if self._spatialReference is None:
            self.__init()
        return self._spatialReference

    #----------------------------------------------------------------------
    @property
    def protected(self):
        '''gets the property value for protected'''
        if self._protected is None:
            self.__init()
        return self._protected

    #----------------------------------------------------------------------
    @property
    def numViews(self):
        '''gets the property value for numViews'''
        if self._numViews is None:
            self.__init()
        return self._numViews

    #----------------------------------------------------------------------
    @property
    def accessInformation(self):
        '''gets the property value for accessInformation'''
        if self._accessInformation is None:
            self.__init()
        return self._accessInformation

    #----------------------------------------------------------------------
    @property
    def root(self):
        """returns the base url"""
        return self._curl
    #----------------------------------------------------------------------
    def refresh(self):
        """refreshes the item class properties"""
        self.__init()
    #----------------------------------------------------------------------
    @property
    def userItem(self):
        """returns a reference to the UserItem class"""
        if self.ownerFolder is not None:
            url = f"{self.root.split('/items/')[0]}/users/{self.owner}/{self.ownerFolder}/items/{self.id}"
        else:
            url = f"{self.root.split('/items/')[0]}/users/{self.owner}/items/{self.id}"
        return UserItem(url=url,
                        securityHandler=self._securityHandler,
                        proxy_url=self._proxy_url,
                        proxy_port=self._proxy_port)

    #----------------------------------------------------------------------
    def __str__(self):
        """returns raw JSON response as string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        """returns properties (key/values) from the JSON response"""
        if self._json_dict is None:
            self.__init()
        for k,v in self._json_dict.items():
            yield [k,v]
    #----------------------------------------------------------------------
    @property
    def groups(self):
        """ returns a list of groups the item is shared with. """
        url = f"{self.root}/groups"
        params = {
            "f": "json",
        }
        return self._get(url,
                             params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def rating(self):
        """ returns the items rating on the portal """
        url = f"{self.root}/rating"
        params = {
            "f": "json",
        }
        return self._get(url,
                             params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def itemData(self, f=None, savePath=None):
        """ returns data for an item on agol/portal

        Inputs:
           f - output format either zip of json
           savePath - location to save the file
        Output:
           either JSON/text or filepath
        """

        params = {
        }
        if f is not None and \
               f.lower() in ['zip', 'json']:
            params['f'] = f
        url = f"{self.root}/data"
        if self.type not in [
            "Shapefile",
            "CityEngine Web Scene",
            "Web Scene",
            "KML",
            "Code Sample",
            "Code Attachment",
            "Operations Dashboard Add In",
            "CSV",
            "CSV Collection",
            "CAD Drawing",
            "Service Definition",
            "Microsoft Word",
            "Microsoft Powerpoint",
            "Microsoft Excel",
            "PDF",
            "Image",
            "Visio Document",
            "iWork Keynote",
            "iWork Pages",
            "iWork Numbers",
            "Map Document",
            "Map Package",
            "Basemap Package",
            "Tile Package",
            "Project Package",
            "Task File",
            "ArcPad Package",
            "Explorer Map",
            "Globe Document",
            "Scene Document",
            "Published Map",
            "Map Template",
            "Windows Mobile Package",
            "Pro Map",
            "Layout",
            "Layer",
            "Layer Package",
            "File Geodatabase",
            "Explorer Layer",
            "Geoprocessing Package",
            "Geoprocessing Sample",
            "Locator Package",
            "Rule Package",
            "Workflow Manager Package",
            "Desktop Application",
            "Desktop Application Template",
            "Code Sample",
            "Desktop Add In",
            "Explorer Add In",
            "ArcGIS Desktop Add-In",
            "ArcGIS Explorer Add-In",
            "ArcGIS Explorer application configuration",
            "ArcGIS Explorer document",
        ]:
            return self._get(
                url,
                params,
                proxy_port=self._proxy_port,
                securityHandler=self._securityHandler,
                proxy_url=self._proxy_url,
            )
        if savePath is None:
            raise AttributeError(
                f'savePath must be provided for a item of type: {self.type}'
            )
        if os.path.isdir(savePath) == False:
            os.makedirs(savePath)
        return self._get(
            url=url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port,
            out_folder=savePath,
            file_name=self.name,
        )
    #----------------------------------------------------------------------
    def addRating(self, rating=5.0):
        """Adds a rating to an item between 1.0 and 5.0"""
        if rating > 5.0:
            rating = 5.0
        elif rating < 1.0:
            rating = 1.0
        url = f"{self.root}/addRating"
        params = {"f": "json", "rating": f"{rating}"}
        return self._post(url,
                             params,
                             proxy_port=self._proxy_port,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteRating(self):
        """Removes the rating the calling user added for the specified item
        (POST only)."""
        url = f"{self.root}/deleteRating"
        params = {
            "f": "json",
        }
        return self._post(url,
                             params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def addComment(self, comment):
        """ adds a comment to a given item.  Must be authenticated """
        url = f"{self.root}/addComment"
        params = {
            "f" : "json",
            "comment" : comment
        }
        return self._post(url, params, proxy_port=self._proxy_port,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def itemComment(self, commentId):
        """ returns details of a single comment """
        url = f"{self.root}/comments/{commentId}"
        params = {
            "f": "json"
        }
        return self._get(url,
                            params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def itemComments(self):
        """ returns all comments for a given item """
        url = f"{self.root}/comments/"
        params = {
            "f": "json"
        }
        return self._get(url,
                            params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteComment(self, commentId):
        """ removes a comment from an Item

        Inputs:
           commentId - unique id of comment to remove
        """
        url = f"{self.root}/comments/{commentId}/delete"
        params = {
            "f": "json",
        }
        return self._post(url,
                             params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    @property
    def sourceUrl(self):
        '''gets the property value for sourceUrl'''
        if self._sourceUrl is None:
            self.__init()
        return self._sourceUrl
    #----------------------------------------------------------------------
    def shareItem(self,
                  groups="",
                  everyone=False,
                  org=False):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong.
        This operation also allows a user to share items with everyone, in
        which case the items are publicly accessible, or with everyone in
        their organization.

        Inputs:
           groups - comma seperate list of group Ids
           everyone - boolean, true means share with all
           org - boolean trues means share with orginization
        """
        params = {
            "f": "json",
            "everyone" : everyone,
            "org" : org
        }
        if groups != "" and groups is not None:
            params['groups'] = groups
        url = f"{self.root}/share"
        res =  self._post(
            url = url,
            securityHandler=self._securityHandler,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
        self.__init()
        return res
    #----------------------------------------------------------------------
    def unshareItem(self, groups):
        """
        Stops sharing the item with the specified list of groups

        Inputs:
           groups - comma seperated list of Ids
        """
        params = {
            "f": "json",
            "groups" : groups
        }
        url = f"{self.root}/unshare"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def itemInfoFile(self):
        """  """
        url = f"{self.root}/info/iteminfo.xml"
        xml = self._get(url=url,
                        param_dict={},
                        securityHandler=self._securityHandler,
                        proxy_url=self._proxy_url,
                        proxy_port=self._proxy_port,
                        out_folder=os.environ['TEMP'],
                        file_name="iteminfo.xml")
        text = open(xml, 'rb').read()
        os.remove(xml)
        return text
    #----------------------------------------------------------------------
    @property
    def packageInfo(self):
        """gets the item's package information file"""
        url = f"{self.root}/item.pkinfo"
        params = {'f' : 'json'}
        return self._get(
            url=url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port,
            out_folder=tempfile.gettempdir(),
        )
    #----------------------------------------------------------------------
    def metadata(self,
                 exportFormat="default",
                 output=None,
                 saveFolder=None,
                 fileName=None):
        """
        exports metadata to the various supported formats
        Inputs:
          exportFormats - export metadata to the following formats: fgdc,
           inspire, iso19139, iso19139-3.2, iso19115, arcgis, and default.
           default means the value will be ISO 19139 Metadata
           Implementation Specification GML3.2 or the default format set
           for your ArcGIS online organizational account.
          output - html or none.  Html returns values as html text.
          saveFolder - Default is None. If provided the metadata file will
           be saved to that location.
          fileName - Default is None. If provided, this will be the name of
           the file on your local drive.
        Output:
         path to file or string
        """
        url = f"{self.root}/info/metadata/metadata.xml"
        allowedFormats = ["fgdc", "inspire", "iso19139",
                          "iso19139-3.2", "iso19115", "arcgis", "default"]
        if exportFormat.lower() not in allowedFormats:
            raise Exception("Invalid exportFormat")
        params = (
            {} if exportFormat.lower() == "arcgis" else {"format": exportFormat}
        )
        if exportFormat.lower() == "default":
            exportFormat = ""
        params = {
            "format" : exportFormat
        }
        if output is not None:
            params['output'] = output
        if saveFolder is None:
            saveFolder = tempfile.gettempdir()
        if fileName is None:
            fileName = "metadata.xml"
        if output is not None:
            return self._post(url=url,
                                param_dict=params,
                                securityHandler=self._securityHandler,
                                proxy_url=self._proxy_url,
                                proxy_port=self._proxy_port)
        result = self._get(url=url,
                           param_dict=params,
                           securityHandler=self._securityHandler,
                           proxy_url=self._proxy_url,
                           proxy_port=self._proxy_port,
                           out_folder=saveFolder,
                           file_name=fileName)
        if os.path.isfile(result) == False:
            with open(os.path.join(saveFolder, fileName), 'wb') as writer:
                writer.write(result)
                writer.flush()
                writer.close()
            return os.path.join(saveFolder, fileName)

        return result
    #----------------------------------------------------------------------
    def deleteInfo(self, infoFile="metadata/metadata.xml"):
        """
        deletes the info information for a given item.
        Input:
          infoFile - the file to erase.
           Example: metadata/metadata.xml is the xml file on the item
        Output:
         dictionary
        """
        url = f"{self.root}/deleteInfo"
        params = {
        "f" : "json",
        "infoFile" : infoFile
        }
        return self._post(url=url, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def updateMetadata(self, metadataFile):
        """
        updates or adds the current item's metadata
        metadataFile is the path to the XML file to upload.
        Output:
         dictionary
        """
        ip = ItemParameter()
        ip.metadata = metadataFile
        res = self.userItem.updateItem(itemParameters=ip,
                                       metadata=metadataFile)
        del ip
        return res
########################################################################
class UserItem(BaseAGOLClass):
    """represents a single item on the site for a given user"""
    _appProxies = None
    _serviceProxyParams = None
    _url = None
    _itemType = None
    _uploaded = None
    _lastModified = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    _json_dict = None
    _sharing = None
    _contentURL = None
    _extent = None
    _culture = None
    _owner = None
    _guid = None
    _numRatings = None
    _numComments = None
    _size = None
    _appCategories = None
    _access = None
    _title = None
    _screenshots = None
    _id = None
    _languages = None
    _snippet = None
    _listed = None
    _largeThumbnail = None
    _type = None
    _thumbnail = None
    _industries = None
    _description = None
    _tags = None
    _typeKeywords = None
    _avgRating = None
    _banner = None
    _properties = None
    _ownerFolder = None
    _name = None
    _licenseInfo = None
    _created = None
    _url = None
    _documentation = None
    _modified = None
    _spatialReference = None
    _protected = None
    _numViews = None
    _accessInformation = None
    _sourceUrl = None
    __curl = None
    _privateUrl = None
    _itemControl = None
    _origin = None
    _proxyFilter = None
    _categories = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initalize=False):
        """Constructor"""
        self._curl = url
        self._contentURL = f"{url.split('/users/')[0]}/items/{os.path.basename(url)}"
        self._securityHandler = securityHandler
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port
        if initalize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        json_dict = self._get(url=self.root,
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
            if k == "item":
                for key,value in v.items():
                    if key in attributes:
                        setattr(self, f"_{key}", value)
                    else:
                        print( key, " - attribute not implemented in UserItem class.")
            elif k in attributes:
                setattr(self, f"_{k}", json_dict[k])
            else:
                print( k, " - attribute not implemented in UserItem class.")
    #----------------------------------------------------------------------
    def refresh(self):
        """ refreshes the UserItem properties """
        self.__init()
    #----------------------------------------------------------------------
    @property
    def itemType(self):
        """gets the item type"""
        if self._itemType is None:
            self.__init()
        return self._itemType
    #----------------------------------------------------------------------
    @property
    def uploaded(self):
        """gets the item type"""
        if self._uploaded is None:
            self.__init()
        return self._uploaded
    #----------------------------------------------------------------------
    @property
    def lastModified(self):
        """gets the item type"""
        if self._lastModified is None:
            self.__init()
        return self._lastModified
    #----------------------------------------------------------------------
    @property
    def itemControl(self):
        '''gets the property value for itemControl'''
        if self._itemControl is None:
            self.__init()
        return self._itemControl
    #----------------------------------------------------------------------
    @property
    def origin(self):
        '''gets the property value for origin'''
        if self._origin is None:
            self.__init()
        return self._origin
    #----------------------------------------------------------------------
    @property
    def extent(self):
        '''gets the property value for extent'''
        if self._extent is None:
            self.__init()
        return self._extent
    #----------------------------------------------------------------------
    @property
    def privateUrl(self):
        '''gets the property value for privateUrl'''
        if self._privateUrl is None:
            self.__init()
        return self._privateUrl
    #----------------------------------------------------------------------
    @property
    def culture(self):
        '''gets the property value for culture'''
        if self._culture is None:
            self.__init()
        return self._culture
    #----------------------------------------------------------------------
    @property
    def owner(self):
        '''gets the property value for owner'''
        if self._owner is None:
            self.__init()
        return self._owner
    #----------------------------------------------------------------------
    @property
    def guid(self):
        '''gets the property value for guid'''
        if self._guid is None:
            self.__init()
        return self._guid
    #----------------------------------------------------------------------
    @property
    def numRatings(self):
        '''gets the property value for numRatings'''
        if self._numRatings is None:
            self.__init()
        return self._numRatings
    #----------------------------------------------------------------------
    @property
    def numComments(self):
        '''gets the property value for numComments'''
        if self._numComments is None:
            self.__init()
        return self._numComments
    #----------------------------------------------------------------------
    @property
    def size(self):
        '''gets the property value for size'''
        if self._size is None:
            self.__init()
        return self._size
    #----------------------------------------------------------------------
    @property
    def appCategories(self):
        '''gets the property value for appCategories'''
        if self._appCategories is None:
            self.__init()
        return self._appCategories
    #----------------------------------------------------------------------
    @property
    def access(self):
        '''gets the property value for access'''
        if self._access is None:
            self.__init()
        return self._access
    #----------------------------------------------------------------------
    @property
    def title(self):
        '''gets the property value for title'''
        if self._title is None:
            self.__init()
        return self._title
    #----------------------------------------------------------------------
    @property
    def screenshots(self):
        '''gets the property value for screenshots'''
        if self._screenshots is None:
            self.__init()
        return self._screenshots
    #----------------------------------------------------------------------
    @property
    def id(self):
        '''gets the property value for id'''
        if self._id is None:
            self.__init()
        return self._id
    #----------------------------------------------------------------------
    @property
    def languages(self):
        '''gets the property value for languages'''
        if self._languages is None:
            self.__init()
        return self._languages
    #----------------------------------------------------------------------
    @property
    def snippet(self):
        '''gets the property value for snippet'''
        if self._snippet is None:
            self.__init()
        return self._snippet
    #----------------------------------------------------------------------
    @property
    def listed(self):
        '''gets the property value for listed'''
        if self._listed is None:
            self.__init()
        return self._listed
    #----------------------------------------------------------------------
    @property
    def largeThumbnail(self):
        '''gets the property value for largeThumbnail'''
        if self._largeThumbnail is None:
            self.__init()
        return self._largeThumbnail
    #----------------------------------------------------------------------
    @property
    def type(self):
        '''gets the property value for type'''
        if self._type is None:
            self.__init()
        return self._type
    #----------------------------------------------------------------------
    @property
    def thumbnail(self):
        '''gets the property value for thumbnail'''
        if self._thumbnail is None:
            self.__init()
        return self._thumbnail
    #----------------------------------------------------------------------
    @property
    def industries(self):
        '''gets the property value for industries'''
        if self._industries is None:
            self.__init()
        return self._industries
    #----------------------------------------------------------------------
    @property
    def description(self):
        '''gets the property value for description'''
        if self._description is None:
            self.__init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def tags(self):
        '''gets the property value for tags'''
        if self._tags is None:
            self.__init()
        return self._tags
    #----------------------------------------------------------------------
    @property
    def typeKeywords(self):
        '''gets the property value for typeKeywords'''
        if self._typeKeywords is None:
            self.__init()
        return self._typeKeywords
    #----------------------------------------------------------------------
    @property
    def avgRating(self):
        '''gets the property value for avgRating'''
        if self._avgRating is None:
            self.__init()
        return self._avgRating
    #----------------------------------------------------------------------
    @property
    def banner(self):
        '''gets the property value for banner'''
        if self._banner is None:
            self.__init()
        return self._banner
    #----------------------------------------------------------------------
    @property
    def properties(self):
        '''gets the property value for properties'''
        if self._properties is None:
            self.__init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def ownerFolder(self):
        '''gets the property value for ownerFolder'''
        if self._ownerFolder is None:
            self.__init()
        return self._ownerFolder
    #----------------------------------------------------------------------
    @property
    def name(self):
        '''gets the property value for name'''
        if self._name is None:
            self.__init()
        return self._name
    #----------------------------------------------------------------------
    @property
    def licenseInfo(self):
        '''gets the property value for licenseInfo'''
        if self._licenseInfo is None:
            self.__init()
        return self._licenseInfo
    #----------------------------------------------------------------------
    @property
    def created(self):
        '''gets the property value for created'''
        if self._created is None:
            self.__init()
        return self._created
    #----------------------------------------------------------------------
    @property
    def url(self):
        '''gets the property value for url'''
        if self._url is None:
            self.__init()
        return self._url
    #----------------------------------------------------------------------
    @property
    def documentation(self):
        '''gets the property value for documentation'''
        if self._documentation is None:
            self.__init()
        return self._documentation
    #----------------------------------------------------------------------
    @property
    def modified(self):
        '''gets the property value for modified'''
        if self._modified is None:
            self.__init()
        return self._modified
    #----------------------------------------------------------------------
    @property
    def spatialReference(self):
        '''gets the property value for spatialReference'''
        if self._spatialReference is None:
            self.__init()
        return self._spatialReference
    #----------------------------------------------------------------------
    @property
    def protected(self):
        '''gets the property value for protected'''
        if self._protected is None:
            self.__init()
        return self._protected
    #----------------------------------------------------------------------
    @property
    def numViews(self):
        '''gets the property value for numViews'''
        if self._numViews is None:
            self.__init()
        return self._numViews
    #----------------------------------------------------------------------
    @property
    def accessInformation(self):
        '''gets the property value for accessInformation'''
        if self._accessInformation is None:
            self.__init()
        return self._accessInformation
    #----------------------------------------------------------------------
    @property
    def sourceUrl(self):
        """gets the property value for sourceUrl"""
        if self._sourceUrl is None:
            self.__init()
        return self._sourceUrl
    #----------------------------------------------------------------------
    @property
    def appProxies(self):
        if self._appProxies is None:
            self.__init()
        return self._appProxies
    #----------------------------------------------------------------------
    @property
    def serviceProxyParams(self):
        if self._serviceProxyParams is None:
            self.__init()
        return self._serviceProxyParams
    #----------------------------------------------------------------------
    @property
    def categories(self):
        if self._categories is None:
            self.__init()
        return self._categories
    #----------------------------------------------------------------------
    @property
    def proxyFilter(self):
        if self._proxyFilter is None:
            self.__init()
        return self._proxyFilter
    #----------------------------------------------------------------------
    @property
    def item(self):
        """returns the Item class of an Item"""
        url = self._contentURL
        return Item(url=self._contentURL,
                    securityHandler=self._securityHandler,
                    proxy_url=self._proxy_url,
                    proxy_port=self._proxy_port,
                    initalize=True)
    #----------------------------------------------------------------------
    @property
    def sharing(self):
        """gets the item's sharing information"""
        if self._sharing is None:
            self.__init()
        return self._sharing
    #----------------------------------------------------------------------
    @property
    def root(self):
        """returns the base url"""
        return self._curl
    #----------------------------------------------------------------------
    def __str__(self):
        """returns raw JSON response as string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        """returns properties (key/values) from the JSON response"""
        if self._json_dict is None:
            self.__init()
        for k,v in self._json_dict.items():
            yield [k,v]
    #----------------------------------------------------------------------
    def deleteItem(self):
        """
        The Delete Item operation (POST only) removes both the item and its
        link from the user's folder by default. This operation is available
        to the user and to the administrator of the organization to which
        the user belongs.

        """
        params = {
            "f" : "json"
        }
        url = f"{self.root}/delete"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def moveItem(self, folder="/"):
        """
        The Move Item operation moves the item (link) from the current
        folder to the specified target folder. Moving an item link does not
        change the URI of the item itself, which continues to be
        /content/items/<itemId>.

        Inputs:
           folder - the destination folder ID for the item. If the item is
                    to be moved to the root folder, specify the value as /
                    (forward slash).

                    Example 1: folder=/ (move to root folder)
                    Example 2: folder=1a9ad803da604628b08c968ce602a231
                    (move to folder with ID 1a9ad803da604628b08c968ce602a231)
        """
        params = {
            "f" : "json",
            "folder" : folder
        }
        url = f"{self.root}/move"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def protect(self):
        """
        The Protect operation protects the items from deletion. This
        operation is available to the user and to the administrator of the
        organization to which the user belongs
        """
        params = {
            "f" : "json"
        }
        url = f"{self.root}/protect"
        return self._post(
            url = url,
            securityHandler=self._securityHandler,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def reassignItem(self,
                     targetUsername,
                     targetFoldername):
        """
        The Reassign Item operation allows the administrator of an
        organization to reassign a member's item to another member of the
        organization.

        Inputs:
           targetUsername - The target username of the new owner of the
                            item
           targetFoldername - The destination folder for the item. If the
                              item is to be moved to the root folder,
                              specify the value as "/" (forward slash). If
                              the target folder doesn't exist, it will be
                              created automatically.
        """
        params = {
            "f" : "json",
            "targetUsername" : targetUsername,
            "targetFoldername" : targetFoldername
        }
        url = f"{self.root}/reassign"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def shareItem(self,
                  everyone=False,
                  org=False,
                  groups=""):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong.
        This operation also allows a user to share items with everyone, in
        which case the items are publicly accessible, or with everyone in
        their organization.

        Inputs:
           groups - comma seperate list of group Ids
           everyone - boolean, true means share with all
           org - boolean trues means share with orginization
        """
        params = {
            "f": "json",
            "everyone" : everyone,
            "org" : org
        }
        if groups != "" and groups is not None:
            params['groups'] = groups
        url = f"{self.root}/share"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def unprotect(self):
        """
        The Unprotect operation disables the item protection from deletion.
        """
        params = {
            "f": "json"
        }
        url = f"{self.root}/unprotect"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def unshareItem(self, groups):
        """
        Stops sharing the item with the specified list of groups. Available
        to the user and the administrator of the organization to which the
        user belongs, if any.

        Inputs:
           groups - comma seperated list of group Ids
        """
        params = {
            "f": "json",
            "groups": groups

        }
        url = f"{self.root}/unshare"
        return self._post(
            url = url,
            param_dict=params,
            securityHandler=self._securityHandler,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def updateItem(self,
                   itemParameters,
                   clearEmptyFields=False,
                   data=None,
                   metadata=None,
                   text=None,
                   serviceUrl=None,
                   multipart=False):
        """
        updates an item's properties using the ItemParameter class.

        Inputs:
           itemParameters - property class to update
           clearEmptyFields - boolean, cleans up empty values
           data - updates the file property of the service like a .sd file
           metadata - this is an xml file that contains metadata information
           text - The text content for the item to be updated.
           serviceUrl - this is a service url endpoint.
           multipart - this is a boolean value that means the file will be
              broken up into smaller pieces and uploaded.
        """
        thumbnail = None
        largeThumbnail = None
        files = {}
        params = {
            "f": "json",

        }
        if clearEmptyFields:
            params["clearEmptyFields"] = clearEmptyFields
        if serviceUrl is not None:
            params['url'] = serviceUrl
        if text is not None:
            params['text'] = text
        if not isinstance(itemParameters, ItemParameter):
            raise AttributeError("itemParameters must be of type parameter.ItemParameter")
        keys_to_delete = ['id', 'owner', 'size', 'numComments',
                          'numRatings', 'avgRating', 'numViews' ,
                          'overwrite']
        dictItem = itemParameters.value
        for key in keys_to_delete:
            if key in dictItem:
                del dictItem[key]

        for key in dictItem:
            if key == "largeThumbnail":
                files['largeThumbnail'] = dictItem['largeThumbnail']
            elif key == "metadata":
                metadata = dictItem['metadata']
                if os.path.basename(metadata) != 'metadata.xml':
                    tempxmlfile = os.path.join(tempfile.gettempdir(), "metadata.xml")
                    if os.path.isfile(tempxmlfile) == True:
                        os.remove(tempxmlfile)
                    import shutil
                    shutil.copy(metadata, tempxmlfile)

                    metadata = tempxmlfile
                files['metadata'] = dictItem['metadata']
            elif key == "thumbnail":
                files['thumbnail'] = dictItem['thumbnail']
            else:
                params[key] = dictItem[key]
        if data is not None:
            files['file'] = data
        if metadata and os.path.isfile(metadata):
            files['metadata'] = metadata
        url = f"{self.root}/update"
        if multipart:
            itemID = self.id
            params['multipart'] = True
            params['fileName'] = os.path.basename(data)
            res = self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
            itemPartJSON = self.addByPart(filePath=data)
            res = self.commit(wait=True, additionalParams=\
                                  {'type' : self.type })

        else:
            res = self._post(url=url,
                 param_dict=params,
                 files=files,
                 securityHandler=self._securityHandler,
                 proxy_url=self._proxy_url,
                 proxy_port=self._proxy_port,
                 force_form_post=True)
        self.__init()
        return self
    #----------------------------------------------------------------------
    def deleteInfo(self, infoFile="metadata/metadata.xml"):
        """
        deletes the info information for a given item.
        Input:
          infoFile - the file to erase.
           Example: metadata/metadata.xml is the xml file on the item
        Output:
         dictionary
        """
        url = f"{self.root}/deleteInfo"
        params = {
        "f" : "json",
        "infoFile" : infoFile
        }
        return self._post(url=url, param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def status(self, jobId=None, jobType=None):
        """
           Inquire about status when publishing an item, adding an item in
           async mode, or adding with a multipart upload. "Partial" is
           available for Add Item Multipart, when only a part is uploaded
           and the item is not committed.

           Input:
              jobType The type of asynchronous job for which the status has
                      to be checked. Default is none, which check the
                      item's status.  This parameter is optional unless
                      used with the operations listed below.
                      Values: publish, generateFeatures, export,
                              and createService
              jobId - The job ID returned during publish, generateFeatures,
                      export, and createService calls.
        """
        params = {
            "f" : "json"
        }
        if jobType is not None:
            params['jobType'] = jobType
        if jobId is not None:
            params["jobId"] = jobId
        url = f"{self.root}/status"
        return self._get(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def parts(self):
        """if the item is being uploaded by multipart, it will return the name
        of each part for the item."""
        url = f"{self.root}/parts"
        params = {"f" : "json"}
        return self._get(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def commit(self, wait=False, additionalParams={}):
        """
        Commit is called once all parts are uploaded during a multipart Add
        Item or Update Item operation. The parts are combined into a file,
        and the original file is overwritten during an Update Item
        operation. This is an asynchronous call and returns immediately.
        Status can be used to check the status of the operation until it is
        completed.

        Inputs:
           itemId - unique item id
           folderId - folder id value, optional
           wait - stops the thread and waits for the commit to finish or fail.
           additionalParams - optional key/value pair like
                              type : "File Geodatabase". This is mainly used
                              when multipart uploads occur.
        """

        url = f"{self.root}/commit"
        params = {
            "f" : "json",
        }
        for key, value in additionalParams.items():
            params[key] = value
        if wait != True:
            return self._post(url=url,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_port=self._proxy_port,
                                 proxy_url=self._proxy_url)
        res = self._post(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
        res = self.status()
        import time
        while res['status'].lower() in ["partial", "processing"]:
            time.sleep(2)
            res = self.status()
        return res
    #----------------------------------------------------------------------
    def addByPart(self, filePath):
        """
           Allows for large file uploads to be split into 50 MB chunks and
           to be sent to AGOL/Portal.  This resolves an issue in Python,
           where the multi-part POST runs out of memory.
           To use this function, an addItem() must be run first and that
           item id must be passed into this function.

           Once the file is uploaded, a commit() must be performed on the
           data to have all the parts merged together.

           No item properties will be inherited from the initial AddItem()
           call unless it is an sd file.  Therefore you must call
           updateItem() on the recently updated item.

           Example:
              fp = r"c:\temp\big.zip"
              #.... AGOL init stuff
              #....
              usercontent = agol.content.usercontent(username)
              res = usercontent.addItem(itemParameters=None,
                                  filePath=fp,
                                  overwrite=True,
                                  multipart=True)
              res = usercontent.addByPart(filePath=fp)
              res = usercontent.commit(itemId)
              usercontent.updateItem(updateItemParameters=ip)
              # Item added and updated.
           Inputs:
              filePath - location of the file on disk
              itemId - empty item added to AGOL/Portal
              folder - folder id
        """
        def read_in_chunks(file_object, chunk_size=10000000):
            """Generate file chunks of 10MB"""
            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break
                yield data

        params = {
        "f" : "json",
        'itemType' : 'file'
        }
        url = f'{self.root}/addPart'
        messages = []
        files = {}
        with open(filePath, 'rb') as f:
            for part_num, piece in enumerate(read_in_chunks(f), start=1):
                params['partNum'] = part_num
                tempFile = os.path.join(os.environ['TEMP'], f"split.part{part_num}")
                files['file'] =  [tempFile, os.path.basename(filePath)]
                with open(tempFile, 'wb') as writer:
                    writer.write(piece)
                    del writer
                res = self._post(url=url,
                                 param_dict=params,
                                 files=files,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
                if os.path.isfile(tempFile):
                    os.remove(tempFile)
                del files
                del tempFile
                files = {}
                messages.append(res)
        return messages
########################################################################
class User(BaseAGOLClass):
    """represents a single user on a portal or AGOL organization"""
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    _json_dict = None
    _folder = "/"
    _folders = None
    _location = None
    _username = None
    _folders = None
    _currentFolder = None
    _nextStart = None
    _items = None
    _start = None
    _num = None
    _total = None

    #----------------------------------------------------------------------
    def __init__(self, url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initalize=False):
        """Constructor"""
        self._url = url
        self._location = url
        self._folder = "/"
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        if initalize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self, folder='/'):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        if folder is None or folder == "/":
            folder = 'root'
        result_template = {
            "username": "",
            "total": 0,
            "start": 1,
            "num": 0,
            "nextStart": 0,
            "currentFolder": None,
            "items": [],
            "folders": []
        }
        nextStart = 1
        self._json_dict = {}
        self._json = ""
        while nextStart > -1:
            res = self.search(start=nextStart, num=100)
            if self._location.find(res['username'].lower()) > -1:
                self._location = self._location.replace(res['username'].lower(), res['username'])
                self._url = self._url.replace(res['username'].lower(), res['username'])

            nextStart = int(res['nextStart'])
            result_template['username'] = res['username']
            result_template["total"] = res["total"]
            result_template['nextStart'] = res['nextStart']
            result_template['start'] = res['start']
            result_template['num'] = res['num']

            #Added so the root has content to match when in a folder,
            #not sure if this is best practice or not.  Did not add
            #username and created
            #if res['currentFolder'] is None:
                #result_template['currentFolder'] = {
                    #'title': 'root',
                    #'id': None,
                    #'created' : None,
                    #'username' : None
                #}
                #result_template['folders'].insert(0, result_template['currentFolder'])
            #else:
            result_template['currentFolder'] = res['currentFolder']
            for item in res['items']:
                if item not in result_template['items']:
                    result_template['items'].append(item)
            #if 'folders' in res and \
               #folder.lower() == 'root':
                #for folder in res['folders']:
                    #if folder not in result_template['folders']:
                        #result_template['folders'].append(folder)

        self._json_dict = result_template
        self._json = json.dumps(result_template)
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                          not attr.startswith('_')]
        for k in result_template:
            if k in attributes:
                setattr(self, f"_{k}", result_template[k])
            else:
                print( k, " - attribute not implemented in Content.User class.")

        self._loadFolders()


    def _loadFolders(self,
               start=1,
               num=100):
        """
        Returns the items for the current location of the user's content
        Inputs:
           start -  The number of the first entry in the result set
                    response. The index number is 1-based.
                    The default value of start is 1 (that is, the first
                    search result).
                    The start parameter, along with the num parameter, can
                    be used to paginate the search results.
           num - The maximum number of results to be included in the result
                 set response.
                 The default value is 10, and the maximum allowed value is
                 100.
                 The start parameter, along with the num parameter, can be
                 used to paginate the search results.

           Output:
             returns a list of dictionary
        """
        url = self.root

        params = {
            "f" : "json",
            "num" : num,
            "start" : start
        }

        res =  self._get(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)
        self._folders = []
        if 'folders' in res:
            self._folders.extend(iter(res['folders']))
        root = {
                'title': 'root',
                'id': None,
                'created' : None,
                'username' : None
                }
        self._folders.insert(0, root)
        if self._currentFolder is None:
            #self._location = self.root
            self._currentFolder = {
                    'title': 'root',
                    'id': None,
                    'created' : None,
                    'username' : None
                }
    #----------------------------------------------------------------------
    def search(self,
               start=1,
               num=10):
        """
        Returns the items for the current location of the user's content
        Inputs:
           start -  The number of the first entry in the result set
                    response. The index number is 1-based.
                    The default value of start is 1 (that is, the first
                    search result).
                    The start parameter, along with the num parameter, can
                    be used to paginate the search results.
           num - The maximum number of results to be included in the result
                 set response.
                 The default value is 10, and the maximum allowed value is
                 100.
                 The start parameter, along with the num parameter, can be
                 used to paginate the search results.

           Output:
             returns a list of dictionary
        """
        url = self.location

        params = {
            "f" : "json",
            "num" : num,
            "start" : start
        }
        return self._get(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)

    #----------------------------------------------------------------------

    @property
    def username(self):
        '''gets the property value for username'''
        if self._username is None:
            self.__init()
        return self._username
    #----------------------------------------------------------------------
    @property
    def folders(self):
        '''gets the property value for folders'''
        if self._folders is None :
            self.__init()
        if self._folders is not None and isinstance(self._folders, list):
            if len(self._folders) == 0:
                self._loadFolders()
        return self._folders
    #----------------------------------------------------------------------
    @property
    def currentFolder(self):
        '''gets/sets the current folder (folder id)'''
        if self._currentFolder is None:
            self.__init()
        return self._currentFolder
    #----------------------------------------------------------------------
    @currentFolder.setter
    def currentFolder(self, value):
        """gets/sets the current folder (folder id)"""
        if value is not None and value.lower() == self._currentFolder['title']:
            return
        if value is None:
            self._location = self.root
            self._currentFolder = {
                    'title': 'root',
                    'id': None,
                    'created' : None,
                    'username' : None
                }
            self.__init()
        elif value == "/" or value.lower() == 'root':
            self.location = self.root
            self._currentFolder = {
                    'title': 'root',
                    'id': None,
                    'created' : None,
                    'username' : None
                }
            self.__init()
        else:
            for folder in self.folders:
                if 'title' in folder:
                    if folder['title'].lower() == value.lower():
                        self._location = f"{self.root}/{folder['id']}"
                        self._currentFolder = folder
                        self.__init(folder['title'])
                        break
    #----------------------------------------------------------------------
    @property
    def nextStart(self):
        '''gets the property value for nextStart'''
        if self._nextStart is None:
            self.__init()
        return self._nextStart
    #----------------------------------------------------------------------
    @property
    def items(self):
        '''gets the property value for items'''
        self.__init()
        return [
            UserItem(
                url=f"{self.location}/items/{item['id']}",
                securityHandler=self._securityHandler,
                proxy_url=self._proxy_url,
                proxy_port=self._proxy_port,
                initalize=True,
            )
            for item in self._items
        ]
    #----------------------------------------------------------------------
    @property
    def start(self):
        '''gets the property value for start'''
        if self._start is None:
            self.__init()
        return self._start
    #----------------------------------------------------------------------
    @property
    def num(self):
        '''gets the property value for num'''
        if self._num is None:
            self.__init()
        return self._num

    #----------------------------------------------------------------------
    @property
    def total(self):
        '''gets the property value for total'''
        if self._total is None:
            self.__init()
        return self._total
    #----------------------------------------------------------------------
    @property
    def root(self):
        """returns the base url"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def location(self):
        """returns the location url on the system"""
        return self._location
    #----------------------------------------------------------------------
    def __str__(self):
        """returns raw JSON response as string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        """returns properties (key/values) from the JSON response"""
        if self._json_dict is None:
            self.__init()
        for k,v in self._json_dict.items():
            yield [k,v]
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the group's items"""
        self.__init()
        return True
    #----------------------------------------------------------------------
    def addRelationship(self,
                        originItemId,
                        destinationItemId,
                        relationshipType):
        """
        Adds a relationship of a certain type between two items.

        Inputs:
           originItemId - The item ID of the origin item of the
                          relationship
           destinationItemId - The item ID of the destination item of the
                               relationship.
           relationshipType - The type of relationship between the two
                              items. Must be defined in Relationship types.
        """
        url = f"{self.root}/addRelationship"
        params = {
            "originItemId" : originItemId,
            "destinationItemId": destinationItemId,
            "relationshipType" : relationshipType,
            "f" : "json"
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteRelationship(self,
                           originItemId,
                           destinationItemId,
                           relationshipType
                           ):
        """
        Deletes a relationship of a certain type between two items. The
        current user must have created the relationship to delete it. If
        the relationship does not exist, an error is thrown.

        Inputs:
           originItemId - The item ID of the origin item of the
                          relationship.
           destinationItemId -  item ID of the destination item of the
                               relationship.
           relationshipType -  type of relationship between the two items.
        """
        url = f"{self.root}/deleteRelationship"
        params = {
            "f" : "json",
            "originItemId" : originItemId,
            "destinationItemid" : destinationItemId,
            "relationshipType" : relationshipType

        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def publishItem(self,
                    fileType,
                    publishParameters=None,
                    itemId=None,
                    filePath=None,
                    text=None,
                    outputType=None,
                    buildIntialCache=False,
                    wait=False,
                    overwrite=False
                    ):
        """
        Publishes a hosted service based on an existing source item.
        Publishers can create feature services as well as tiled map
        services.
        Feature services can be created using input files of type csv,
        shapefile, serviceDefinition, featureCollection, and
        fileGeodatabase.

        Inputs:
           fileType - Item type.
                      Values: serviceDefinition | shapefile | csv |
                      tilePackage | featureService | featureCollection |
                      fileGeodata | geojson | scenePackage
           publishParameters - object describing the service to be created
                               as part of the publish operation. Only
                               required for CSV, Shapefiles, feature
                               collection, and file geodatabase.
           itemId - The ID of the item to be published.
           text - The text in the file to be published. This ONLY applies
                  to CSV files.
           filePath - The file to be uploaded.
           outputType - Only used when a feature service is published as a
                        tile service.
           buildIntialCache - default false.  Allows the user to prevent
                              the creation of the initial cache for tiled
                              services.
        """
        _allowed_types = ["serviceDefinition", "shapefile", "csv",
                          "tilePackage", "featureService",
                          "featureCollection", "fileGeodatabase",
                          "geojson", "scenePackage"]
        if fileType.lower() not in [t.lower() for t in _allowed_types]:
            raise AttributeError(f"Invalid fileType: {fileType}")

        url = f"{self.location}/publish"
        params = {
            "f" : "json",
            'fileType': fileType
        }

        if isinstance(buildIntialCache, bool):
            params['buildInitialCache'] = buildIntialCache
        if publishParameters is not None and not isinstance(
            publishParameters, PublishCSVParameters
        ):
            params['publishParameters'] = json.dumps(publishParameters.value)
        elif isinstance(publishParameters, PublishCSVParameters):
            params['publishParameters'] = json.dumps(publishParameters.value)

        if itemId is not None:
            params['itemId'] = itemId
        if text is not None and fileType.lower() == 'csv':
            params['text'] = text
        if overwrite != False:
            params['overwrite'] = overwrite
        if filePath is not None:

            files = {'file': filePath}
            res = self._post(url=url,
                             param_dict=params,
                             files=files,
                             securityHandler=self._securityHandler,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
        else:
            res = self._post(url=url,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_port=self._proxy_port,
                                 proxy_url=self._proxy_url)
        if (
            'services' in res
            and len(res['services']) > 0
            and 'error' in res['services'][0]
        ):
            if 'message' in res['services'][0]['error']:
                print(res['services'][0]['error']['message'])
            else:
                print(res['services'][0]['error'])
            raise Exception(f"Could not publish item: {itemId}")
        elif 'services' in res and len(res['services']) > 0:
            itemId = res['services'][0]['serviceItemId']
            ui = UserItem(
                url=f"{self.location}/items/{itemId}",
                securityHandler=self._securityHandler,
                proxy_url=self._proxy_url,
                proxy_port=self._proxy_port,
            )
            if wait == True:
                status = "partial"
                while status != "completed":
                    status = ui.status(jobId=res['services'][0]['jobId'], jobType="publish")

                    if status['status'] == 'failed':
                                #if 'statusMessage' in status:
                                    #print( status['statusMessage'])
                        print(status)
                        raise Exception(f"Could not publish item: {itemId}")

                    elif status['status'].lower() == "completed":
                        break
                    time.sleep(2)
            return ui
        else:
            print (res)
            raise Exception(f"Could not publish item: {itemId}")
        return None

    #----------------------------------------------------------------------
    def exportItem(self,
                   title,
                   itemId,
                   exportFormat,
                   tags="export",
                   snippet=None,
                   exportParameters=None,
                   wait=True):
        """
        Exports a service item (POST only) to the specified output format.
        Available only to users with an organizational subscription.
        Invokable only by the service item owner or an administrator.

        Inputs:
           title - name of export item
           itemId - id of the item to export
           exportFormat - out format. Values: Shapefile, CSV or File
                          Geodatabase, feature collection, GeoJson,
                          or Scene Package
           tags - comma seperated list of quick descriptors, the default is
            export.
           snippet - short explination of the exported item
           exportParameters - A JSON object describing the layers to be
                              exported and the export parameters for each
                              layer.
           wait - optional - default false. Export item is an a synchronus
            operation. If true is specified, the process will wait till the
            operation is completed.
        Output:
           If wait is True:
              UserItem class
           else:
              job id for the export item.
        """
        url = f"{self.location}/export"
        params = {
            "f" : "json",
            "title" : title,
            "tags" : tags,
            "itemId" : itemId,
            "exportFormat" : exportFormat,
        }
        if snippet is not None:
            params['snippet'] = snippet
        if exportParameters is not None:
            params["exportParameters"] = json.dumps(exportParameters)
        res = self._post(url=url,
                            param_dict=params,
                            securityHandler=self._securityHandler,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
        itemURL = f"{self.location}/items/{res['exportItemId']}"
        if self.currentFolder is not None or self.currentFolder['title'] != "root":
            self.moveItems(items=res['exportItemId'], folder=self.currentFolder['id'])
        ui = UserItem(url=itemURL,
                      securityHandler=self._securityHandler,
                      proxy_url=self._proxy_url,
                      proxy_port=self._proxy_port)
        if wait != True:
            return res['jobId'], ui
        status = "partial"
        while status != "completed":
            status = ui.status(jobId=res['jobId'], jobType="export")
            if status['status'] == 'failed':
                raise Exception(f"Could not export item: {itemId}")
            elif status['status'].lower() == "completed":
                break
            time.sleep(2)
        return ui
    #----------------------------------------------------------------------
    def createService(self, createServiceParameter,
                      description=None,
                      tags="Feature Service",
                      snippet=None):
        """
        The Create Service operation allows users to create a hosted
        feature service. You can use the API to create an empty hosted
        feaure service from feature service metadata JSON.

        Inputs:
           createServiceParameter - create service object
        """
        url = f"{self.location}/createService"
        val = createServiceParameter.value
        params = {
            "f" : "json",
            "outputType" : "featureService",
            "createParameters" : json.dumps(val),
            "tags" : tags
        }
        if snippet is not None:
            params['snippet'] = snippet
        if description is not None:
            params['description'] = description
        res =  self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
        if 'id' in res or 'serviceItemId' in res:
            url = (
                f"{self.location}/items/{res['id']}"
                if 'id' in res
                else f"{self.location}/items/{res['serviceItemId']}"
            )
            return UserItem(url=url,
                            securityHandler=self._securityHandler,
                            proxy_url=self._proxy_url,
                            proxy_port=self._proxy_port)
        return res
    #----------------------------------------------------------------------
    def deleteFolder(self):
        """
        The delete user folder operation (POST only) is available only on
        the user's non-root folders. The user's root folder cannot be
        deleted.
        Deleting a folder also deletes all items that it contains (both the
        items and the links are removed).


        """
        if self.currentFolder is None or self.currentFolder['id'] is None:
            return "Cannot delete root folder."
        url = f"{self.location}/delete"
        params = {
            "f" : "json"
        }
        res = self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
        self._folders = None
        self.currentFolder = None
        self.refresh
        return res
    #----------------------------------------------------------------------
    def shareItems(self, items, groups="", everyone=False,
                   org=False):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong. This
        operation also allows a user to share items with everyone, in which
        case the items are publicly accessible, or with everyone in their
        organization.

        Inputs:
           everyone - boolean, makes item public
           org - boolean, shares with all of the organization
           items - comma seperated list of items to share
           groups - comma sperated list of groups to share with
        """
        url = f"{self.root}/shareItems"
        params = {
            "f" : "json",
            "items" : items,
            "everyone" : everyone,
            "org" : org,
            "groups" : groups
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def unshareItems(self, items, groups):
        """
        Unshares a batch of items with the specified list of groups

        Inputs:
           items - comma-seperated list of items to unshare
           groups - comma-seperated list of groups to not share items with
        """
        url = f"{self.root}/unshareItems"
        params = {
            "f" : "json",
            "items" : items,
            "groups" : groups
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def moveItems(self, items, folder="/"):
        """
        Moves a batch of items from their current folder to the specified
        target folder.

        Inputs:
           items - comma-seperated list of items to move
           folder - destination folder id. "/" means root
        """
        url = f"{self.root}/moveItems"
        params = {
            "f" : "json",
            "items" : items,
            "folder" : folder

        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteItems(self, items):
        """
        Deletes a batch of items owned or administered by the calling user.

        Inputs:
           items - A comma separated list of items to be deleted.
        """
        url = f"{self.root}/deleteItems"
        params = {
            "f" : "json",
            "items" : items
        }
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def createFolder(self, name):
        """
        Creates a folder in which items can be placed. Folders are only
        visible to a user and solely used for organizing content within
        that user's content space.
        """
        url = f"{self.root}/createFolder"
        params = {
            "f" : "json",
            "title" : name
        }
        self._folders = None
        return self._post(url=url,
                             param_dict=params,
                             securityHandler=self._securityHandler,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    def _addItemMultiPart(self,
                          itemParameters,
                          filePath):
        """
        The secret sauce behind the addByPart workflow
        Inputs:
           itemParatmers - ItemParamter class
           filePath - full disk path location.
        Output:
           UserItem class
        """
        url = f"{self._location}/addItem"
        params = {
            "f": "json",
            'multipart' : 'true',
            "filename"	: os.path.basename(filePath)
        }
        res = self._post(url=url,
                         param_dict=params,
                         securityHandler=self._securityHandler)
        if 'id' in res:
            itemID = res['id']
            iUrl = f"{self.location}/items/{itemID}"
            ui = UserItem(url=iUrl,
                          securityHandler=self._securityHandler,
                          proxy_url=self._proxy_url,
                          proxy_port=self._proxy_port)
            res = ui.addByPart(filePath=filePath)
            res = ui.commit(wait=True)
            up = ItemParameter()
            up.title = itemParameters.title
            up.tags = itemParameters.tags
            up.filename = os.path.basename(filePath)
            up.type = itemParameters.type
            ui.updateItem(itemParameters=up)

            update_url = ui.root.replace('/rest/', '/') + "/update"

            data = {'title': itemParameters.title,
                   'tags': itemParameters.tags,
                   'filename': os.path.basename(filePath),
                   'type': itemParameters.type,
                   'f': 'json'}
            for k,v in itemParameters.value.items():
                if k not in data.keys():
                    data[k] = json.dumps(v) if isinstance(v, bool) else v
            res = self._post(url=update_url,
                             param_dict=data,
                            securityHandler=self._securityHandler)
            ui.refresh()
            return ui
        return None
    #----------------------------------------------------------------------
    def addItem(self,
                itemParameters,
                filePath=None,
                overwrite=False,
                folder=None,
                dataURL=None,
                url=None,
                text=None,
                relationshipType=None,
                originItemId=None,
                destinationItemId=None,
                serviceProxyParams=None,
                metadata=None,
                multipart=False):
        """
        Adds an item to ArcGIS Online or Portal.
        Te Add Item operation (POST only) is used to upload an item file,
        submit text content, or submit the item URL to the specified user
        folder depending on documented items and item types. This operation
        is available only to the specified user.

        Inputs:
           itemParameters - required except for when multipart = True or SD
                            file. This contains all the information
                            regarding type, tags, etc...
           filePath - if updating the item's content
           overwrite - if the item exists, it overwrites it
           folder - id of the folder to place the item
           dataURL - The URL where the item can be downloaded. The resource
                     will be downloaded and stored as a file type. Similar
                     to uploading a file to be added, but instead of
                     transferring the contents of the file, the URL of the
                     data file is referenced and creates a file item.
           url - The URL of the item to be submitted. The URL can be a URL
                 to a service, a web mapping application, or any other
                 content available at that URL.
           text - The text content for the item to be submitted.
           relationshipType - The type of relationship between the two
                              items. See Relationship types for a complete
                              listing of types.
           originItemId - The item ID of the origin item of the
                          relationship
           destinationItemId - item ID of the destination item of the
                               relationship.
           serviceProxyParams -  JSON object that provides rate limiting
                                 and referrer checks when accessing secured
                                 services.
           metadata - XML meta data file.
           multipart - If true, the file is uploaded in multiple parts. Used
                       for files over 100 MBs in size.
        """
        params = {
            "f" : "json"
        }
        res = ""
        if itemParameters is not None:
            for k,v in itemParameters.value.items():
                params[k] = json.dumps(v) if isinstance(v, bool) else v
        if itemParameters.overwrite is not None:
            params['overwrite'] = json.dumps(overwrite)
        if itemParameters.overwrite != overwrite:
            params['overwrite'] = json.dumps(overwrite)
        if dataURL is not None:
            params['dataURL'] = dataURL
        if url is not None:
            params['url'] = url
        if text is not None:
            params['text'] = text
        if relationshipType is not None:
            params['relationshipType'] = relationshipType
        if originItemId is not None:
            params['originItemId'] = originItemId
        if destinationItemId is not None:
            params['destinationItemId'] = destinationItemId
        if serviceProxyParams is not None:
            params['serviceProxyParams'] = serviceProxyParams
        url = f"{self.location}/addItem"
        files = {}
        if multipart:
            res = self._addItemMultiPart(
                itemParameters=itemParameters,
                filePath=filePath)
        else:
            if filePath is not None:
                if os.path.isfile(filePath):
                    files['file'] = filePath
                    params["filename"] = os.path.basename(filePath)
                elif multipart:
                    params["filename"] = os.path.basename(filePath)
                elif not os.path.isfile(filePath):
                    print ("{0} not found".format(filePath))
            if 'thumbnail' in params:
                v = params['thumbnail']
                del params['thumbnail']
                files['thumbnail'] = v
            if metadata is not None and os.path.isfile(metadata):
                files['metadata'] = metadata
            if not files:
                res = self._post(url,
                                 param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
            else:
                params['itemType'] = 'file'
                params['async'] = False
                res = self._post(url=url,
                                 param_dict=params,
                                 files=files,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        if (isinstance(res, dict) and \
               "id" not in res):
            raise Exception(f"Cannot add the item: {res}")
        elif (isinstance(res, (UserItem, Item)) and \
                  res.id is None):
            raise Exception(f"Cannot add the item: {str(res)}")
        elif isinstance(res, (UserItem, Item)):
            return res
        else:
            itemId = res['id']
            return UserItem(
                url=f"{self.location}/items/{itemId}",
                securityHandler=self._securityHandler,
                proxy_url=self._proxy_url,
                proxy_port=self._proxy_port,
            )
########################################################################
class FeatureContent(BaseAGOLClass):
    """
    Feature Content Root is the parent resource for feature operations such
    as Analyze and Generate.
    """
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    #----------------------------------------------------------------------
    def __init__(self, url, securityHandler,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        self._url = f"{url}/features" if url.lower().find("/features") < 0 else url
        self._securityHandler = securityHandler
        if securityHandler is not None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    @property
    def root(self):
        """ returns the feature content root url """
        return self._url
    #----------------------------------------------------------------------
    def analyze(self,
                itemId=None,
                filePath=None,
                text=None,
                fileType="csv",
                analyzeParameters=None):
        """
        The Analyze call helps a client analyze a CSV file prior to
        publishing or generating features using the Publish or Generate
        operation, respectively.
        Analyze returns information about the file including the fields
        present as well as sample records. Analyze attempts to detect the
        presence of location fields that may be present as either X,Y
        fields or address fields.
        Analyze packages its result so that publishParameters within the
        JSON response contains information that can be passed back to the
        server in a subsequent call to Publish or Generate. The
        publishParameters subobject contains properties that describe the
        resulting layer after publishing, including its fields, the desired
        renderer, and so on. Analyze will suggest defaults for the renderer.
        In a typical workflow, the client will present portions of the
        Analyze results to the user for editing before making the call to
        Publish or Generate.
        If the file to be analyzed currently exists in the portal as an
        item, callers can pass in its itemId. Callers can also directly
        post the file. In this case, the request must be a multipart post
        request pursuant to IETF RFC1867. The third option for text files
        is to pass the text in as the value of the text parameter.

        Inputs:
           itemid - The ID of the item to be analyzed.
           file - The file to be analyzed.
           text - The text in the file to be analyzed.
           filetype - The type of input file.
           analyzeParameters - A AnalyzeParameters object that provides
                               geocoding information
        """
        files = []
        url = f"{self._url}/analyze"
        fileType = "csv"
        params = {"f": "json", "fileType": fileType}
        if analyzeParameters is not None and\
               isinstance(analyzeParameters, AnalyzeParameters):
            params['analyzeParameters'] = analyzeParameters.value

        if filePath is not None and os.path.isfile(filePath):
            params['text'] = open(filePath, 'rb').read()
            return self._post(url=url, param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        elif itemId is not None:
            params["fileType"] = fileType
            params['itemId'] = itemId
            return self._post(url=url, param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        else:
            raise AttributeError("either an Item ID or a file path must be given.")
    #----------------------------------------------------------------------
    def generate(self,
                 publishParameters,
                 itemId=None,
                 filePath=None,
                 fileType=None,
                 option='on'
                 ):
        """
        The Generate call helps a client generate features from a CSV file
        or a shapefile.
        CSV files that contain location fields (either address fields or X,
        Y fields) are spatially enabled by the Generate operation.
        The result of Generate is a JSON feature collection.
        If the file to be analyzed already exists in the portal as an item,
        callers can pass in its itemId. Callers can also directly post the
        file. In this case, the request must be a multipart post request
        pursuant to IETF RFC1867. The third option for text files is to
        pass the text in as the value of the text parameter.
        Generate requires that the caller pass in publish parameters that
        describe the layers in the feature collection to be generated.

        Inputs:
           publishParameters - A JSON object describing the layer and
                               service to be created as part of the Publish
                               operation. The appropriate value for publish
                               parameters depends on the file type being
                               published. (Python Dictionary)
           itemId - unique id of item to generate
           filePath - path to zipped shapefile or csv
           fileType - either shapefile or csv
        """
        allowedFileTypes = ['shapefile', 'csv']
        files = {}
        url = self._url + "/generate"
        params = {
            "f" : "json"
        }
        params['publishParameters'] = publishParameters
        params['option'] = option


        if fileType.lower() not in allowedFileTypes and \
           filePath is not None:
            raise AttributeError("fileType must be either shapefile or csv when specifying a file")
        if filePath is not None:
            params['filetype'] = fileType
            #Changed from type to filetype to generate a FC from zip
            if fileType.lower() == "csv":
                params['text'] = open(filePath,'rb').read()
                return self._post(url=url, param_dict=params,
                                     securityHandler=self._securityHandler,
                                     proxy_url=self._proxy_url,
                                     proxy_port=self._proxy_port)
            else:
                files['file'] = filePath
                res = self._post(url=url,
                                 param_dict=params,
                                 files=files,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
                return res
        elif itemId is not None:
            params["fileType"] = fileType
            params['itemId'] = itemId
            return self._post(url=url, param_dict=params,
                                 securityHandler=self._securityHandler,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
########################################################################
class Group(BaseAGOLClass):
    """
    The group's content provides access to the items that are shared with
    the group. Group items are stored by reference and are not physically
    stored in a group. Rather, they are stored as links to the original
    item (/content/items/<itemId>).Available only to the users of the group
    """
    _contentURL = None
    _groupId = None
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    _json_dict = None
    _items = None
    _communityUrl = None
    #----------------------------------------------------------------------
    def __init__(self,
                 groupId,
                 contentURL,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initalize=False):
        """Constructor"""
        if contentURL.find(groupId) < 0:
            self._url = "%s/%s" % (contentURL, groupId)
        else:
            self._url = contentURL
        self._groupId = groupId
        self._contentURL = contentURL
        self._securityHandler = securityHandler
        if not securityHandler is None:
            self._referer_url = securityHandler.referer_url
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        if initalize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        json_dict = self._get(url=self._url,
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
            if k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                setattr(self, k, v)
    #----------------------------------------------------------------------
    @property
    def root(self):
        """returns the base url"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def id(self):
        """gets the group id"""
        return self._groupId
    #----------------------------------------------------------------------
    def __str__(self):
        """returns raw JSON response as string"""
        if self._json is None:
            self.__init()
        return self._json
    #----------------------------------------------------------------------
    def __iter__(self):
        """returns properties (key/values) from the JSON response"""
        if self._json_dict is None:
            self.__init()
        for k,v in self._json_dict.items():
            yield [k,v]
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the group's items"""
        self.__init()
        return True
    #----------------------------------------------------------------------
    @property
    def items(self):
        """returns the registered items for a given group"""
        if self._items is None:
            self.__init()
        return self._items
    #----------------------------------------------------------------------
    def __assembleURL(self, url, groupId):
        """private function that assembles the URL for the community.Group
        class"""
        from ..packages.six.moves.urllib_parse import urlparse
        parsed = urlparse(url)
        communityURL = "%s://%s%s/sharing/rest/community/groups/%s" % (parsed.scheme, parsed.netloc,
                                                                        parsed.path.lower().split('/sharing/rest/')[0],
                                                                        groupId)
        return communityURL

    #----------------------------------------------------------------------
    @property
    def group(self):
        """returns the community.Group class for the current group"""
        split_count = self._url.lower().find("/content/")
        len_count = len('/content/')
        gURL = self._url[:self._url.lower().find("/content/")] + \
            "/community/" + self._url[split_count+ len_count:]#self.__assembleURL(self._contentURL, self._groupId)

        return CommunityGroup(url=gURL,
                              securityHandler=self._securityHandler,
                              proxy_url=self._proxy_url,
                              proxy_port=self._proxy_port)






