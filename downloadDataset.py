from pyega import *
import sys
from multiprocessing import Pool, cpu_count

exons = 'EGAD00001001913'

# Load up session
(username, password, key) = load_credentials()
session = api_login(username, password)
if not session:
    sys.exit(1)

# List all file names
reply = api_list_files_in_dataset(session, exons)
#pretty_print_files_in_dataset(reply, exons)
print 'Downloading exon files:', len(reply['response']['result'])

# For every file
tmp = [[session, exonFile['fileID']] for exonFile in reply['response']['result']]

def getFile(args):
    session = args[0]
    exonFile = args[1]
    req_label = str( uuid.uuid4() )
    req_reply = api_make_request(session, 'files', exonFile, req_label, key)

    list_reply = api_list_requests(session, req_label)

    # Save a copy of the request ticket
    with open(req_label + ".json", "w+") as fo:
        print("Writing copy of request ticket to {}".format(req_label + ".json"))
        fo.write( json.dumps(list_reply) )
    download_request(list_reply)

print 'There are %d CPUs available.' % cpu_count()
#pool = Pool(processes=cpu_count())
pool = Pool(processes=8)
pool.map(getFile, tmp)
pool.close()
pool.join()

api_logout(session)

