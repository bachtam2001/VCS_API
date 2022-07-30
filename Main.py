import json
import logging
from time import gmtime, strftime
from flask import Flask, request
from BanPick import VCSBanPick
from Ingame import VCSIngame
from waitress import serve
from tinydb import TinyDB
app = Flask("__name__")
db = TinyDB('db.json')
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

BanPick = VCSBanPick(db)
Ingame = VCSIngame(db)


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
    return json.dumps(BanPick.Player)

@app.route('/State')
def getState():
    if (BanPick.TimerFormat == "ss"):
        Timer = str(BanPick.Timer)
        if (BanPick.Timer<10):
            Timer = "0" + Timer
    elif (BanPick.TimerFormat == "mm:ss"):
        Timer = strftime("%M:%S", gmtime(int(BanPick.Timer)))
    elif (BanPick.TimerFormat == "hh:mm:ss"):
        Timer = strftime("%H:%M:%S", gmtime(int(BanPick.Timer)))
    else:
        Timer = str(BanPick.Timer)
    return json.dumps([{"Timer": Timer,"State": BanPick.State}])


@app.route('/Score')
def getIngame():
    BlueBar, RedBar = Ingame.getScoreBar()
    BlueBar["Gold"] = Ingame.convertLoLGold(Ingame.gold["blue"])
    RedBar["Gold"] = Ingame.convertLoLGold(Ingame.gold["red"])
    data = []
    data.append(BlueBar)
    data.append(RedBar)
    return json.dumps(data)

@app.route('/POV')
def getPOV():
    data = []
    Player = BanPick.Player
    for i in range(5):
        player = {"Blue": Player[i]["Image"], "Red": Player[i+5]["Image"]}
        data.append(player)
    return json.dumps(data)
    
@app.route('/Dragon')
def getDragon():
    data = []
    DragonBlue,DragonRed = Ingame.getDragon()
    for i in range(5):
        dragon = {"Blue": DragonBlue[i], "Red": DragonRed[i]}
        data.append(dragon)
    return json.dumps(data)

@app.route('/Timer')
def getTime():
    data = [{
        "Time": Ingame.convertLoLTime(Ingame.timer),
        "Dragon": Ingame.convertObjectTime(Ingame.dragontimer),
        "DragonType": Ingame.dragontype,
        "Herald" : Ingame.convertObjectTime(Ingame.heraldtimer),
        "Baron" : Ingame.convertObjectTime(Ingame.barontimer),
        "HeraldIcon" : Ingame.heraldicon,
        "HeraldBG" : Ingame.heraldbackground,
    }]
    return json.dumps(data)

@app.route('/Object')
def getObject():
    Ingame.getObject()
    if (Ingame.elderteamtaken=="Blue"):
        Elder_Team_Name = BanPick.Team[0]["Name"]
    elif (Ingame.elderteamtaken=="Red"):
        Elder_Team_Name = BanPick.Team[1]["Name"]
    else:
        Elder_Team_Name = ""
    if (Ingame.baronteamtaken=="Blue"):
        Baron_Team_Name = BanPick.Team[0]["Name"]
    elif (Ingame.baronteamtaken=="Red"):
        Baron_Team_Name = BanPick.Team[1]["Name"]
    else:
        Baron_Team_Name = ""
        
    if Ingame.baronpowerplay != 0:
        baronpowerplay = '{0:+d}'.format(Ingame.baronpowerplay) 
    else:
        baronpowerplay = '0'
    data = [{
        "ElderTime": Ingame.convertObjectTime(Ingame.eldertimeremain),
        "ElderTeamName" : Elder_Team_Name,
        "ElderBG" : Ingame.elderbackground,
        "BaronTime": Ingame.convertObjectTime(Ingame.barontimeremain),
        "BaronTeamName" : Baron_Team_Name,
        "BaronBG" : Ingame.baronbackground,
        "BaronPowerPlay" : (baronpowerplay if Ingame.barontimeremain > 0 else '')
    }]
    return json.dumps(data)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=3005, threads=8)
