from __future__ import absolute_import
import zipfile
import datetime
import calendar
import glob
import mimetypes
import os
from ..packages import six
from ..packages.six.moves import http_client as httplib
from ..web._base import BaseWebOperations

###########################################################################
class BaseCMP(BaseWebOperations):
    """ base community mapping program class"""
    pass
class BaseOpenData(BaseWebOperations):
    """ base opendata site"""
    pass
########################################################################
class BaseGeoEnrichment(BaseWebOperations):
    """ base geoenrichment class """
    pass
########################################################################
class BaseBookmark(object):
    """ base Bookmark class """
    pass
########################################################################
class BaseBaseMap(object):
    """base BaseMap object class"""
    pass
########################################################################
class BaseWebMap(object):
    """base webmap object class"""
    pass
########################################################################
class BaseOperationalLayerObject(object):
    """ base operational layer object class """
    pass
########################################################################
class BaseGPObject(object):
    """ base geoprocessing object """
    _value = None
    _paramName = None
    _dataType = None
    # ----------------------------------------------------------------------
    @property
    def dataType(self):
        """returns the data type"""
        return self._dataType
    # ----------------------------------------------------------------------
    @property
    def paramName(self):
        """gets/set the parameter name"""
        return self._paramName
    # ----------------------------------------------------------------------
    @paramName.setter
    def paramName(self, value):
        """gets/set the parameter name"""
        if isinstance(value, basestring):
            self._paramName = value
########################################################################
class BaseDomain(object):
    """ all domain values inherit this class """
    pass
########################################################################
class BaseDefinition(object):
    """ class that all definition objects inherit from """
    pass
########################################################################
class BaseSymbol(object):
    """ class that all symbol object inherit from """
    pass
########################################################################
class BaseRenderer(object):
    """ all renderers inherit this class """
    pass
########################################################################
class BaseParameters(object):
    """ All parameter objects used for Portal/AGOL """
    pass
########################################################################
class BaseSecurityHandler(BaseWebOperations):
    """ All Security Objects inherit from this class """
    _token = None
    _valid = True
    _message = ""
    _is_portal = False
    #----------------------------------------------------------------------
    @property
    def message(self):
        """ returns any messages """
        return self._message
    #----------------------------------------------------------------------
    @property
    def valid(self):
        """ returns boolean wether handler is valid """
        return self._valid
########################################################################
class AbstractGeometry(object):
    """ Base Geometry Class """
    pass
########################################################################
class BaseFilter(object):
    """ base filter class """
    pass
########################################################################
class DynamicData(object):
    """base class for data source"""
    pass
########################################################################
class DataSource(object):
    """base class for data source"""
    pass

########################################################################
class BaseAGSServer(BaseWebOperations):
    """ base class from which all service inherit """
    _url = None
    _proxy_url = None
    _proxy_port = None
    #----------------------------------------------------------------------
    @property
    def proxy_port(self):
        """gets the proxy port"""
        return self._proxy_port
    #----------------------------------------------------------------------
    @property
    def proxy_url(self):
        """ gets the proxy URL """
        return self._proxy_url
    #----------------------------------------------------------------------
    @proxy_url.setter
    def proxy_url(self, value):
        """ sets the proxy url """
        self._proxy_url = value
    #----------------------------------------------------------------------
    @proxy_port.setter
    def proxy_port(self, value):
        """ sets the proxy port """
        if isinstance(value, int):
            self._proxy_port = value
    #----------------------------------------------------------------------
    @property
    def url(self):
        return self._url
    #----------------------------------------------------------------------
    @url.setter
    def url(self, value):
        self._url = value
    #----------------------------------------------------------------------
    def _tostr(self,obj):
        """ converts a object to list, if object is a list, it creates a
            comma seperated string.
        """
        if not obj:
            return ''
        return ', '.join(map(self._tostr, obj)) if isinstance(obj, list) else str(obj)
    #----------------------------------------------------------------------
    def _unicode_convert(self, obj):
        """ converts unicode to anscii """
        if isinstance(obj, dict):
            return {self._unicode_convert(key): self._unicode_convert(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._unicode_convert(element) for element in obj]
        elif isinstance(obj, str):
            return obj 
        elif isinstance(obj, six.text_type):
            return obj.encode('utf-8')
        elif isinstance(obj, six.integer_types):
            return obj
        else:
            return obj
# This function is a workaround to deal with what's typically described as a
# problem with the web server closing a connection. This is problem
# experienced with www.arcgis.com (first encountered 12/13/2012). The problem
# and workaround is described here:
# http://bobrochel.blogspot.com/2010/11/bad-servers-chunked-encoding-and.html

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead as e:
            return e

    return inner
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
########################################################################
class BaseAGOLClass(BaseWebOperations):

    _token = None
    _org_url ="http://www.arcgis.com"
    _url = "http://www.arcgis.com/sharing/rest"
    _surl = "https://www.arcgis.com/sharing/rest"
    _referer_url = "http://www.arcgis.com"
    _useragent = "ArcREST"
    _token_url = 'https://www.arcgis.com/sharing/rest/generateToken'
    _proxy_url = None
    _proxy_port = None
    def initURL(self,org_url=None, token_url=None,referer_url=None):

        if org_url is not None and org_url != '':
            if not org_url.startswith('http://') and not org_url.startswith('https://'):
                org_url = f'http://{org_url}'
            self._org_url = org_url

        if self._org_url.lower().find('/sharing/rest') > -1:
            self._url = self._org_url
        else:
            self._url = f"{self._org_url}/sharing/rest"

        if self._url.startswith('http://'):
            self._surl = self._url.replace('http://', 'https://')
        else:
            self._surl  =  self._url

        if token_url is None:
            self._token_url = f'{self._surl}/generateToken'
        else:
            self._token_url = token_url

        if referer_url is None:
            if not self._org_url.startswith('http://'):
                self._referer_url = self._org_url.replace('http://', 'https://')
            else:
                self._referer_url = self._org_url
        else:
            self._referer_url = referer_url



    #----------------------------------------------------------------------
    def _unzip_file(self, zip_file, out_folder):
        """ unzips a file to a given folder """
        try:
            zf = zipfile.ZipFile(zip_file, 'r')
            zf.extractall(path=out_folder)
            zf.close()
            del zf
            return True
        except:
            return False
    #----------------------------------------------------------------------
    def _date_handler(self, obj):
        if isinstance(obj, datetime.datetime):
            return calendar.timegm(obj.utctimetuple()) * 1000
        else:
            return obj
    #----------------------------------------------------------------------
    def _list_files(self, path):
        """lists files in a given directory"""
        return sorted(glob.glob(pathname=path))
    #----------------------------------------------------------------------
    def _get_content_type(self, filename):
        """ gets the content type of a file """
        mntype = mimetypes.guess_type(filename)[0]
        filename, fileExtension = os.path.splitext(filename)
        if mntype is None:
            if fileExtension.lower() == ".csv":
                mntype = "text/csv"
            elif fileExtension.lower() == ".sd":
                mntype = "File/sd"
            else:
                        #mntype = 'application/octet-stream'
                mntype = f"File/{fileExtension.replace('.', '')}"
        return mntype
    #----------------------------------------------------------------------
    def _tostr(self,obj):
        """ converts a object to list, if object is a list, it creates a
            comma seperated string.
        """
        if not obj:
            return ''
        return ', '.join(map(self._tostr, obj)) if isinstance(obj, list) else str(obj)
    #----------------------------------------------------------------------
    def _unicode_convert(self, obj):
        """ converts unicode to anscii """
        if isinstance(obj, dict):
            return {self._unicode_convert(key): self._unicode_convert(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._unicode_convert(element) for element in obj]
        elif isinstance(obj, str):
            return obj 
        elif isinstance(obj, six.text_type):
            return obj.encode('utf-8')
        elif isinstance(obj, six.integer_types):
            return obj
        else:
            return obj
