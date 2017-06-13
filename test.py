import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd

dbfile = 'db/cheminventory.db'

conn = sqlite3.connect(dbfile)
c = conn.cursor()
rooms = []
catid = []
CAS = []
d = {}
c.execute('select catid,room,CAS from Bot')
tmp1 = c.fetchall()
for i in range(len(tmp1)):
    catid.append(tmp1[i][0])
    rooms.append(tmp1[i][1])
    CAS.append(tmp1[i][2])
    tmp2 = []
    for j in range(1,len(tmp1[i])):
        tmp2.append(tmp1[i][j])
    d[tmp1[i][0]] = tmp2
    conn.commit()
c.close()



df= pd.DataFrame.from_dict(d,orient='index')
df.rename(columns={0:'room',1:'CAS'},inplace=True)
df.index.name = 'CATID'


roomsdf = df.room.unique()
roomslist = roomsdf.tolist()
#filter rooms that should not be rooms
tmp = [ x for x in roomslist if 'retire' not in x ]
tmp = [ x for x in tmp if 'combine' not in x ]
tmp = [ x for x in tmp if 'neu' not in x ]
rooms = tmp

