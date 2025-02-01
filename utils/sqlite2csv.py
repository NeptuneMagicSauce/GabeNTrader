#!/usr/bin/env python3

from common import *

Common.init()

from utils import *

if len(sys.argv) != 2:
    print('Usage:', sys.argv[0], '<path-to-sqlite-db>')
    exit(1)

db = sqlite_copy_db(sys.argv[1])

cursor = db.con.execute('select * from moz_cookies')

header = list(map(lambda x: x[0], cursor.description))
print(','.join(header))

while row := cursor.fetchone():
    for item in row:
        if isinstance(item, str):
            print("'", item, "'", sep='', end=',')
        else:
            print(item, sep='', end=',')
    print('')
