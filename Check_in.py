#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sense_hat import SenseHat
import socket
import time
import requests as req

class CheckIn():
    
    def __init__(self):

        self.s = SenseHat()
        self.s.low_light = True
        
        self.gC = (0, 255, 0)
        self.yC = (255, 255, 0)
        self.bC = (0, 0, 255)
        self.rC = (255, 0, 0)
        self.dRC = (30, 0 ,0)
        self.wC = (255,255,255)
        self.nC = (0,0,0)
        self.pC = (255, 105, 180)
        
        self.lokaleData = []
        self.kortData = []
        self.Room = 1
        self.User = 1
        self._get_Data()
        
        
        self.serverIP = '192.168.24.201'
        self.serverPort = 7221
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.currentRoom = self.lokaleData[0]
        self.currentUser = self.kortData[0]
        self.checkIn = False
        self.image = []
        for n in range(8*8):
            self.image.append(self.nC)
    
    def _get_Data(self):
        self.lokaleData=[]
        self.kortData=[]
        print("Getting Data")
        try:
            db_online_data = req.get("https://restogtests20221210170609.azurewebsites.net/api/Lokale") 
            json = db_online_data.json()
            for row in json:
                self.lokaleData.append([row["lokaleId"],row["cardId"]])
        except Exception as e:
            print("Error getting local data:", e)
        
        try:
            db_online_data = req.get("https://restogtests20221210170609.azurewebsites.net/api/Kort") 
            json = db_online_data.json()
            for row in json:
                self.kortData.append([row["cardId"],row["kort_Ejer"]])
        except Exception as e:
            print("Error getting card data:", e)
        
        self._object_Chooser()
    
    def _room_Free(self):
        g = self.gC
        w = self.wC
        n = self.nC
        
        self.image = [
        g, g, w, w, w, w, g, g,
        g, g, w, g, g, w, g, g,
        g, g, w, g, g, g, g, g,
        g, w, w, w, w, w, w, g,
        g, w, w, n, n, w, w, g,
        g, w, w, n, n, w, w, g,
        g, w, w, n, n, w, w, g,
        g, w, w, w, w, w, w, g,
        ]
    
    def _denied(self):
        r = self.rC
        d = self.dRC
        n = self.nC
        
        return [
        r, d, d, d, d, d, d, r,
        d, r, d, d, d, d, r, d,
        d, d, r, d, d, r, d, d,
        d, d, d, r, r, d, d, d,
        d, d, d, r, r, d, d, d,
        d, d, r, d, d, r, d, d,
        d, r, d, d, d, d, r, d,
        r, d, d, d, d, d, d, r,
        ]
    
    def _room_Occupied(self):
        r = self.rC
        w = self.wC
        n = self.nC
        
        self.image = [
        r, r, w, w, w, w, r, r,
        r, r, w, r, r, w, r, r,
        r, r, w, r, r, w, r, r,
        r, w, w, w, w, w, w, r,
        r, w, w, n, n, w, w, r,
        r, w, w, n, n, w, w, r,
        r, w, w, n, n, w, w, r,
        r, w, w, w, w, w, w, r,
        ]
        
    def _coor_Single(self, coor=[0,0], color=(255, 105, 180)): #Not in use
        self.image[(coor[0])+(coor[1])*8] = color
    
    def _coor_Multi(self, coorm=[[0,0],[0,1]], color=(255, 105, 180)): #Not in use
        for coor in coorm:
            self.image[(coor[0])+(coor[1])*8] = color
    
    def _object_chooser(self):
        user_data = {
            1: self.kortData[0],
            2: self.kortData[1]
        }
        room_data = {
            1: self.lokaleData[0],
            2: self.lokaleData[1]
        }
    
        self.currentUser = user_data.get(self.User)
        if not self.currentUser:
            print("ERROR USER DOES NOT EXIST")
    
        self.currentRoom = room_data.get(self.Room)
        if not self.currentRoom:
            print("ERROR ROOM DOES NOT EXIST")
    
    def _joystick_Checker(self):
        for event in self.s.stick.get_events():
            if event.action == "pressed":
                if event.direction == "up":
                    self.Room = 1
                    self.s.show_message("R1", scroll_speed=0.02)
                elif event.direction == "left":
                    self.Room = 2
                    self.s.show_message("R2", scroll_speed=0.02)
                elif event.direction == "down":
                    self.User = 1
                    self.s.show_message("P1", scroll_speed=0.02)
                elif event.direction == "right":
                    self.User = 2
                    self.s.show_message("P2", scroll_speed=0.02)
                elif event.direction == "middle":
                    self.checkIn = True
                self._object_Chooser()
                return True
            else:
                return False
    
    def _UDP_Sender(self, message):
        """Sends the given message over UDP to the server."""
        try:
            # Encode the message as bytes and send it to the server's IP and port
            self.clientSocket.sendto(message.encode(), (self.serverIP, self.serverPort))
        except Exception as e:
            # Print an error message if an exception occurs
            print("An error occurred while sending the message:", e)

    def _check_in(self):
        message = '{"lokaleId":"'+str(self.currentRoom[0])+'", "cardId":'+str(self.currentUser[0])+'}$'+str(self.currentUser[0])+''
        self._UDP_Sender(message)
        self._get_Data()
    
    def _check_out(self):
        self.s.show_message("Opt out?", text_colour=self.wC, back_colour=self.nC, scroll_speed=0.02)
        self.s.show_letter("?", text_colour=self.wC, back_colour=self.rC)
        for x in range(150):
            for event in self.s.stick.get_events():
                if event.action == "pressed":
                    if event.direction == "middle":
                        message = '{"lokaleId":"'+str(self.currentRoom[0])+'", "cardId":0}$'+str(self.currentUser[0])+''
                        self._UDP_Sender(message)
                        self.s.show_letter("?", text_colour=self.wC, back_colour=self.gC)
                        self._get_Data()
            time.sleep(0.01)
    
    def _access_denied(self):
        self.s.set_pixels(self._denied())
        for x in range(100):
    
    def _checkIn_Systems(self):
        print()
        print("Before")
        print(self.currentRoom[1])
        if self.currentRoom[1] == None:
            print("Check in")
            self._check_in()
                
        elif self.currentRoom[1] == self.currentUser[0]:
            print("Check out")
            self._check_out
            
        elif self.currentRoom[1] != None:
            print("Denied")
            self._access_denied()
        
    def imageInserter(self):
        
        if self._joystick_Checker() and self.checkIn:
            if self.currentRoom[1] == None:
                self._room_Occupied()
            self.s.set_pixels(self.image)
            self._checkIn_Systems()
            print()
            print("After")
            print(self.currentRoom[1])
        
        if self.currentRoom[1] == None:
            self._room_Free()
        elif self.currentRoom[1] != "None":
            self._room_Occupied()
            
        self.checkIn = False
        return self.image
            
CI = CheckIn()

while(True):
    CI.s.set_pixels(CI.imageInserter())
    time.sleep(0.1)
    
CI.clientSocket.close()


# In[1]:


user_data = {
        1: 1,
        2: 2
    }
type(user_data)


# In[ ]:




