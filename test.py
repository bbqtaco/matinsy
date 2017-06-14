import tkinter as tk
import sqlite3
import numpy as np
import pandas as pd
from os import system, path
import glob

dbfile = 'db/cheminventory.db'

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

tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory searchable </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > Links in RED are Potentially Hazardous Substances</H1>\n<H2>See the last words in each red link for additional info</H2>\n'
hd = '<H1>'  
he = '</H1>\n'
lt = '<UL>'
le = '</UL>'
li = '<LI>'
dn = '</BODY>\n </HTML>\n'

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
        regtype = 'none'
    conn.commit()
    c.close()
    return regtype  #chemname,CAS,reorder,CATID

def getsdsfilename(CAS,reorder):
    #conn = sqlite3.connect(dbfile)
    #c = conn.cursor()
    #c.execute('select reorder,CAS from Bot where CATID=?',[CATID])
    #tmp = c.fetchall()
    #if tmp1:
    #    reorder = tmp1[0][0]
    #else:
    #    reorder = 'none'
    #CAS = tmp1[0][1]
    #print(CATID,'tmp',tmp1[0])
    
    #conn.commit()
    #c.close()
    if CAS ==None:
        CAS = 'none' #generic
    msdsbase = './html/'
    if reorder==None:
        reorder='none' #generic
    tmp = msdsbase + CAS+'_'+reorder
    if tmp[-4:] == 'none':
        fname = tmp[:-5]
    else:
        fname = tmp

    fname += '.pdf'
    sdsfilename = fname
    link = '<A HREF='+fname+'>'+'LINK'+'</A>'
    if path.isfile(fname) == True:
        pass
    else:
        missing = fname
    return link,missing


df= pd.DataFrame.from_dict(d,orient='index')
df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
df.index.name = 'CATID'
df['regtype'] = 'none'
df['msds_file'] = 'none'
df['missing info'] = 'none'

roomsdf = df.room.unique()
roomslist = roomsdf.tolist()
#filter rooms that should not be rooms
tmp = [ x for x in roomslist if 'retire' not in x ]
tmp = [ x for x in tmp if 'combine' not in x ]
tmp = [ x for x in tmp if 'neu' not in x ]

rooms = tmp

CAS = '993-43-1'
CAS = 'na4'
CAS = '1-0-0001'
regtype = getregtype(CAS,dbfile)

missinglist = []
for CATID in df.index:
    #print('CATID',CATID)
    CAS = df.loc[CATID].CAS
    reorder = df.loc[CATID].reorder
    regtype = getregtype(CAS,dbfile)
    link,missing = getsdsfilename(CAS,reorder)
    missinglist.append(missing)
    df.set_value(CATID,'regtype',regtype)
    df.set_value(CATID,'msds_file',link)
    df.set_value(CATID,'missing info',missing)

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

#df = df.sort_values('room')

#df.style.applymap(color_negative_red,subset=['regtype'])
#df.style.set_properties(**{'background-color': 'black',
#                           'color': 'lawngreen',
#                           'border-color': 'white'})
#significant = lambda x: '<span class="significant">%f</span>' % x if x<0.05 else str(x)

#table = df.to_html(formatters={'regtype':lambda x: color_negative_red(x)})

#table = df.to_html(formatters={'regtype':lambda x: highlight_vals(x)},escape=False)

#TODO:  filter out UNK, retired, etc.
#dfout = df[df['room'] != 'retired']
#dfout = dfout[dfout['room'] != 'retire'] 
#dfout = dfout[dfout['room'] != 'UNK']

#df.room.str.contains('retire*')

dumplist = ['retire*','UNK','combine','neut','Unk']
mask = df.room.notnull()
for item in dumplist:
    mask = mask & ~df.room.str.contains(item)
    
#mask = df.room.isin( dumplist)
dfout = df[mask].sort_values('room')

#f = open(ofile, 'w')
#f.write( tp)
#f.write( hd)
#f.write(room)
#f.write( he)
#f.write(lt)
#f.write(table)
#f.write( le)

#f.write(dn)

#f.close()
#for room in rooms:
#    print(room)
#    tmpcatid,tmpreg = coimodbyroom(CAS,dbfile)
#    tmpdreg
#select RegType from Coi where CAS =  '993-43-1';

##output flat
ofile = './output/flat.html'
with open(ofile, 'w') as f:
    f.write( tp)
    f.write(dfout.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render())
    f.write(dn)

def writehtml(ofile,df):
    tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory  </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > Links in RED are Potentially Hazardous Substances</H1>\n<H2>See the last words in each red link for additional info</H2>\n'

    dn = '</BODY>\n </HTML>\n'
    with open(ofile, 'w') as f:
        f.write( tp)
        f.write(df.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render())
        f.write(dn)

##output room files
roomsarray = dfout.room.unique()
rooms = roomsarray.tolist()
rooms.remove('')

for room in rooms:
    dfroomout = dfout[dfout.room == room]
    ofile = './output/sds_'+room +'.html'
    writehtml(ofile,dfroomout.sort_values('name'))


##write master sds file
tp = '<HTML>\n <HEAD><TITLE>SDS chemical inventory  </TITLE></HEAD>\n<BODY>\n<H1 style=\"color:red\" > Links in RED are Potentially Hazardous Substances</H1>\n<H2>See the last words in each red link for additional info</H2>\n'
dn = '</BODY>\n </HTML>\n'
lt = '<UL>'
le = '</UL>'
li = '<LI>'
ofile = './output/index.html'
htmlbase='./'
files =  glob.glob("./output/sds_*.html")
f = open(ofile, 'w')
f.write( tp)
f.write(lt)
for file in np.sort(files):
    print(file)
    room = file.split('_')[1].split('.')[0]
    pathfile = htmlbase+file.split('/')[-1]
    link = li+'<A HREF='+pathfile+'>'+room+'</A>\n'
    print(room)
    f.write(link)
f.write(le)
f.write(dn)
f.close()
#if path.isfile(fname) == True:
#    pass
#else:
#    missing = fname

