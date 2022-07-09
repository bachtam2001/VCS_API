from flask.templating import render_template
import websocket
import requests
import threading
import json
import logging
import asyncio
from time import gmtime, strftime
from flask import Flask, request
from BanPick import VCSBanPick
from Ingame import VCSIngame
app = Flask("__name__")

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

BanPick = VCSBanPick()
Ingame = VCSIngame()


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
    return json.dumps(BanPick.Ban)

@app.route('/Pick')
def getPick():
    return json.dumps(BanPick.Pick)

@app.route('/Team')
def getTeam():
    Team = []
    for data in BanPick.Team:
        Team.append({"Team":data})
    return json.dumps(Team)

@app.route('/Player')
def getPlayer():
    Player = []
    for data in BanPick.Player:
        Player.append({"Player":data})
    return json.dumps(Player)

@app.route('/State')
def getState():
    if (BanPick.TimerFormat == "ss"):
        Timer = BanPick.Timer
        if (BanPick.Timer<10):
            Timer = "0" + str(Timer)
    elif (BanPick.TimerFormat == "mm:ss"):
        Timer = strftime("%M:%S", gmtime(int(BanPick.Timer)))
    elif (BanPick.TimerFormat == "hh:mm:ss"):
        Timer = strftime("%H:%M:%S", gmtime(int(BanPick.Timer)))
    else:
        Timer = BanPick.Timer
    return json.dumps([{"Timer": Timer,"State": BanPick.State}])


@app.route('/Ingame')
def getIngame():
    Ingame.BlueBar["Gold"] = Ingame.convertLoLGold(Ingame.gold["blue"])
    Ingame.RedBar["Gold"] = Ingame.convertLoLGold(Ingame.gold["red"])
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
        "Time": Ingame.convertLoLTime(Ingame.timer),
        "Dragon": Ingame.convertObjectTime(Ingame.dragontimer),
        "Herald" : Ingame.convertObjectTime(Ingame.heraldtimer),
        "Baron" : Ingame.convertObjectTime(Ingame.barontimer),
        "HeraldIcon" : Ingame.rehaldicon,
        "HeraldBG" : Ingame.rehaldbackground,
    }]
    return json.dumps(data)

@app.route('/Object')
def getObject():
    data = [{
        "ElderTime": Ingame.convertObjectTime(Ingame.eldertimeremain),
        "ElderTeamName" : Ingame.elderteamname,
        "ElderBG" : Ingame.elderbackground,
        "BaronTime": Ingame.convertObjectTime(Ingame.barontimeremain),
        "BaronTeamName" : Ingame.baronteamname,
        "BaronBG" : Ingame.baronbackground,
        "BaronPowerPlay" : '{0:+}'.format(Ingame.baronpowerplay),
    }]
    return json.dumps(data)

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
                Ingame.NumDragonBlue=1
            Ingame.BlueDragon["dragon1"] = Ingame.dragonpath + request.form["DragonBlue1"] + ".png"
            if (request.form["DragonBlue2"]!="None"):
                Ingame.NumDragonBlue=2
            Ingame.BlueDragon["dragon2"] = Ingame.dragonpath + request.form["DragonBlue2"] + ".png"        
            if (request.form["DragonBlue3"]!="None"):
                Ingame.NumDragonBlue=3
            Ingame.BlueDragon["dragon3"] = Ingame.dragonpath + request.form["DragonBlue3"] + ".png"        
            if (request.form["DragonBlue4"]!="None"):
                Ingame.NumDragonBlue=4
            Ingame.BlueDragon["dragon4"] = Ingame.dragonpath + request.form["DragonBlue4"] + ".png"
            if (request.form["DragonBlueSoul"]!="None"):
                Ingame.BlueDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonBlueSoul"] + "_Soul.png"
            else:
                Ingame.BlueDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonBlueSoul"] + ".png"
        if ("DragonRed1" in request.form):
            if (request.form["DragonRed1"]!="None"):
                Ingame.NumDragonRed=1
            Ingame.RedDragon["dragon1"] = Ingame.dragonpath + request.form["DragonRed1"] + ".png"
            if (request.form["DragonRed2"]!="None"):
                Ingame.NumDragonRed=2
            Ingame.RedDragon["dragon2"] = Ingame.dragonpath + request.form["DragonRed2"] + ".png"        
            if (request.form["DragonRed3"]!="None"):
                Ingame.NumDragonRed=3
            Ingame.RedDragon["dragon3"] = Ingame.dragonpath + request.form["DragonRed3"] + ".png"        
            if (request.form["DragonRed4"]!="None"):
                Ingame.NumDragonRed=4
            Ingame.RedDragon["dragon4"] = Ingame.dragonpath + request.form["DragonRed4"] + ".png"
            if (request.form["DragonRedSoul"]!="None"):
                Ingame.RedDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonRedSoul"] + "_Soul.png"
            else:
                Ingame.RedDragon["dragonsoul"] = Ingame.dragonpath + request.form["DragonRedSoul"] + ".png"
        if ("timer" in request.form):
            BanPick.TimerFormat = request.form["timer"]
    return render_template('admin.html', Ingame=Ingame)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='3006', threaded=True,debug=False)