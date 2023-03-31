# ------------------------------------
# interface to the Samba File Server
# ------------------------------------
# author:   Baumann Danièl
# created:  2023-02-14
# version:  1.0
# ------------------------------------
from smb.SMBConnection import SMBConnection

from mongodb import get_samba_credentials

# set username, password and the server_ip from the cretendials
credentials = get_samba_credentials()
username = credentials["username"]
password = credentials["password"]
server_ip = credentials["server_ip"]

# get_sharedfiles()
#
# returns: all shared files from the samba file server
def get_sharedfiles():

    # open connection to samba server
    conn = SMBConnection(username, password, "", "", "",
                         use_ntlm_v2=True, is_direct_tcp=True)
    conn.connect(server_ip, 445)
    shares = conn.listShares()

    # array of all shared files
    sharedfiles = []

    # get through all shared directories and save all files from the "reports" directory
    for share in shares:
        if (share.name in ['reports']):
            sharedfiles = conn.listPath(share.name, '/')

    conn.close()

    # array of found files on the server
    files = []

    for file in sharedfiles:
        if (file.filename not in ['.', '..']):
            # insert found file into array
            files.append(file.filename)

    # sort files reverse, that the latest created file is the first one
    files.sort(reverse=True)

    return files

# download(filename)
#
# parameter:
#   filename = filename from report to download
#
# downloads the file from the samba fileserver and stores it in the "download" directory
#
# returns: the path to the downloaded file
def download(filename):

    # open connection to samba fileserver
    conn = SMBConnection(username, password, "", "", "",
                         use_ntlm_v2=True, is_direct_tcp=True)
    conn.connect(server_ip, 445)

    # if connection is established
    # try to open a new temporary file and store the conntent 
    # given from the samvba fileserver in the temporary file
    if conn:
        with open("./download/"+filename, 'wb') as tmp_file:
            conn.retrieveFile('reports', '/'+filename, tmp_file)
            conn.close()

    return "download/"+filename

# upload(filename)
#
# parameter:
#   filename = filename from report to upload
#
# uploads the given file to the samba fileserver
def upload(filename):

    # open connection to samba fileserver
    conn = SMBConnection(username, password, "", "", "",
                         use_ntlm_v2=True, is_direct_tcp=True)
    conn.connect(server_ip, 445)

    # if connection is established
    # try to upload the given report file to the server
    if conn:
        with open("reports/"+filename, 'rb') as file_obj:
            conn.storeFile('reports', '/'+filename, file_obj)
            conn.close()
