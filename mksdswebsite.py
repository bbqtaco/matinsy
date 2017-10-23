
# coding: utf-8

# In[1]:

import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd
from pandas import HDFStore

#import pubchempy as pcp
#import json

#from urllib.request import urlopen
#import urllib
#from urllib.request import urlopen
#from bs4 import BeautifulSoup


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
    cheminfodir = htmldir+'cheminfo/'
    cheminfodata = home+'cheminfodata/'
    evacplandir = home+'evac_plans/'
    webevacplandir = webhtmldir+'evac_plans/'
    
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
    cheminfodir = htmldir+'cheminfo/'
    cheminfodata = home+'matinsy/cheminfodata/'
    webevacplandir = webhtmldir+'evac_plans/'
else:
    pass


print('********************************************')

bmsg = ' websync beginning '
print(host,bmsg,btime)


# In[2]:

storagedict = {'g':"General",'w':"Corrosive",'r':'Flammable','y':'Oxidizer','b':'Toxic','none':'none or null: checkme','blank':'blank:checkme','hw':'hw:fixme','2':'2:fixme','1':'1:fixme','3':'3:fixme','4':'4:fixme','unk':'unk:fixme','na':'na:fixme','[CH2CH(CH2NH2•HCl)]n':'[CH2CH(CH2NH2•HCl)]n:fixme'}


# In[3]:

###delete old html files
#TODO: make into function
#files = glob.glob(htmldir+'sds_*.html')
#print(files)
#for file in files:
    #print(file)
#    try:
#        remove(file)
#    except (OSError,e):  ## if failed, report it back to the user ##
#        print("Error: {0} {1} - %s.".format(e.filename,e.strerror) )
        
def deloldhtmlfiles():
    '''this function has a problem.  It deletes the entire site, so there is a dead time when the data may not be available.
    Better would be to delete one file at a time, but this idea would lead to html files remaining after they have been deleted 
    from the db.
    '''
    ###delete old html files
    #TODO: make into function
    files = glob.glob(htmldir+'sds_*.html')
    #print(files)
    for file in files:
        #print(file)
        try:
            remove(file)
        except (OSError,e):  ## if failed, report it back to the user ##
            print("Error: {0} {1} - %s.".format(e.filename,e.strerror) )


# In[26]:

def getevaclinkNSB(room):
    NL = ['109','110','111','112','113','114','115','116','119A','119B','119C','123','125']
    SL = ['106','103','M101','132A','132','130','128','126']
    
    plandict = {'NS100N':'NSB_Evac_Complete.pdf#page=2'}
    plandict['NS100S'] = 'NSB_Evac_Complete.pdf#page=1'
    plandict['NS200N'] = 'NSB_Evac_Complete.pdf#page=4'
    plandict['NS200S'] = 'NSB_Evac_Complete.pdf#page=3'
    plandict['NS300N'] = 'NSB_Evac_Complete.pdf#page=6'
    plandict['NS300S'] = 'NSB_Evac_Complete.pdf#page=5'
    plandict['NSGN'] = 'NSB_Evac_Complete.pdf#page=7'
    plandict['NSGS'] = 'NSB_Evac_Complete.pdf#page=8'
    plandict['NSGM'] = 'NSB_Evac_Complete.pdf#page=9'
    
    blkey = room[:2]
    flkey = room[2]
    roomnum = room[2:]
    #print(blkey,flkey,roomnum)
    if flkey == 'G':
        blflkey = blkey+flkey+'N'
        Nfile = webevacplandir+plandict[blflkey]
        blflkey = blkey+flkey+'S'
        Sfile = webevacplandir+plandict[blflkey]
        blflkey = blkey+flkey+'M'
        Mfile = webevacplandir+plandict[blflkey]
        evaclink = '<ul> <li><a href='+Nfile+'> Northside Evacuation Plan </a><li><a href='+Mfile+'> Middle of the floor Evacuation Plan </a><li> <a href='+Sfile+'> Southside Evacuation Plan </a></ul>'
        
        pass
    else:
        blflkey = blkey+flkey+'00'+'N'
        Nfile = webevacplandir+plandict[blflkey]
        blflkey = blkey+flkey+'00'+'S'
        Sfile = webevacplandir+plandict[blflkey]
        evaclink = '<ul> <li><a href='+Nfile+'> Northside Evacuation Plan </a><li> <a href='+Sfile+'> Southside Evacuation Plan </a></ul>'
    
    return evaclink
#getevaclinkNSB('NS400N')


# In[24]:




###get room non inventory links
room = 'NS322'
#print(rooms)
def getdirfromroom(room):
    
    #files = glob.glob(safetyplansdir+room+'*/*')
    files = glob.glob(safetyplansdir+room+'*/*.pdf')# only pdf files
    #print(files)
    if not files:
        files = [safetyplansnoplan]
    #print(files)
    return files

def mkfiles4web(files):
    #files =  getdirfromroom(room)
    webfiles = []
    #print(files)
    for file in files:
        #webfiles.append(file.split('/')[-1])
        webfiles.append('/'.join(file.split('/')[-2:]))
    return webfiles




def getevaclinkbkup(room):
    ###find evac plan
    rmdict = {'not':'noplans.html',  'NS':'NSB_Evac_Complete.pdf','ST':'Stillwell_Evac_Complete.pdf','MK':'McKee_Evac_Complete.pdf'}
    rmkey = room[:2]
    flkey = room[2]
    #print(flkey)
    if rmkey not in ['BA','HB','HH','MR','de']:
        
        file = webevacplandir+rmdict[rmkey]
        evaclink = '<a href='+file+'> Evacuation Plan </a>'
    else:
        file = webevacplandir+rmdict['not']
        evaclink = '<a href='+file+'> Evacuation Plan </a>'
    return evaclink

#getevaclinkbkup('NS322')

def getevaclink(room):
    rmkey = room[:2]
    ###find evac plan
    files =  getdirfromroom(room)
    files = mkfiles4web(files)
    ind = [i for i, s in enumerate(files) if 'evac_plan' in s]
    #print(ind)
    if not ind:
        ind = [0]
        evaclink = getevaclinkbkup(room)
        if rmkey == 'NS':
            evaclink = getevaclinkNSB(room)
    else:
        evaclink = '<a href='+websafetyplansdir+files[ind[0]]+'> Evacuation Plan </a>'
    return evaclink

def getchplink(room):
    ###find CHP
    files =  getdirfromroom(room)
    files = mkfiles4web(files)
    ind = [i for i, s in enumerate(files) if 'CHP' in s]
    if not ind:
        ind = [0]
    chplink = '<a href='+websafetyplansdir+files[ind[0]]+'> Chemical Hygene Plan </a>'
    return chplink

def getsoplinks_org(room):
    ###findSOPs
    files =  getdirfromroom(room)
    #files = mkfiles4web(files)
    #ind = [i for i, s in enumerate(files) if 'SOP' in s]
    #soplinks = []
    #for i in range(len(ind)):
    #    soplinks.append(files[ind[i]])

    #### parse out type of sop
    soplinklabels = []
    for link in soplinks:
        soplinklabels.append('SOP for ' +link.split('/')[-1].split('_')[0][15:])
    soplink = []
    for i in range(len(soplinks)):
        soplink.append('<li> <a href='+websafetyplansdir+soplinks[i]+'>'+soplinklabels[i]+'</a> \n')
    sopb = '<ul>'
    sope = '</ul>'
    return sopb+' '.join(soplink)+sope

def getsoplinks(room):
    ###findSOPs
    #files =  getdirfromroom(room)
    files = glob.glob(safetyplansdir+room+'*/*SOP*.pdf')# only pdf files
    files = mkfiles4web(files)
    #print(room,files)
    #ind = [i for i, s in enumerate(files) if 'SOP' in s]
    
    soplinks = []
    for i,file in enumerate(files):
        #print(i,file)
        soplinks.append(file)

    #### parse out type of sop
    soplinklabels = []
    for link in soplinks:
        bindex = link.index('SOP')+3
        eindex = link.find('_',bindex)
        #efindex = link.rfind('.pdf')
        #eindex = np.min([e_index,efindex])
        soplinklabels.append('SOP for ' +link[bindex:eindex])
    soplink = []
    for i in range(len(soplinks)):
        soplink.append('<li> <a href='+websafetyplansdir+soplinks[i]+'>'+soplinklabels[i]+'</a> \n')
    sopb = '<ul>'
    sope = '</ul>'
    return sopb+' '.join(soplink)+sope

#print(getsoplinks('NS323'))

def getcheminfolink(room):
    file = cheminfodir+room+'.html'
    file = cheminfodir+'test.html'
    cheminfolink = evaclink = '<a href='+file+'> Extra Chemical Information </a>'
    return cheminfolink
#files = getdirfromroom(room)
#print(getevaclink(room))
#print(getchplink(room))
#print(getsoplinks(room))
#files = mkfiles4web(files)
#files[0].split('/')
#file = files[0]
#'/'.join(file.split('/')[-2:])
#file


# In[6]:

def mkweblink(webaddress,text):
    link = '<A HREF='+ webaddress +'>'+text+'</A>'
    return link
def getsdsfilename(CAS,reorder):
    flag = ''#g2g'   #good to go
    msdsbase = msdsdir
    if CAS ==None:
        CAS = 'none' #generic
        flag = 'dbnoCAS'
        #CAS = ''
    
    if reorder==None:
        #reorder='none' #generic
        reorder = 'none'
        #altfname =  CAS +'.pdf'
        flag = 'dbnoreorder'    ### db contains no reorder number old style sds file is the 
        
    altfname =  CAS +'.pdf'
    fname = CAS+'_'+reorder +'.pdf'
    #else:
        #fname = CAS+'_'+reorder +'.pdf'
    #if tmp[-4:] == None:
    #    fname = tmp[:-5]
    #else:
    #    fname = tmp

    #fname += '.pdf'
    sdsfilename = msdsbase + fname
    webfname = webmsdsdir+fname.split('/')[-1] ##check what this does
    sdsaltfilename = msdsbase + altfname
    webaltfname = webmsdsdir+altfname.split('/')[-1] ##check what this does
    #print(webfname)
    
    #if flag == 'g2g':
    if path.isfile(sdsfilename) == True:
        link = mkweblink(webfname,fname)
            #link = '<A HREF='+ webfname +'>'+fname+'</A>'
        message = flag + ''
            
    elif path.isfile(sdsaltfilename) == True:
        link = mkweblink(webaltfname,altfname)
        message = flag+'  No product specific SDS' 
    else:
        link = ''#mkweblink(webfname,fname)
        message = flag+ ' missing sds file =>'+fname
    #link = '<A HREF='+ webfname +'>'+fname+'</A>'
    #if path.isfile(sdsfilename) == True:
    #    missing = ''
    #    flag = 0
    #    pass
    #else:
    #    missing = fname
    #print(CAS,reorder)
    return link,message

CAS = '10025-77-1__'
reorder = 's25317a'
reorder = None
CAS = '91-17-8'
CAS = None
reorder = '36117'
link,missing = getsdsfilename(CAS,reorder)
#print(link,missing)


# In[7]:

def getstorage(CAS,dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
       
    #regtype = []
    c.execute('select HazardClass from Chem where CAS=?',[CAS])
    #c.execute('SELECT  catid, regtype,bot.name, bot.cas FROM bot, coi WHERE bot.cas =coi.cas AND bot.cas != \'\' AND bot.room != \'retired\' AND bot.room != \'UNK\' ORDER BY room AND bot.room =?',[room])
    #c.execute('select RegType from Coi where CAS =?',[CAS])
    
    tmp = c.fetchall()
    #print(tmp)
    #for i in range(len(tmp1)):
    #room.append(tmp1[i][0])
    #CATID.append(tmp1[i][0])
    if tmp:
        HC = tmp[0][0]
    else:
        HC = 'none'
    if HC ==None:
        HC = 'none'
    conn.commit()
    c.close()
    return storagedict[HC ]


def gethazard(CAS,dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
       
    #regtype = []
    c.execute('select Health,Flammability,Reactivity,Special from Chem where CAS=?',[CAS])
    #c.execute('SELECT  catid, regtype,bot.name, bot.cas FROM bot, coi WHERE bot.cas =coi.cas AND bot.cas != \'\' AND bot.room != \'retired\' AND bot.room != \'UNK\' ORDER BY room AND bot.room =?',[room])
    #c.execute('select RegType from Coi where CAS =?',[CAS])
    
    tmp = c.fetchall()
    #print(tmp)
    #for i in range(len(tmp1)):
    #room.append(tmp1[i][0])
    #CATID.append(tmp1[i][0])
    if tmp:
        H = tmp[0][0]
        F = tmp[0][1]
        R = tmp[0][2]
        S = tmp[0][3]
    else:
        H = None
        F = None
        R = None
        S = None
    conn.commit()
    c.close()
    return H,F,R,S

def getregtype(CAS,dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
       
    #regtype = []
    c.execute('select Regtype from Coi where CAS=?',[CAS])
    #c.execute('SELECT  catid, regtype,bot.name, bot.cas FROM bot, coi WHERE bot.cas =coi.cas AND bot.cas != \'\' AND bot.room != \'retired\' AND bot.room != \'UNK\' ORDER BY room AND bot.room =?',[room])
    #c.execute('select RegType from Coi where CAS =?',[CAS])
    
    tmp = c.fetchall()
    #print(tmp)
    #for i in range(len(tmp1)):
    #room.append(tmp1[i][0])
    #CATID.append(tmp1[i][0])
    if tmp:
        regtype = tmp[0][0]
    else:
        regtype = None
    if regtype == 'None':
        regtype == None
    conn.commit()
    c.close()
    return regtype  #chemname,CAS,reorder,CATID



def writehtml(ofile,df,roomdf):
    room = df.room.unique()
    room = room.tolist()[0]
    #print(getevaclink(room))
    #print(getchplink(room))
    #print(getsoplinks(room))
    cheminfolink = getcheminfolink(room)
    evaclink = getevaclink(room)
    chplink = getchplink(room)
    soplink = getsoplinks(room)
    table = df.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render()
    nfpatable = roomdf.to_html(na_rep='0', col_space=12)##ask wes about this
    out = ' '.join(('<HTML>\n <HEAD><TITLE>SDS chemical inventory  </TITLE>         </HEAD>\n<BODY>\n <H1> ',room,
        '</H1><H2>Evacuation plans </H2>',evaclink,                    \
        '<H2> Copies of hygiene plans and Standard Operating Procedures </H2>',chplink, soplink,                     \
        '<H2> NFPA max scores </H2>',nfpatable,  \
       # '<H2> Extra Chemical information </H2>',cheminfolink,            \
        "<H2> Chemical Inventory </H2>\n    \
        \n<H4 style=\"color:red\" > RED Column (regtype) indicates Potentially Hazardous Substance warnings</H4>\n    \
        \n",table,'</BODY>\n </HTML>\n'))
    #tp = "<HTML>\n <HEAD><TITLE>SDS chemical inventory  </TITLE> \
    #    </HEAD>\n<BODY>\n                                           \
    #    <H1>Evaculation plans for this room </H1>                    \
    #    <H1> Hygene plans for this room </H1>                      \
    #    <H1> NFPA max scores for this room </H1>                    \
    #    
    #    <H1 style=\"color:red\" > Chemical Inventory  RED are Potentially Hazardous Substances</H1>\n    \
    #    \n"
    
    #dn = '</BODY>\n </HTML>\n'
    with open(ofile, 'w') as f:
        f.write(out)
        #f.write( tp)
        #f.write(df.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render())
        #f.write(dn)
    os.chmod(ofile, mod)
    return


def highlight_vals(val):
    if val != 'none':
        return 'color: red' 
    else:
        return ''
def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val != 'none' else 'black'
    return 'color: %s'.format(color)

#def 

def getallbots(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    rooms = []
    catid = []
    CAS = []
    d = {}
    #c.execute('select catid,room,CAS,reorder,name from Bot')
    c.execute('select catid,room,CAS,reorder,name,Manufacturer from Bot')
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


# In[8]:


d = getallbots(dbfile)

df= pd.DataFrame.from_dict(d,orient='index')
#df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name',4:'Manufacturer'},inplace=True)
df.index.name = 'CATID'
df['regtype'] = None
df['msds_file'] = None
df['messages'] = None
df['storage'] = None
#df['chemclass'] = None   #cameo
#print(df['CAS'][df.index == 110586])

roomsdf = df.room.unique()
roomslist = roomsdf.tolist()
#filter rooms that should not be rooms
tmp = [ x for x in roomslist if 'retire' not in x ]
tmp = [ x for x in tmp if 'combine' not in x ]
tmp = [ x for x in tmp if 'neu' not in x ]

rooms = tmp

#CAS = '7440-38-2'
#CAS = '993-43-1'
#CAS = 'na4'
#CAS = '1-0-0001'

#regtype = getregtype(CAS,dbfile)
#HC = getstorage(CAS,dbfile)
#H,F,R,S = gethazard(CAS,dbfile)
#print(HC)
missinglist = []
for CATID in df.index:
    #print('CATID',CATID)
    CAS = df.loc[CATID].CAS
    reorder = df.loc[CATID].reorder
    regtype = getregtype(CAS,dbfile)
    HC = getstorage(CAS,dbfile)
    link,message = getsdsfilename(CAS,reorder)
    missinglist.append(missing)
    df.set_value(CATID,'storage',HC)
    df.set_value(CATID,'regtype',regtype)
    df.set_value(CATID,'msds_file',link)
    df.set_value(CATID,'messages',message)
   



#######other links put this accessable via cheminfo webpage
#df['chemclass'] = None   #cameo
#store = HDFStore(cheminfodata+'store.h5')
#dfs = store['dfstruct']  # load it
#dfs = dfs[['name','cid','smiles']]
#PandasTools.AddMoleculeColumnToFrame(dfs,'smiles','Molecule',includeFingerprints=True)

#rgn = 31
#paturl = '<a href=https://cameochemicals.noaa.gov/react/'+'{0}'.format(rgn)+ '> CAMEO </a>'
#smilepat = 'C1=CC=C(C=C1)O'  #phenol
#pat = Chem.MolFromSmiles(smilepat)
#founddf = dfs[dfs['Molecule'] >=pat]
#caswithpat = founddf.index.tolist()
#df['chemclass'][df['CAS'].isin(caswithpat)] = paturl



# concat reorder and manufacuture
#df['manreorder'] = df.reorder.astype(str).str.cat(df.Manufacturer.astype(str), sep=', ')


#TODO:  Make a dictionary to convert HC to storeage info

dumplist = ['retire*','UNK','combine','neut','Unk']
mask = df.room.notnull()
for item in dumplist:
    mask = mask & ~df.room.str.contains(item)
    
#mask = df.room.isin( dumplist)
dfout = df[mask].sort_values('room')


#filter out hazardous waste bottles from inventory
#mask = ~df.CAS.str.contains('0-0-0000')
#dfout = dfout[mask]

#dfrooms = {}# put here room specific hygene plan, evac plans, nfps

#print(dfout['room'])
#print(mask)

#
#if path.isfile(fname) == True:
#    pass
#else:
#    missing = fname


# In[9]:

#df[df['reorder'] == 'None']
#df.head()
#dfout[['CAS','reorder']]
#dfout[dfout['CAS'] == '77-09-8']
#dfout
#CAS = '110-82-7'
#room = 'NS205'#
#H,F,R,S = gethazard(CAS,dbfile)
#print(H,F,R,S)
#for room in rooms:
#    tmp = dfout[dfout['room'] == room]['CAS']
#    hazdict = {}
#    for CAS in tmp.unique():
#        H,F,R,S = gethazard(CAS,dbfile)
#        #TODO: convert all non-numbers to 0
#        hazdict[CAS] = [H,F,R,S]


# In[10]:

tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory searchable </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > College of Arts and Sciences Chemical Inventory</H1>\n<H2>Survey for Acknowlegment link of Safety Training</H2> <a href="https://wcu.az1.qualtrics.com/jfe/form/SV_9AIPM7mTueMaA8B">Survey Link</a>\n'
hd = '<H1>'  
he = '</H1>\n'
lt = '<UL>'
le = '</UL>'
li = '<LI>'
dn = '</BODY>\n </HTML>\n'


# In[11]:

def findmaxhaz(L):
    newL = []
    for code in set(L):
        #print(code)
        try:
            val = int(code)
        except ValueError:
            pass
        else:
            newL.append(val)
    maxhaz = np.max(newL)
    return maxhaz

def findShazmat(L):
    if 'w' in L:
        Shazmat = 'Water Reactive'
    else:
        Shazmat = ''
    return Shazmat

def mkhazardtable2(room,df):
    tmpcas = set(df[df['room'] == room]['CAS'])
    #print(tmpcas)
    hazdict = {}
    for i,CAS in enumerate(tmpcas):
        #print(CAS)
        H,F,R,S = gethazard(CAS,dbfile)
        #print(i,H,F,R,S)
        hazdict[CAS] = [H,F,R,S]
        #print(hazdict[CAS])
    #hdf = pd.DataFrame(hazdict,dtype=[int,int,int,str]).T
    hdf = pd.DataFrame(hazdict,index=['H','F','R','S']).T#,
    hdf.replace(np.nan,0,inplace=True)
    hdf.replace('na',0,inplace=True)
    roomd = {}
    for hc in ['H','F','R']:
        L = hdf[hc].tolist()
        maxhaz = findmaxhaz(L)
        roomd[hc] = maxhaz
    
    LS = list(set(hdf['S']))
    Shazmat = findShazmat(LS)
    roomd['S'] = Shazmat
    roomdf = pd.DataFrame(pd.Series(roomd))
    roomdf.rename(columns={0:'max score'},inplace=True)
    #dtypes={'H':'int','F':'int','R':'int','S':'str'}
    #hdf['S'] = hdf['S'].apply(lambda x: str(x))
    #hdf.rename(columns={0:'H',1:'F',2:'R',3:'S'},inplace=True)
    #for c in hdf.columns:
        #print(hdf[c].astype(dtypes[c]),c,dtypes[c])
        #hdf[c] = hdf[c].astype(dtypes[c])
    return roomdf,hdf
        


# In[12]:

##output room files

roomsarray = dfout.room.unique()
rooms = roomsarray.tolist()
rooms.remove('')
#rooms = ['NS202']
#rooms = ['NS323']

deloldhtmlfiles()  ###delete old room files
for room in rooms:
    dfroomout = dfout[dfout.room == room].replace(np.nan,' ')
    mask = ~dfroomout.CAS.str.contains('0-0-0000')#filter out waste
    dfroomout = dfroomout[mask]
    mask = ~dfroomout.CAS.str.contains('1-0-0001')#filter out blank
    dfroomout = dfroomout[mask]
    if dfroomout.empty:
        pass
    else:
        #print('room',room)
        roomdf,hdf = mkhazardtable2(room,dfroomout)
        ofile = htmldir+'sds_'+room +'.html'
        #writehtml(ofile,dfroomout.sort_values('name'),roomdf)
        writehtml(ofile,dfroomout.sort_values(['storage','name']),roomdf)
        

        


# In[13]:

#df[df.index == 110586]


# In[14]:

##output flat
dfout.replace(np.nan,' ',inplace=True)
ofile = htmldir+'flat.html'
if os.path.isfile(ofile)  == True:
    remove(ofile)
else:
    pass
with open(ofile, 'w') as f:
    f.write( tp)
    f.write(dfout.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render())
    f.write(dn)

os.chmod(ofile, mod)


# In[15]:

datestamp ='Website last updated:  '+ time.strftime("%Y-%m-%d %H:%M")
#write master sds file index file
tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory  </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > Links in RED are Potentially Hazardous Substances</H1>\n<H2>See the last words in each red link for additional info</H2>\n'
tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory searchable </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > College of Arts and Sciences Chemical Inventory</H1>\n<H2>Survey for Acknowlegment link of Safety Training</H2> <a href="https://wcu.az1.qualtrics.com/jfe/form/SV_9AIPM7mTueMaA8B">Survey Link</a>\n'
dn = '</BODY>\n </HTML>\n'
lt = '<UL>'
le = '</UL>'
li = '<LI>'
ofile = htmldir+'index.html'
htmlbase=htmldir
files =  glob.glob(htmldir+"sds_*.html")
f = open(ofile, 'w')
f.write( tp)
f.write(lt)
flatlink = '<H2><A HREF=flat.html>The Whole Enchilada</A></H2>\n'
f.write(flatlink)
for file in np.sort(files):
    #print(file)
    #room = file.split('_')[1].split('.')[0] ###old
    room = file.split('/')[-1].split('_')[-1].split('.')[0]
    pathfile = webhtmldir+file.split('/')[-1]
    link = li+'<A HREF='+pathfile+'>'+room+'</A>\n'
    #print(room)
    f.write(link)
f.write(le)
#f.write('<H3> <a href="cheminfodata/test.html">Extra Chemical Information</a></H3>')
f.write('<H3> <a href="ZZZ_problems.html">DB Integrety Checks</a></H3>')
f.write(datestamp)
f.write(dn)
f.close()

#copy index.html to sds.html
sdsfile = htmldir+'sds.html'
remove(sdsfile)
shutil.copy2(ofile,sdsfile)
os.chmod(sdsfile,mod)
#os.chmod(ofile, mod)# i don't have ownership to this file


# In[16]:

msg = 'website complete at '
etime = time.strftime("%Y-%m-%d %H:%M")
print(msg,etime)


# In[17]:

#rooms = roomsarray.tolist()
#print(rooms)


# In[18]:

#fname = '/wwbintz/public_html/msds/7664-93-9_290000acs.pdf'
#webmsdsdir+fname.split('/')[-1]


# In[19]:

#roomdf.head()
#roomdf.to_html(col_space=12)


# In[20]:

##chmod for msds and Lab_specific blah
#files = glob.glob(msdsdir+'*')
#for file in files:
#    os.chmod(file, mod)
#    
#dirs = glob.glob(safetyplansdir+'*')
#for d in dirs:
#    os.chmod(d, mod)
#    path = d+'/'
#    #print(path)
#    files = glob.glob(path+'*')
#    #print(files)
#    for file in files:
#        #print(file)
#        os.chmod(file, mod)


# In[21]:

#print(room,file,link)
#file.split('/')[-1].split('_')[-1].split('.')[0]
#room='NS202'
#dfroomout = dfout[dfout.room == room]
#room = dfroomout.room.unique()
#room = room.tolist()[0]
#room


# In[22]:

#Hdf = pd.DataFrame(hazdict).T
#Hdf.rename(columns={0:'H',1:'F',2:'R',3:'S'},inplace=True)

#Hdf['H'].isnull()
#Hdf['H'].max()
#Hcol = Hdf['H'].as_matrix()
#L = 'H'
#roomdf = Hdf[Hdf[L] == Hdf[L].isnull()].max()
#print(Hdf['S'][Hdf['S'] == 'w'])
#print(Hdf['S'])
#TODO:  list all S in room( W = Water reactive)
#print(Hdf.max(axis=0,skipna=True))
#print(Hdf.head())
#nfpasdict = {'w':"Water Reactive",'NaN':' '}
#roomdf['S'] = nfpasdict['w']
#roomdf = pd.DataFrame(roomdf)
#roomdf.rename(columns={0:'table'})

#rooms
#def mkhazardtable(room,dfout):
#    nfpasdict = {'w':"Water Reactive",'ox':' ','na':' '}
#    tmp = dfout[dfout['room'] == room]['CAS']
#    hazdict = {}
#    for CAS in tmp.unique():
#        H,F,R,S = gethazard(CAS,dbfile)
#        print(H,F,R,S)
#        #if S == 'ox':
#            #S = none
#        if S == None:
#            S = 'na'
#        if S == '':
#            S = 'na'
#        #TODO: convert all non-numbers to 0
#        hazdict[CAS] = [H,F,R,S]
#        print(hazdict[CAS])
#    Hdf = pd.DataFrame(hazdict).T
#    Hdf.rename(columns={0:'H',1:'F',2:'R',3:'S'},inplace=True)
#    #print(Hdf)
#    roomd = {}
#    for L in ['H','F','R']:   ######loop through each safety and generate series
#        tmp = Hdf[L][Hdf[L].notnull()].as_matrix()
        #print('room',room,'tmp',tmp)
        ##check if tmp is empty
        
#        if not tmp[tmp != 'na'].all():
#            roomd[L] = 0
#        elif not np.unique(tmp).any():
#            roomd[L] = 0
#        else:
            #print(pd.Series(tmp[np.core.defchararray.isnumeric(tmp)]).max())
#            print('room',room,'tmp',np.unique(tmp))
#           roomd[L] = tmp[tmp != 'na'].max()
        #roomd[L] = Hdf[L][Hdf[L] == Hdf[L].isnull()].max()
#    tmp = Hdf['S'][Hdf['S'].notnull()]
    #print('S',np.unique(tmp))
#    if 'w' in np.unique(tmp):
        #print('here')
#        roomd['S'] = nfpasdict['w']
#    if tmp.empty:
#        roomd['S'] = nfpasdict['na']
    #print(room,roomd)
#    roomdf = pd.DataFrame(pd.Series(roomd))
    #print('roomdf',roomdf)
#    roomdf.rename(columns={0:'max score'},inplace=True)
#    return roomdf
#room = 'NS205'
#L = 'S'
#tmp  = pd.Series({'F': 0, 'H': 0, 'R': 0})
#print(tmp)
#roomdf,Hdf = mkhazardtable(room,dfout)
#print(roomdf)
#tmp = Hdf[L][Hdf[L].notnull()]
#print(np.unique(tmp))
#if 'w' in np.unique(tmp):
    #print('here')
#tmp[tmp != 'na'].max()
#print(S)
#print(roomdf)


# In[23]:

#python script.py >> /wwbintz/matinsy/var/websync.log 2>&1


# ## db integrety checking
# maybe put this stuff in a different file

# In[ ]:



