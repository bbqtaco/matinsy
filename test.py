import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd

dbfile = 'db/cheminventory.db'

conn = sqlite3.connect(dbfile)
c = conn.cursor()
rooms = []
catid = []
c.execute('select catid,room from Bot')
tmp1 = c.fetchall()
for i in range(len(tmp1)):
    catid.append(tmp1[i][0])
    rooms.append(tmp1[i][1])
    conn.commit()
c.close()

df= pd.Series(rooms,index=catid)

