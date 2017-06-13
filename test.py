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

df= pd.DataFrame.from_dict(d,orient='index')
df.rename(columns={0:'room',1:'CAS',2:'reorder',3:'name'},inplace=True)
df.index.name = 'CATID'
df['regtype'] = 'none'


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

for CATID in df.index:
    #print(CATID)
    CAS = df.loc[CATID].CAS
    regtype = getregtype(CAS,dbfile)
    df.set_value(CATID,'regtype',regtype)


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

df = df.sort_values('room')

#df.style.applymap(color_negative_red,subset=['regtype'])
#df.style.set_properties(**{'background-color': 'black',
#                           'color': 'lawngreen',
#                           'border-color': 'white'})
#significant = lambda x: '<span class="significant">%f</span>' % x if x<0.05 else str(x)
ofile = './output/flat.html'
#table = df.to_html(formatters={'regtype':lambda x: color_negative_red(x)})

#table = df.to_html(formatters={'regtype':lambda x: highlight_vals(x)},escape=False)

#TODO:  filter out UNK, retired, etc.
#dfout = df[df['room'] != 'retired']
#dfout = dfout[dfout['room'] != 'retire'] 
#dfout = dfout[dfout['room'] != 'UNK']
dumplist = ['retire','retired','UNK','combine']
mask = df.room.isin( dumplist)
dfout = df[mask]
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
with open(ofile, 'w') as f:
    f.write( tp)
    f.write(dfout.style.applymap(highlight_vals, subset=['regtype']).set_table_attributes("border=1").render())
    f.write(dn)
