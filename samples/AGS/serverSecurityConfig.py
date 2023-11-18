from arcrest.security.security import AGSTokenSecurityHandler
from arcrest.manageags import AGSAdministration

if __name__ == "__main__":
    username = ""
    password = ""
    url = ""

    sh = AGSTokenSecurityHandler(
        username=username,
        password=password,
        token_url=f'{url}/tokens/',
        proxy_url=None,
        proxy_port=None,
    )

    ags = AGSAdministration(url=url,
                            securityHandler=sh,
                            proxy_url=None,
                            proxy_port=None)

    security_cfg = ags.security.securityConfig
    print(security_cfg)

    if 'sslEnabled' in security_cfg:
        security_cfg['sslEnabled'] = False

    if 'httpEnabled' in security_cfg:
        security_cfg['httpEnabled'] = True

    res = ags.security.updateSecurityConfig(security_cfg)
    print(res)
