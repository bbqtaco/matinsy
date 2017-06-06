import tkinter as tk
import sqlite3

dbfile = 'db/chemicalinventory.db'

def dosql (cmd) :
    print(cmd)
    #c = db.query(cmd)
    #setSelect ()

def addEntry () :
    print('here')
    #c = db.query("select max(id)+1 from phones")
    #id = c.fetchdict()[0].values()[0]  # digs deep to get next id
    #dosql("insert into phones values (%d,'%s','%s')" % (id,nameVar.get(), phoneVar.get()))


def updateEntry() :
    print('here')
    #id = phoneList[whichSelected()][0]
    #dosql("update phones set name='%s', phone='%s' where id=%d" % (nameVar.get(), phoneVar.get(), id))

def deleteEntry():
    print('here')
    #id = phoneList[whichSelected()][0]
    #dosql("delete from phones where id=%d" % id)

def loadEntry  () :
    print('here')
    #id, name, phone = phoneList[whichSelected()]
    #nameVar.set(name)
    #phoneVar.set(phone)
    
def makeWindow () :
    global nameVar, phoneVar, select
    win = tk.Tk()

    frame1 = tk.Frame(win)
    frame1.pack()

    tk.Label(frame1, text="Name").grid(row=0, column=0, sticky=tk.W)
    nameVar = tk.StringVar()
    name = tk.Entry(frame1, textvariable=nameVar)
    name.grid(row=0, column=1)

    tk.Label(frame1, text="Phone").grid(row=1, column=0, sticky=tk.W)
    phoneVar= tk.StringVar()
    phone= tk.Entry(frame1, textvariable=phoneVar)
    phone.grid(row=1, column=1,sticky=tk.W)

    frame2 = tk.Frame(win)       # Row of buttons
    frame2.pack()
    b1 = tk.Button(frame2,text=" Add  ",command=addEntry)
    b2 = tk.Button(frame2,text="Update",command=updateEntry)
    b3 = tk.Button(frame2,text="Delete",command=deleteEntry)
    b4 = tk.Button(frame2,text="Load  ",command=loadEntry)
    b5 = tk.Button(frame2,text="Refresh",command=setSelect)
    b1.pack(side=tk.LEFT); b2.pack(side=tk.LEFT)
    b3.pack(side=tk.LEFT); b4.pack(side=tk.LEFT); b5.pack(side=tk.LEFT)

    frame3 = tk.Frame(win)       # select of names
    frame3.pack()
    scroll = tk.Scrollbar(frame3, orient=tk.VERTICAL)
    select = tk.Listbox(frame3, yscrollcommand=scroll.set, height=6)
    scroll.config (command=select.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    select.pack(side=tk.LEFT,  fill=tk.BOTH, expand=1)
    return win

def setSelect () :
    global phoneList
    print('here')
    #c = db.query("select id,name,phone from phones order by name")
    #phoneList = c.fetchrows()
    #select.delete(0,END)
    #for id,name,phone in phoneList :
    #    select.insert (END, name)

win = makeWindow()
#setSelect ()
win.mainloop()
