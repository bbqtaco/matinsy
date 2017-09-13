
# coding: utf-8

# In[106]:

import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd
import os as os
from os import system, path, remove
import glob
import time
import shutil

import platform
host = platform.node()

#file modes for chmod commands
mod = 0o755

btime = time.strftime("%Y-%m-%d %H:%M")
#print(btime)


#hostflag = 0
if host == 'boron':
    home = '/home/huffman/work/matinsy/'
    dbfile = home+'db/cheminventory.db'
    webhtmldir = './'
    webmsdsdir = webhtmldir+'msds/'
    websafetyplansdir = webhtmldir+'Lab_Specific_Hygiene_Plans/'
    htmldir = '/home/huffman/public_html/sdsweb/'
    safetyplansdir = htmldir+'Lab_Specific_Hygiene_Plans/'
    safetyplansnoplan = './noplans.html'
    msdsdir = htmldir+'msds/'
    roomfile = home+'etc/allrooms.dat'
    
elif host == 'msds.wcu.edu':
    home = '/wwbintz/'
    dbfile = home+'/matinsy/db/cheminventory.db'
    htmldir = home+'public_html/'
    webhtmldir = './'
    safetyplansdir = htmldir+'Lab_Specific_Hygiene_Plans/'
    safetyplansnoplan = './noplans.html'
    msdsdir = htmldir+'msds/'
    webmsdsdir = webhtmldir+'msds/'
    websafetyplansdir = webhtmldir+'Lab_Specific_Hygiene_Plans/'
    roomfile = home+'matinsy/etc/allrooms.dat'
else:
    pass



tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory DB Problems </TITLE></HEAD>\n<BODY>\n'
hd = '<H1>'  
he = '</H1>\n'
lt = '<UL>'
le = '</UL>'
li = '<LI>'
dn = '</BODY>\n </HTML>\n'

print('********************************************')

bmsg = ' db integrety checking beginning '
print(host,bmsg,btime)


# In[11]:

def highlight_vals(val):
    if val != 'none':
        return 'color: red' 
    else:
        return ''


# ## CAS problems
# 

# In[2]:

def getallbots(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    rooms = []
    catid = []
    CAS = []
    d = {}
    c.execute('select catid,room,CAS,reorder,name from Bot')
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
    return d


# In[63]:

d = getallbots(dbfile)
df = pd.DataFrame.from_dict(d, orient='index')
df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
df.head()
df_noCAS = df[df['CAS'].isnull()]
df_noROOM = df[df['room'].isnull()]
df_noNAME = df[df['name'].isnull()]
df_noREORDER = df[df['reorder'].isnull()]
#TODO: add these to dictionary for output
outdict = {'noCAS':df_noCAS,'noROOM':df_noROOM,'noREORDER':df_noREORDER,'noName':df_noNAME}


# ## Rooms that aren't correct

# In[114]:

##this realrooms should be readable from a config file
realrooms = 'NS102 NS102A NS103 NS105 NS106  NS108 NS110 NS114 NS118 NS119A NS119B NS119C NS122 NS127 NS129 NS202 NS204 NS205 NS207 NS208 NS209 NS214 NS216 NS216A NS217 NS218 NS220 NS221 NS226 NS227 NS302 NS304 NS307 NS308A NS309 NS311 NS312 NS314 NS315 NS317 NS322 NS323 NS324 NSG NSG02 NSG03 NSG04 NSG05 NSG10 NSG14 NSG17 ST114 ST115 ST116 ST118 ST119 ST120 ST121 ST122 ST124 ST125 ST126 ST127 ST130 ST131 ST132 ST134 ST136 ST153 ST155 ST157 ST157A ST157B ST159 ST201 ST209 ST210 ST212 ST214 ST215 ST218 ST219 ST220 ST220A ST220B ST303 ST304 ST305 ST306 ST309 ST312 ST314 ST315 ST323 ST355 ST401 ST403 ST404 ST405 ST409 ST412 ST413 ST415 ST419 ST420'
realrooms.split(' ')

###read room file
def readdbparms(file):
    parm = []
    f = open(file,'r')
    tmp = f.readlines()
    f.close()
    for line in tmp:
        parm.append( line.rstrip('\n\r\t'))

    #parm = filter(None, parm) # drop empty elements in a list
    parm = [x for x in parm if x != '']
    return parm

realrooms = readdbparms(roomfile)

badroomcatid = []
roomslist =  list(df['room'].unique())
tmp = [ x for x in roomslist if 'retire' not in x ]
tmp = [ x for x in tmp if 'combine' not in x ]
tmp = [ x for x in tmp if 'neu' not in x ]
roomlist = tmp
for room in  roomlist:
    if room not in realrooms:
        for catid in df['room'][df['room'] == room].index:
            badroomcatid.append(catid)
        
outdict['bad rooms'] = df.ix[badroomcatid]


# In[ ]:




# ## output html report file

# In[ ]:




# In[116]:

#dfout.replace(np.nan,' ',inplace=True)
hd = '<H1 style=color:red>\n'  
he = '</H1>\n'
ofile = htmldir+'ZZZ_problems.html'
#remove(ofile)
with open(ofile, 'w') as f:
    f.write( tp)
    for key,dfout in outdict.items():
        print(key)
        f.write(hd)
        f.write(key)
        f.write(he)
        f.write(dfout.to_html())
        
    f.write(dn)

os.chmod(ofile, mod)


# In[117]:

etime = time.strftime("%Y-%m-%d %H:%M")
emsg = ' db integrety checking ending '
print(host,emsg,etime)


# In[ ]:



