import sqlite3
import random


#foobar_uri = 'file:foobar_database?mode=memory&cache=shared'
# conn = sqlite3.connect('file::memory:?cache=shared', uri=True)
#conn = sqlite3.connect(':memory:')

randomnumber = random.random()
conn = sqlite3.connect('db/'+str(randomnumber)+'.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE FlowStatsDb
             (fid int, dp int, byte int, pkt int, time DATETIME)''')

c.execute('''CREATE TABLE FlowThroughputDb
             (fid int, dp int, th int, time DATETIME)''')

c.execute('''CREATE TABLE flowdblong
             (fid int, dp int, byte int, pkt int, time DATETIME)''')


def insert_stat(fid, dp, byte, pkt):
    # Insert a row of data
    c.execute("INSERT INTO FlowStatsDb VALUES (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))", (fid, dp, byte, pkt))
    print_stat()

def insert_throughput(fid, dp, th):
    # Insert a row of data
    c.execute("INSERT INTO FlowThroughputDb VALUES (?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))", (fid, dp, th))
    #print_stat()

def update_stat(fid, dp, byte, pkt):
    c.execute("UPDATE FlowStatsDb set byte=?,pkt=?, time=strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE fid=? and dp=?", (byte,pkt,fid,dp))
    conn.commit()
    # print_stat()

def read_stat(fid, dp):
    c.execute("SELECT byte from FlowStatsDb WHERE fid=? and dp=?", (fid,dp))
    data=c.fetchone()[0]
    conn.commit()
    return data

def fidcheck(fid, dp):
    c.execute("SELECT count(*) from FlowStatsDb WHERE fid=? and dp=?", (fid,dp))
    data=c.fetchone()[0]
    conn.commit()
    return data

def bytecheck():
    c.execute("SELECT byte from FlowStatsDb WHERE byte>700")
    rows = c.fetchall()
    for row in rows:
        print row

def print_stat():
   c.execute("SELECT * FROM FlowStatsDb ORDER BY ROWID")
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