import asyncio
import logging
import json
import threading
import requests
from datetime import datetime

class VCSIngame:
    def __init__(self):
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        self.load_config()
        self.event = None
        self.json = ""
        self.setData()  
        let = threading.Thread(target=self.start)
        let.start()

    def setData(self):
        self.logfile = "./log/ingame/" + datetime.now().strftime("%d-%m-%Y %H-%M-%S")+".log"
        self.BlueBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0
        }
        self.RedBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0
        }      
        self.NumDragonBlue = 1
        self.NumDragonRed = 1
        self.BlueDragon = {
            "dragon1": self.dragonpath + "None.png",
            "dragon2": self.dragonpath + "None.png",
            "dragon3": self.dragonpath + "None.png",
            "dragon4": self.dragonpath + "None.png",
            "dragonsoul": self.dragonpath + "None.png",
        }
        self.RedDragon = {
            "dragon1": self.dragonpath + "None.png",
            "dragon2": self.dragonpath + "None.png",
            "dragon3": self.dragonpath + "None.png",
            "dragon4": self.dragonpath + "None.png",
            "dragonsoul": self.dragonpath + "None.png",
        }


    def load_config(self):
        self.ip = self._config["OBS_IP"]
        vmip = self._config["Vmix_IP"]
        vmport = self._config["Vmix_Port"]
        self.Url = "http://" + vmip + ":" + vmport + "/api/?Function="
        self.port = self._config["Ingame_Event_Port"]
        self.dragonpath = self._config["Dragon_Icon"]

    def start(self):
        while True:
            self.file = open(self.logfile, "ab+")
            asyncio.run(self.process())
            self.file.close()

    async def process(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            print("Live Event API Connected\n")
            while not self.reader.at_eof():
                data = await self.reader.readline()
                self.file.write(data)
                self.parseData(data)
            try:
                self.writer.close()
                print("Live Event API Disconnected\n")
            except Exception as msg:
                #print("Live Event API Connect Error\n")
                print(msg)
                return
        except Exception as msg:
            #print(msg)
            return

            
    def parseData(self, data):
        if (data==b'}\n'):
            self.json += data.decode("utf-8")
            self.parseJSON()
            self.json = ""
        else:
            self.json += data.decode("utf-8")

    def parseJSON(self):
        try:
            self.event = json.loads(self.json)
        except Exception as msg:
            self.event = None
            #print(msg)
            return
        if (self.event["eventname"] == "OnGameStart"):
            self.setData()
        elif (self.event["eventname"] == "OnChampionKill"):
            if (self.event["sourceTeam"] == "Order"):
                self.BlueBar["Kill"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.RedBar["Kill"] += 1        
        elif (self.event["eventname"] == "OnTurretDie"):
            if (self.event["sourceTeam"] == "Order"):
                self.RedBar["Turret"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.BlueBar["Turret"] += 1   
        elif (self.event["eventname"] == "OnKillDragon_Spectator"): # Dragon Event
            if (self.event["sourceTeam"] == "Order"):
                if (self.event["other"] == "SRU_Dragon_Air"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Air.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Air_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Fire"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Fire.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Fire_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Water"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Water.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Water_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Earth"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Earth.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Earth_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Hextech"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Hextech.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Hextech_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Chemtech"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Chemtech.png"
                    if (self.NumDragonBlue==4):
                        self.BlueDragon["dragonsoul"] = self.dragonpath + "Chemtech_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Elder"): # Elder Blue Event
                    self.vmixfunc("OverlayInput4In","Elder Team 1")
                    return
                self.NumDragonBlue += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                if (self.event["other"] == "SRU_Dragon_Air"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Air.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Air_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Fire"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Fire.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Fire_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Water"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Water.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Water_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Earth"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Earth.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Earth_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Hextech"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Hextech.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Hextech_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Chemtech"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Chemtech.png"
                    if (self.NumDragonRed==4):
                        self.RedDragon["dragonsoul"] = self.dragonpath + "Chemtech_Soul.png"
                elif (self.event["other"] == "SRU_Dragon_Elder"): # Elder Red Event
                    self.vmixfunc("OverlayInput4In","Elder Team 2")
                    return
                self.NumDragonRed += 1

        elif (self.event["eventname"] == "OnKillWorm_Spectator"): #Baron Event
            if (self.event["sourceTeam"] == "Order"):
                   self.vmixfunc("OverlayInput3In","Baron Team 1")
            elif (self.event["sourceTeam"] == "Chaos"):
                   self.vmixfunc("OverlayInput3In","Baron Team 2")


    def vmixfunc(self, func, input):
        url = self.Url + func + "&Input=" + input
        try:
            requests.get(url)
        except:
            pass