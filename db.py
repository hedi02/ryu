import csv
import sqlite3

conn = sqlite3.connect(':memory:')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE flowdb
             (fid int, dp int, byte int, pkt int)''')

def insertdb(fid, dp, byte, pkt):
    # Insert a row of data
    c.execute("INSERT INTO flowdb VALUES (?, ?, ?, ?)", (fid, dp, byte, pkt))

    # Save (commit) the changes
    conn.commit()

    c.execute("SELECT * FROM flowdb")

    rows = c.fetchall()

    for row in rows:
        print row

def updatedb(fid, dp, byte, pkt):
    c.execute("UPDATE flowdb set byte=? WHERE fid=? and dp=?", (byte,fid,dp))

    conn.commit()
    c.execute("SELECT * FROM flowdb")
    rows = c.fetchall()
    for row in rows:
        print row
        print "****"

def fidcheck(fid, dp):
    c.execute("SELECT count(*) from flowdb WHERE fid=? and dp=?", (fid,dp))
    data=c.fetchone()[0]
    conn.commit()
    return data

# insertdb(1,2,3,4)
#
# if fidcheck(1, 2):
#     print "aaa"
# else:
#     print "bbb"



# conn.close()