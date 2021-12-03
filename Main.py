from flask.templating import render_template
import websocket
import requests
import json
import threading, time
import logging
import asyncio
from flask import Flask, request
from BanPick import VCSBanPick
from InGame import VCSIngame
from IGTimer import VCSTimer     

app = Flask("__name__")
BanPick = VCSBanPick()
Ingame = VCSIngame()
Timer = VCSTimer()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return '''VCS Broadcast API <br>
    /Admin : Manual Change Ingame Value <br>
    /Ban : Get Champion Ban <br>
    /Pick : Get Champion Pick <br>
    /Team : Get Team Name <br>
    /Player : Get Player Name <br>
    /State : Get State and Timer Ban Pick <br>
    /Ingame : Get Ingame Gold and Turret <br>
    /Timer : Get Ingame Timer<br>
    '''

@app.route('/Ban')
def getBan():
    return json.dumps(BanPick.Ban);

@app.route('/Pick')
def getPick():
    return json.dumps(BanPick.Pick);

@app.route('/Team')
def getTeam():
    Team = []
    for data in BanPick.TeamName:
        Team.append({"Team":data})
    return json.dumps(Team)

@app.route('/Player')
def getPlayer():
    Player = []
    for data in BanPick.TeamPlayer:
        Player.append({"Player":data})
    return json.dumps(Player)

@app.route('/State')
def getState():
    if (BanPick.Timer<10):
        Timer = "0" + str(BanPick.Timer)
    else:
        Timer = str(BanPick.Timer)
    return json.dumps([{"State":BanPick.StateArrow,"Timer": Timer}])
    
@app.route('/Admin', methods = ['POST', 'GET'])
def editIngame():
    if request.method == 'POST':
        if ("BKill" in request.form):
            Ingame.BlueBar["Kill"] = request.form["BKill"]
        if ("BTurret" in request.form):
            Ingame.BlueBar["Turret"] = request.form["BTurret"]
        if ("RKill" in request.form):
            Ingame.RedBar["Kill"] = request.form["RKill"]
        if ("RTurret" in request.form):
            Ingame.RedBar["Turret"] = request.form["RTurret"]
        if ("DragonBlue1" in request.form):
            if (request.form["DragonBlue1"]!="None"):
                Ingame.NumDragonBlue=2
            else:
                Ingame.NumDragonBlue=1
            if (request.form["DragonBlue2"]!="None"):
                Ingame.NumDragonBlue=3
            if (request.form["DragonBlue3"]!="None"):
                Ingame.NumDragonBlue=4
            Ingame.BlueDragon["dragon1"] = Ingame.dragonpath + request.form["DragonBlue1"] + ".png"
            Ingame.BlueDragon["dragon2"] = Ingame.dragonpath + request.form["DragonBlue2"] + ".png"        
            Ingame.BlueDragon["dragon3"] = Ingame.dragonpath + request.form["DragonBlue3"] + ".png"
            Ingame.BlueDragon["dragon4"] = Ingame.dragonpath + request.form["DragonBlue4"] + ".png"
            if (request.form["DragonBlueSoul"]!="None"):
                Ingame.BlueDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonBlueSoul"] + "_Soul.png"
            else:
                Ingame.BlueDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonBlueSoul"] + ".png"
        if ("DragonRed1" in request.form):
            if (request.form["DragonRed1"]!="None"):
                Ingame.NumDragonRed=2
            else:
                Ingame.NumDragonRed=1
            if (request.form["DragonRed2"]!="None"):
                Ingame.NumDragonRed=3       
            if (request.form["DragonRed3"]!="None"):
                Ingame.NumDragonRed=4
            Ingame.RedDragon["dragon1"] = Ingame.dragonpath + request.form["DragonRed1"] + ".png"
            Ingame.RedDragon["dragon2"] = Ingame.dragonpath + request.form["DragonRed2"] + ".png" 
            Ingame.RedDragon["dragon3"] = Ingame.dragonpath + request.form["DragonRed3"] + ".png"        
            Ingame.RedDragon["dragon4"] = Ingame.dragonpath + request.form["DragonRed4"] + ".png"
            if (request.form["DragonRedSoul"]!="None"):
                Ingame.RedDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonRedSoul"] + "_Soul.png"
            else:
                Ingame.RedDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonRedSoul"] + ".png"
    return render_template('admin.html', Ingame=Ingame)

@app.route('/Ingame')
def getIngame():
    Ingame.BlueBar["Gold"] = Timer.gold["blue"]
    Ingame.RedBar["Gold"] = Timer.gold["red"]
    data = []
    data.append(Ingame.BlueBar)
    data.append(Ingame.RedBar)
    return json.dumps(data)

@app.route('/Dragon')
def getDragon():
    data = []
    data.append(Ingame.BlueDragon)
    data.append(Ingame.RedDragon)
    return json.dumps(data)

@app.route('/Timer')
def getTime():
    data = [{
        "Time": Timer.live,
        "Dragon": Timer.dragon["timer"],
        "Dragon_Type" : Timer.dragon["type"],
        "Baron" : Timer.baron["timer"]
    }]
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='3005', threaded=True)