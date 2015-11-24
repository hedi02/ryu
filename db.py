import sqlite3

foobar_uri = 'file:foobar_database?mode=memory&cache=shared'
# conn = sqlite3.connect('file::memory:?cache=shared', uri=True)
conn = sqlite3.connect(':memory:')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE flowdb
             (fid int, dp int, byte int, pkt int, time DATETIME)''')

c.execute('''CREATE TABLE flowdblong
             (fid int, dp int, byte int, pkt int, time DATETIME)''')


def insertdb(fid, dp, byte, pkt):
    # Insert a row of data
    c.execute("INSERT INTO flowdb VALUES (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))", (fid, dp, byte, pkt))
    printdb()

def updatedb(fid, dp, byte, pkt):
    c.execute("UPDATE flowdb set byte=?,pkt=?, time=strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE fid=? and dp=?", (byte,pkt,fid,dp))
    conn.commit()
    # printdb()

def fidcheck(fid, dp):
    c.execute("SELECT count(*) from flowdb WHERE fid=? and dp=?", (fid,dp))
    data=c.fetchone()[0]
    conn.commit()
    return data

def bytecheck():
    c.execute("SELECT byte from flowdb WHERE byte>700")
    rows = c.fetchall()
    for row in rows:
        print row

def printdb():
   c.execute("SELECT * FROM flowdb ORDER BY ROWID")
   rows = c.fetchall()
   for row in rows:
       print row


# insertdb(1,2,3,4)
#
# if fidcheck(1, 2):
#     print "aaa"
# else:
#     print "bbb"

# conn.close()