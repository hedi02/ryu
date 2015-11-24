import sqlite3
#   import db

foobar_uri = 'file:foobar_database?mode=memory&cache=shared'
conn2 = sqlite3.connect(foobar_uri)

c = conn2.cursor()

# c.execute("SELECT * FROM flowdb ORDER BY ROWID")
# # rows = c.fetchall()
# # print "aaa"
# # for row in rows:
# #    print row
#
# conn2.commit()
conn2.close()
