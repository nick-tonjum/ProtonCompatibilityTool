import tkinter as tk
from tkinter import ttk
from pathlib import Path
import vdf
import requests
from PIL import ImageTk, Image
import os
import pickle

steamfolderlocation = "/home/" + os.getlogin() + "/.steam"

registryfilelocation = steamfolderlocation + "/registry.vdf"
registryfilelocationpath = Path(registryfilelocation)

d = vdf.load(open(registryfilelocation))
d = vdf.parse(open(registryfilelocation))
vdf_text = vdf.dumps(d)
indented_vdf = vdf.dumps(d, pretty=True)

dbresponse = requests.get("https://protondb.max-p.me/games/")
dbscraped = dbresponse.json()

sortdirection = "UP"

try:
    with open('session.pct', 'rb') as handle:
        gamedictionary = pickle.load(handle)
except:
    gamedictionary = {}

def UpdateDictionary():
    global root, gamedictionary, sortdirection
    gamedictionary = {}
    for game in d["Registry"]["HKCU"]["Software"]["Valve"]["Steam"]["Apps"].keys():
        sortdirection = "UP"
        response = requests.get("https://protondb.max-p.me/games/" + game + "/reports")
        scraped = response.json()
        gamename = ""
        if not len(scraped) == 0:
            try:
                gamename = str(d["Registry"]["HKCU"]["Software"]["Valve"]["Steam"]["Apps"][game]["name"])
            except:
                try:
                    for dbgame in dbscraped:
                        if dbgame["appId"] == game:
                            gamename = str(dbgame["title"])
                except:
                    gamename = str(game)
            print(gamename)
            ratingscore = 0
            totalratings = 0
            protonversions = []
            launchoptions = []
            nativementions = 0
            totalnotes = 0
            for i in range (0,len(scraped)):
                totalratings += 1
                rating = scraped[i]["rating"]
                protonversions.append(scraped[i]["protonVersion"])
                if not scraped[i]["notes"] == None:
                    totalnotes += 1
                    if "launch options" in scraped[i]["notes"]:
                        launchoptions.append(scraped[i]["notes"])
                    if " native" in scraped[i]["notes"]:
                        nativementions += 1
                if rating == "Native":
                    ratingscore += 10
                elif rating == "Platinum":
                    ratingscore += 10
                elif rating == "Gold":
                    ratingscore += 8
                elif rating == "Silver":
                    ratingscore += 6
                elif rating == "Bronze":
                    ratingscore += 4
                elif rating == "null":
                    totalratings -= 1
                else:
                    pass
            #print("Native Mentions: " + str(nativementions) + " of " + str(totalnotes) + " notes")
            namedrating = ""
            if round((ratingscore/totalratings),2) >= 9.5:
                namedrating = "Platinum"
            elif round((ratingscore/totalratings),2) >= 9:
                namedrating = "Gold+"
            elif round((ratingscore/totalratings),2) >= 8:
                namedrating = "Gold"
            elif round((ratingscore/totalratings),2) >= 7:
                namedrating = "Silver+"
            elif round((ratingscore/totalratings),2) >= 6:
                namedrating = "Silver"
            elif round((ratingscore/totalratings),2) >= 5:
                namedrating = "Bronze+"
            elif round((ratingscore/totalratings),2) >= 4:
                namedrating = "Bronze"
            elif round((ratingscore/totalratings),2) >= 2:
                namedrating = "Kinda Borked"
            else:
                namedrating = "Fully Borked"
            if totalnotes >= 2:
                if nativementions >= round((totalnotes/4),2):
                    namedrating = "Native"
            gamedictionary[gamename] = {"Rating":str(round((ratingscore/totalratings),2)),"Ranking":namedrating,"Proton":str(max(set(protonversions), key = protonversions.count)),"Options":str(launchoptions)}
            PlotDictionary()
            root.update()
            root.update_idletasks()
    with open('session.pct', 'wb') as handle:
        pickle.dump(gamedictionary,handle,protocol=pickle.HIGHEST_PROTOCOL)

def Colorize():
    global showcolor
    if showcolor.get() == 1:
        tree.tag_configure('Native', background="#A2FF74")
        tree.tag_configure('Platinum', background='#00FFFC')
        tree.tag_configure('Gold+', background='#FFF100')
        tree.tag_configure('Gold', background='#FFFBAD')
        tree.tag_configure('Silver+', background='#A6A6A6')
        tree.tag_configure('Silver', background='#E0E0E0')
        tree.tag_configure('Bronze+', background='#8D624A')
        tree.tag_configure('Bronze', background='#E5BFAA')
        tree.tag_configure('Kinda Borked', background='#FF2D00')
        tree.tag_configure('Fully Borked', background='#9A0000')
    else:
        tree.tag_configure('Native', background="#ffffff")
        tree.tag_configure('Platinum', background="#ffffff")
        tree.tag_configure('Gold+', background="#ffffff")
        tree.tag_configure('Gold', background="#ffffff")
        tree.tag_configure('Silver+', background="#ffffff")
        tree.tag_configure('Silver', background="#ffffff")
        tree.tag_configure('Bronze+', background="#ffffff")
        tree.tag_configure('Bronze', background="#ffffff")
        tree.tag_configure('Kinda Borked', background="#ffffff")
        tree.tag_configure('Fully Borked', background="#ffffff")

def PlotDictionary(filter="none",sort="rating"):
    global tree,root,sortdirection,showcolor
    for record in tree.get_children():
        tree.delete(record)
    gamelist = []
    if sort == "alphabetical":
        for game in gamedictionary.keys():
            gamelist.append(game)
        gamelist.sort()
    elif sort == "rating":
        whilerating = 10.0
        for game in gamedictionary.keys():
            if gamedictionary[game]["Ranking"] == "Native":
                gamelist.append(game)
        while whilerating >= 0:
            for game in gamedictionary.keys():
                if str(gamedictionary[game]["Rating"]) == str(whilerating):
                    if not gamedictionary[game]["Ranking"] == "Native":
                        gamelist.append(game)
            whilerating -= 0.01
            whilerating = round(whilerating, 2)
    if sortdirection == "UP":
        sortdirection = "DOWN"
    else:
        gamelist.reverse()
        sortdirection = "UP"
    for game in gamelist:
        if not gamedictionary[game]["Ranking"] == "Native":
            tree.insert(parent='',index='end', text=str(game), tags = [str(gamedictionary[game]["Ranking"])], values=(str(gamedictionary[game]["Ranking"] + " (" + gamedictionary[game]["Rating"] + ")"),gamedictionary[game]["Proton"]))
        else:
            tree.insert(parent='', index='end', text=str(game), tags=[str(gamedictionary[game]["Ranking"])], values=(
            str(gamedictionary[game]["Ranking"]),
            gamedictionary[game]["Proton"]))
    Colorize()

root = tk.Tk()
root.title("Proton Compatibility Tool")
root.geometry("960x720")
root.configure(bg="#d9d9f2")

tree=ttk.Treeview(root)

refreshimage = ImageTk.PhotoImage(Image.open(Path(os.getcwd() + "/assets/refresh.png")))
refreshbutton = tk.Button(root, image=refreshimage,width=50,height=50,command=lambda: UpdateDictionary())
refreshbutton.place(x=20,y=120)

fakeimage = tk.PhotoImage()

alphabeticalsortbutton = tk.Button(root, compound="center", image=fakeimage,width=30,height=10,text="Sort", command=lambda: PlotDictionary(sort="alphabetical"))
alphabeticalsortbutton.place(x=246,y=70)


showcolor = tk.IntVar()
showtechnical = tk.IntVar()

showcolor.set(1)

showcolorcheckbutton = tk.Checkbutton(root, variable=showcolor, onvalue=1, offvalue=0, text="Show Colors", bg="#d9d9f2", command=Colorize)
showcolorcheckbutton.place(x=700,y=70)

ratingsortbutton = tk.Button(root, compound="center", image=fakeimage,width=30,height=10,text="Sort", command=lambda: PlotDictionary(sort="rating"))
ratingsortbutton.place(x=491,y=70)

tree["columns"]=("one","two")
tree.column("#0", width=350, minwidth=350, stretch=tk.NO)
tree.column("one", width=140, minwidth=140, anchor=tk.CENTER, stretch=tk.NO)
tree.column("two", width=258, minwidth=258, anchor=tk.CENTER, stretch=tk.NO)

tree.heading("#0",text="Game",anchor=tk.N)
tree.heading("one", text="Rating",anchor=tk.N)
tree.heading("two", text="Recommended Proton Version",anchor=tk.N)

tree.place(x=100,y=100,width=750,height=575)
root.update()
root.update_idletasks()


treescrollbar = ttk.Scrollbar(root,orient="vertical",command=tree.yview)
treescrollbar.place(x=(tree.winfo_x()+tree.winfo_width()),y=(tree.winfo_y()),width=20,height=tree.winfo_height())
tree.configure(xscrollcommand=treescrollbar.set)


root.update()
root.update_idletasks()
PlotDictionary()

while True:
    root.update()
    root.update_idletasks()
