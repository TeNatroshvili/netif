from smb.SMBConnection import SMBConnection

userID = 'sambauser'
password = 'Syp2022'
server_ip = '10.128.10.7'

def get_sharedfiles():
    conn = SMBConnection(userID, password, "", "", "", use_ntlm_v2=True,is_direct_tcp=True)
    conn.connect(server_ip, 445)
    shares = conn.listShares()
    sharedfiles = []

    for share in shares:
        if(share.name in ['reports']):
            sharedfiles = conn.listPath(share.name, '/')

    conn.close()

    files = []

    for file in sharedfiles:
        if(file.filename not in ['.','..']):
            files.append(file.filename)
    files.sort(reverse=True)
    return files

def download(filename):
    conn = SMBConnection(userID, password, "", "", "", use_ntlm_v2=True,is_direct_tcp=True)
    conn.connect(server_ip, 445)
    if conn:
        with open("./download/"+filename, 'wb') as tmp_file:
            conn.retrieveFile('reports', '/'+filename, tmp_file)
            conn.close()
    return "download/"+filename

def upload(filename):
    conn = SMBConnection(userID, password, "", "", "", use_ntlm_v2=True,is_direct_tcp=True)
    conn.connect(server_ip, 445)
    if conn:
        with open("reports/"+filename, 'rb') as file_obj:
            conn.storeFile('reports', '/'+filename, file_obj)
        conn.close()