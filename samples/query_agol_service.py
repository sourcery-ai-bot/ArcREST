"""
   Query agol service
   Python 2.x
   ArcREST 3.0.1
"""


from __future__ import print_function
from arcresthelper import securityhandlerhelper
from arcrest.agol import FeatureService
from arcrest.common.filters import LayerDefinitionFilter

if __name__ == "__main__":
    url = ''
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
    shh = securityhandlerhelper.securityhandlerhelper(securityinfo=securityinfo)
    if shh.valid == False:
        print (shh.message)
    else:
        fs = FeatureService(
            url=url,
            securityHandler=shh.securityhandler,
            proxy_port=proxy_port,
            proxy_url=proxy_url,
            initialize=True)
        ldf = LayerDefinitionFilter()
        ldf.addFilter(0, where="1=1")
        print (fs.query(layerDefsFilter=ldf,
                       returnCountOnly=True))
        # should see something like : {'layers': [{'count': 4, 'id': 0}]}