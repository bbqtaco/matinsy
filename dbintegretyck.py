
# coding: utf-8

# In[1]:

#import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd

#import pubchempy as pcp
#import json
#from urllib.request import urlopen
#from rdkit import Chem
#from rdkit.Chem.Draw import IPythonConsole
#from rdkit.Chem import Draw
#from rdkit.Chem import PandasTools

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
if host == ('boron' or 'sausage'):
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
    cheminfodata = home+'cheminfodata/'
    
elif host == 'msds.wcu.edu':
    print(host)
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
    cheminfodata = home+'matinsy/cheminfodata/'
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


# In[2]:

def highlight_vals(val):
    if val != 'none':
        return 'color: red' 
    else:
        return ''


# ## definitions
# 

# In[3]:

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

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False

    return True

def ckcasvalidity(cas):
    #print('CAS',cas)
    exceptions = (';afjadjfakjf;ad','addad22222',None,'na','fake','?','?8-83-4')#('114460-21-8', '1319-46-6',  '9003-70-7', '10486-00-7','9047-08-9','14024-63-6','28053-08-9','58-86-6','8005-03-6','9001-41-6','13520-83-7','13520-83-7','1250-23-4','9000-01-5','12030-88-5','67-09-5')
    if cas in exceptions:
        casflag = 2
        #print('CAS exception')
    elif is_number(cas[0]) == False:
        print(cas)
        casflag = 2
    elif '1-0-' in cas:
        casflag = 3
    else:
        #print(cas)
        cs = cas.split('-')
        #print('cs',cs)
        Nstr = ''.join(cs[:2])
        #print('Nstr',Nstr)
        Q = float(cs[-1])
        #print('Q',Q)
        LN = len(Nstr)
        Nlist = []
        for i,N in enumerate(Nstr):
            Nlist.append(float(N)*(LN-i))
        Nprod = np.mod(np.sum(Nlist),10)
        if Nprod == Q:
            casflag = 1
            #print('Valid CAS')
        else:
            casflag = 0
            #print('Bad CAS',cas,Nprod,Q)
    return casflag
#print(Q,Nprod,Nlist)
def casvalidlist(caslist):
    #TODO:  add wes cas filter
    validlist = []
    invalidlist = []
    exceptlist = []
    wescas = []
    for cas in caslist:
        flag = ckcasvalidity(cas)
        if flag == 1:
            validlist.append(cas)
        elif flag == 0:
            invalidlist.append(cas)
        elif flag == 2:
            exceptlist.append(cas)
        elif flag == 3:
            wescas.append(cas)
        else:
            pass
    return validlist,invalidlist,exceptlist,wescas


# In[4]:

#dd = getallbots(dbfile)
#ddf = pd.DataFrame.from_dict(dd, orient='index')
#ddf.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
#caslist = list(filter(None,set(ddf['CAS'].tolist())))
#valid,invalid,exclist,wescas = casvalidlist(caslist)

#dfvalid = ddf[ddf.CAS.isin(valid)]
#dfinvalid = ddf[ddf.CAS.isin(invalid)]
#dfexclist = ddf[ddf.CAS.isin(exclist)]
#dfwescas  = ddf[ddf.CAS.isin(wescas)]
#outdict['dfvalid'] = dfvalid
#outdict['invalid cas'] = dfinvalid
#outdict['completely wrong'] = dfexclist
#outdict['wes cas'] = dfwescas
#ddf[ddf.CAS.isin(invalid)]


# ## Missing INFO

# In[5]:

d = getallbots(dbfile)
df = pd.DataFrame.from_dict(d, orient='index')
df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
df.head()
df_noCAS = df[df['CAS'].isnull()].sort_values('name')
df_noROOM = df[df['room'].isnull()].sort_values('CAS')
df_noNAME = df[df['name'].isnull()].sort_values('CAS')
df_noREORDER = df[df['reorder'].isnull()]
df_noREORDER = df_noREORDER[~df_noREORDER.room.str.contains('retired')]
df_noREORDER = df_noREORDER[~df_noREORDER.room.str.contains('combin')]
df_noREORDER = df_noREORDER[~df_noREORDER.room.str.contains('neut')].sort_values('name')
#df_noREORDER = df_noREORDER[~df_noREORDER.room.str.contains('UNK')]
#TODO: add these to dictionary for output
outdict = {'noCAS':df_noCAS,'noROOM':df_noROOM,'noREORDER':df_noREORDER,'noName':df_noNAME}


# In[6]:

#df_noREORDER[~df_noREORDER.room.str.contains('combin')]


# ## CAS problems

# In[7]:

caslist = list(filter(None,set(df['CAS'].tolist())))
valid,invalid,exclist,wescas = casvalidlist(caslist)

#dfvalid = ddf[ddf.CAS.isin(valid)]
dfinvalid = df[df.CAS.isin(invalid)].sort_values('name')
dfexclist = df[df.CAS.isin(exclist)].sort_values('name')
dfwescas  = df[df.CAS.isin(wescas)].sort_values('CAS')
#outdict['dfvalid'] = dfvalid
outdict['invalid CAS'] = dfinvalid
outdict['completely wrong CAS'] = dfexclist
outdict['Wes CAS'] = dfwescas


# ## Rooms that aren't correct

# In[8]:

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
        
outdict['bad rooms'] = df.loc[badroomcatid].sort_values('room')


# In[ ]:




# ## output html report file

# In[ ]:




# In[9]:

#dfout.replace(np.nan,' ',inplace=True)
hd = '<H1 style=color:red>\n'  
he = '</H1>\n'
ofile = htmldir+'ZZZ_problems.html'
if os.path.isfile(ofile)  == True:
    remove(ofile)
else:
    pass
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


# In[10]:

etime = time.strftime("%Y-%m-%d %H:%M")
emsg = ' db integrety checking ending '
print(host,emsg,etime)


# In[ ]:



