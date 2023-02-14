from smb.SMBConnection import SMBConnection

def get_sharedfiles():
    userID = 'sambauser'
    password = 'Syp2022'
    server_ip = '10.128.10.7'

    conn = SMBConnection(userID, password, "", "", "", use_ntlm_v2=True,is_direct_tcp=True)

    conn.connect(server_ip, 445)

    shares = conn.listShares()
    sharedfiles = []

    for share in shares:
        if(share.name in ['reports']):
            sharedfiles = conn.listPath(share.name, '/')

    conn.close()
    return sharedfiles
