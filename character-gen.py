

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from tkinter import * 
from tkinter import Tk
from tkinter import filedialog
import json
import os
import math
import numpy as np

def get_json(path):
    with open(path, "r") as json_file:
        data = json.load(json_file)
        return data
    
info = get_json("./info.json")
charTemplate = get_json("./character-sheet.json")
    
class mainWindow(QDialog):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        
        self.setFixedSize(600,400)
        mainLayout= QHBoxLayout()
        # mainLayout.setStretch(400,400)
        
        menuWidget = QWidget()
        
        menuLayout = QVBoxLayout()
        menuWidget.setLayout(menuLayout)
        menuLayout.addStretch()
        
        newCharButton = QPushButton("Create New")
        newCharButton.clicked.connect(self.createNew)
        menuLayout.addWidget(newCharButton)
        
        loadCharButton = QPushButton("Load")
        self.charWindow = characterWindow()
        loadCharButton.clicked.connect(self.load)
        menuLayout.addWidget(loadCharButton)
        
        exitButton = QPushButton("Quit")
        exitButton.clicked.connect(self.exitProgram)
        menuLayout.addWidget(exitButton)
        menuLayout.addStretch()
        
        self.backgroundImage = QLabel()
        pixmap = QPixmap("./bin/background_image.jpg")
        self.backgroundImage.setPixmap(pixmap)
        self.setStyleSheet("QDialog{background-image: url(bin/background_image.jpg)}")
        
        mainLayout.addStretch()
        mainLayout.addWidget(menuWidget)
        mainLayout.addStretch()
        self.setLayout(mainLayout)
        self.setWindowTitle("Abril Theia Character Generator")
        
        
    def createNew(self):
        self.nameDialog = enterNameWindow()
    
    def load(self):
        self.charWindow.onOpen()
        # self.charWindow.show()
    
    def exitProgram(self):
        self.close()
        
        
class singleLineEdit(QTextEdit):
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key_Return,Qt.Key_Enter):
            return
        super().keyPressEvent(event)
        
class enterNameWindow(QDialog):
    def __init__(self,parent=None):
        super(enterNameWindow, self).__init__(parent)
        
        self.setWindowTitle("Enter file name")
        nameLayout = QVBoxLayout()
        self.setnametext = QLabel()
        self.setnametext.setText("Enter your character name here \n(This can be changed later)")
        self.setLayout(nameLayout)
        self.nameEntryBox = QLineEdit("")
        nameLayout.addWidget(self.setnametext)
        nameLayout.addWidget(self.nameEntryBox)
        
        okButton = QPushButton("OK")
        okButton.clicked.connect(self.onClickOK)
        nameLayout.addWidget(okButton)
        self.show()
    
    def onClickOK(self):
        name = self.nameEntryBox.text()
        if name != "":
            charTemplate["character"] = name
            jsonName = ".".join([name,"json"])
            fileRoute = "".join(["./characters/",jsonName])
            # ADD: If character exists - ask if wanting to overwrite            
            with open(fileRoute, "w+") as file:
                json.dump(charTemplate,file,indent=4,sort_keys=True)
                print("File created at: ",jsonName)
        else:
            pass
        self.close()
              
class raceBox(QComboBox):
    def __init__(self):
        super(raceBox,self).__init__()
        for race in info["races"]:
            self.addItem(info["races"][race]["raceName"])
        
class heritageBox(QComboBox):
    def __init__(self):
        super(heritageBox,self).__init__()
            
class characterWindow(QDialog):
    def __init__(self, parent=None):
        super(characterWindow, self).__init__(parent)   
        self.file = None
        self.fileName = None
        self.changed_list=[]
        self.imagePath = ""
        self.starting = True
        GridLayout = QGridLayout()
        
        #### TABS
        
        self.tabs = QTabWidget()
        self.chartab = QWidget()
        chartabLayout = QGridLayout()
        
        self.skilltab = QWidget()
        skilltabLayout = QGridLayout()
        
        self.combattab = QWidget()
        combattabLayout = QGridLayout()
        
        self.traitstab = QWidget()
        traitstabLayout = QGridLayout()
        
        self.invtab = QWidget()
        invtabLayout = QGridLayout()
        
        self.tabs.addTab(self.chartab,"Character")
        self.tabs.addTab(self.skilltab, "Skills")
        self.tabs.addTab(self.combattab, "Combat")
        self.tabs.addTab(self.traitstab, "Traits")
        self.tabs.addTab(self.invtab, "Inventory")
        
        #### CHARACTER TAB WIDGETS
        
        nameLayout = QHBoxLayout()
        nameContainer = QWidget()
        nameContainer.setLayout(nameLayout)
        
        self.nameText = QLabel("Name:")
        self.nameBox = singleLineEdit()
        self.nameBox.setFixedHeight(25)
        self.nameBox.setText("Name")
        nameLayout.addWidget(self.nameText)
        nameLayout.addWidget(self.nameBox)
        # nameLayout.addStretch()
        
        attrsContainer = QWidget()
        attrsLayout = QGridLayout()
        attrsContainer.setLayout(attrsLayout)
        
        self.attrsLabels = []
        self.attrsMinLabels = []
        self.attrsMaxLabels = []
        self.attrsManual = []
        self.attrsTraits = []
        self.attrsTotals = []
        self.attrsBonus = []
        
        attrs = ["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"]
        for index,attr in enumerate(attrs):
            self.attrsLabels.append(QLabel(attr))
            attrsLayout.addWidget(self.attrsLabels[index],index+1,0,1,1)
            self.attrsMinLabels.append(QLabel())
            attrsLayout.addWidget(self.attrsMinLabels[index],index+1,1,1,1)
            self.attrsMaxLabels.append(QLabel())
            attrsLayout.addWidget(self.attrsMaxLabels[index],index+1,2,1,1)
            self.attrsManual.append(QSpinBox())
            self.attrsManual[index].setFixedSize(40,25)
            self.attrsManual[index].valueChanged.connect(lambda: self.update_file(show_update=False))
            attrsLayout.addWidget(self.attrsManual[index],index+1,3,1,1)
            self.attrsTraits.append(QLabel("0"))
            attrsLayout.addWidget(self.attrsTraits[index],index+1,4,1,1)
            self.attrsTotals.append(QLabel("0"))
            attrsLayout.addWidget(self.attrsTotals[index],index+1,5,1,1)
            self.attrsBonus.append(QLabel())
            attrsLayout.addWidget(self.attrsBonus[index],index+1,6,1,1)
            # self.attrsOthers.append(QLabel())
            # attrsLayout.addWidget(self.attrsOthers[index],index+1,4,1,1)
            
        attrsLayout.addWidget(QLabel("Stat"),0,0,1,1)
        attrsLayout.addWidget(QLabel("Min"),0,1,1,1)
        attrsLayout.addWidget(QLabel("Max"),0,2,1,1)
        attrsLayout.addWidget(QLabel("Traits"),0,4,1,1)
        attrsLayout.addWidget(QLabel("Total"),0,5,1,1)
        attrsLayout.addWidget(QLabel("Bonus"),0,6,1,1)
            
        self.ptsSpent = QLabel("Points Spent: ")
        self.ptsSpent.setAlignment(Qt.AlignCenter)
        attrsLayout.addWidget(self.ptsSpent,7,0,1,6)
        
        
        raceLayout = QHBoxLayout()
        raceContainer = QWidget()
        raceContainer.setLayout(raceLayout)
        self.raceText = QLabel("Race:")
        self.raceListBox = raceBox()
        self.raceListBox.activated.connect(lambda: self.update_file(show_update=False))
        self.raceInfoButton = QPushButton("Info")
        self.raceInfoButton.setFixedWidth(50)
        self.raceInfoButton.clicked.connect(self.genRaceInfoWindow)
        raceLayout.addWidget(self.raceText)
        raceLayout.addWidget(self.raceListBox)
        raceLayout.addWidget(self.raceInfoButton)
        
        heritageLayout = QHBoxLayout()
        heritageContainer = QWidget()
        heritageContainer.setLayout(heritageLayout)
        self.heritageText = QLabel("Heritage:")
        self.heritageListBox = heritageBox()
        self.heritageListBox.activated.connect(lambda: self.update_file(show_update=False))
        self.heritageInfoButton = QPushButton("Info")
        self.heritageInfoButton.setFixedWidth(50)
        self.heritageInfoButton.clicked.connect(self.genHeritageInfoWindow)
        heritageLayout.addWidget(self.heritageText)
        heritageLayout.addWidget(self.heritageListBox)
        heritageLayout.addWidget(self.heritageInfoButton)
        
        imageLayout = QVBoxLayout()
        imageContainer = QWidget()
        imageContainer.setLayout(imageLayout)
        self.charImage = QLabel()
        imageContainer.setFixedHeight(300)
        imageContainer.setFixedWidth(300)
        self.imageButton = QPushButton("Choose image")
        self.imageButton.clicked.connect(self.setImagePath)
        
        imageLayout.addWidget(self.charImage)
        imageLayout.addWidget(self.imageButton)
        imageLayout.addStretch()
        
        #### RP stats
        
        rpStatsLayout = QGridLayout()
        rpStatsContainer = QWidget()
        rpStatsContainer.setLayout(rpStatsLayout)
        self.ageLabel = QLabel("Age:")
        self.ageBox = QSpinBox()
        # self.ageBox.valueChanged.connect(lambda: self.update_file(show_update=False))
        self.heightLabel = QLabel("Height:")
        self.heightBox = singleLineEdit()
        # self.heightBox.textChanged.connect(lambda: self.update_file(show_update=False))
        self.weightLabel = QLabel("Weight:")
        self.weightBox = singleLineEdit()
        # self.weightBox.textChanged.connect(lambda: self.update_file(show_update=False))
        self.eyeLabel = QLabel("Eye Colour:")
        self.eyeBox = singleLineEdit()
        # self.eyeBox.textChanged.connect(lambda: self.update_file(show_update=False))
        self.skinLabel = QLabel("Skin Colour:")
        self.skinBox = singleLineEdit()
        # self.skinBox.textChanged.connect(lambda: self.update_file(show_update=False))
        self.hairLabel = QLabel("Hair Colour:")
        self.hairBox = singleLineEdit()
        # self.hairBox.textChanged.connect(lambda: self.update_file(show_update=False))
        for box in [self.heightBox,self.weightBox,self.eyeBox,self.skinBox,self.hairBox]:
            box.setFixedWidth(75)
            box.setFixedHeight(25)
        
        rpStatsLayout.addWidget(self.ageLabel,0,0,1,1)
        rpStatsLayout.addWidget(self.ageBox,0,1,1,1)
        rpStatsLayout.addWidget(self.heightLabel,0,2,1,1)
        rpStatsLayout.addWidget(self.heightBox,0,3,1,1)
        rpStatsLayout.addWidget(self.weightLabel,1,0,1,1)
        rpStatsLayout.addWidget(self.weightBox,1,1,1,1)
        rpStatsLayout.addWidget(self.eyeLabel,1,2,1,1)
        rpStatsLayout.addWidget(self.eyeBox,1,3,1,1)
        rpStatsLayout.addWidget(self.skinLabel,2,0,1,1)
        rpStatsLayout.addWidget(self.skinBox,2,1,1,1)
        rpStatsLayout.addWidget(self.hairLabel,2,2,1,1)
        rpStatsLayout.addWidget(self.hairBox,2,3,1,1)
        
        rpLayout = QGridLayout()
        rpContainer = QWidget()
        rpContainer.setLayout(rpLayout)
        self.backgroundLabel = QLabel("Background:")
        self.backgroundBox = QTextEdit()
        rpLayout.addWidget(self.backgroundLabel,0,0,1,1)
        rpLayout.addWidget(self.backgroundBox,1,0,1,1)
        
        notesLayout = QVBoxLayout()
        notesContainer = QWidget()
        notesContainer.setLayout(notesLayout)
        self.notesLabel = QLabel("Notes:")
        self.notesBox = QTextEdit()
        notesLayout.addWidget(self.notesLabel)
        notesLayout.addWidget(self.notesBox)
        
        
        #### SKILLS TAB WIDGETS
        
        self.skillsLayout = QGridLayout()
        skillsWidget = QWidget()
        skillsWidget.setLayout(self.skillsLayout)
        
        headers = ["Skill","Ability Modifier","Ability Bonus", "Proficiency", "Other modifiers","Temp","Total Skill Bonus","Quick Roll"]
        for index in range(0,len(headers)):
            headerWidget = QLabel(headers[index])
            headerWidget.setAlignment(Qt.AlignHCenter)
            self.skillsLayout.addWidget(headerWidget,0,index,1,1)
        
        self.skillsNameWidgets = []
        self.skillsStatsWidgets = []
        self.skillsModifsWidgets = []
        self.skillsProfsWidgets = []
        self.skillsManualWidgets = []
        self.skillsTempWidgets = []
        self.skillsTotalWidgets = []
        self.skillsRollWidgets = []
        for j,i in enumerate(info["skills"]):
            self.skillsNameWidgets.append(QLabel(info["skills"][i]["name"]))
            self.skillsLayout.addWidget(self.skillsNameWidgets[j],j+1,0,1,1)
            self.skillsStatsWidgets.append(QLabel(parseStat(info["skills"][i]["stat"])))
            self.skillsLayout.addWidget(self.skillsStatsWidgets[j],j+1,1,1,1)
            self.skillsModifsWidgets.append(QLabel("0"))
            self.skillsModifsWidgets[j].setAlignment(Qt.AlignHCenter)
            self.skillsLayout.addWidget(self.skillsModifsWidgets[j],j+1,2,1,1)
            profCheckBox = QCheckBox()
            profCheckBox.setTristate(True)
            self.skillsProfsWidgets.append(profCheckBox)
            self.skillsLayout.addWidget(self.skillsProfsWidgets[j],j+1,3,1,1)
            self.skillsManualWidgets.append(QSpinBox())
            self.skillsManualWidgets[j].setRange(-10,10)
            self.skillsManualWidgets[j].setFixedWidth(40)
            self.skillsManualWidgets[j].setAlignment(Qt.AlignCenter)
            self.skillsLayout.addWidget(self.skillsManualWidgets[j],j+1,4,1,1)
            self.skillsTempWidgets.append(QSpinBox())
            self.skillsTempWidgets[j].setRange(-10,10)
            self.skillsTempWidgets[j].setFixedWidth(40)
            self.skillsTempWidgets[j].setAlignment(Qt.AlignCenter)
            self.skillsLayout.addWidget(self.skillsTempWidgets[j],j+1,5,1,1)
            self.skillsTotalWidgets.append(QLabel())
            self.skillsTotalWidgets[j].setAlignment(Qt.AlignCenter)
            self.skillsTotalWidgets[j].setStyleSheet("font-weight: bold")
            self.skillsLayout.addWidget(self.skillsTotalWidgets[j],j+1,6,1,1)
            self.skillsRollWidgets.append(rollWidget(self,file=self.file,skill=i,index=j))
            self.skillsLayout.addWidget(self.skillsRollWidgets[j],j+1,7,1,1)
            
        traitsMainLayout = QHBoxLayout()
        self.traitsLeftLayoutContainer = QWidget()
        self.traitsRightLayoutContainer = QWidget()
        self.traitsLeftLayout = QVBoxLayout()
        self.traitsRightLayout = QVBoxLayout()
        self.traitsLeftLayoutContainer.setLayout(self.traitsLeftLayout)
        self.traitsRightLayoutContainer.setLayout(self.traitsRightLayout)
        self.traitsOwnedTabs = QTabWidget()
        self.traitsOwnedMartialTab = QScrollArea()
        self.traitsOwnedLeymancyTab = QScrollArea()
        self.traitsOwnedProfessionTab = QScrollArea()
        self.traitsOwnedSubtletyTab = QScrollArea()
        
        self.traitsOwnedTabs.addTab(self.traitsOwnedLeymancyTab,"Leymancy (0)")
        self.traitsOwnedTabs.addTab(self.traitsOwnedMartialTab,"Martial (0)")
        self.traitsOwnedTabs.addTab(self.traitsOwnedProfessionTab,"Profession (0)")
        self.traitsOwnedTabs.addTab(self.traitsOwnedSubtletyTab,"Subtlety (0)")
        self.traitsLeftLayout.addWidget(self.traitsOwnedTabs)
        
        self.traitsInfoTabs = QTabWidget()
        self.traitsInfoMartialTab = QScrollArea()
        self.traitsInfoMartialTab.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        self.traitsInfoLeymancyTab = QScrollArea()
        self.traitsInfoProfessionTab = QScrollArea()
        self.traitsInfoSubtletyTab = QScrollArea()
        
        self.traitsInfoMartialTabLayout = QVBoxLayout()
        self.traitsInfoLeymancyTabLayout = QVBoxLayout()
        self.traitsInfoProfessionTabLayout = QVBoxLayout()
        self.traitsInfoSubtletyTabLayout = QVBoxLayout()
        
        self.martialTabContainer = QWidget()
        self.leymancyTabContainer = QWidget()
        self.professionTabContainer = QWidget()
        self.subtletyTabContainer = QWidget()
        
        self.martialTabContainer.setLayout(self.traitsInfoMartialTabLayout)
        self.leymancyTabContainer.setLayout(self.traitsInfoLeymancyTabLayout)
        self.professionTabContainer.setLayout(self.traitsInfoProfessionTabLayout)
        self.subtletyTabContainer.setLayout(self.traitsInfoSubtletyTabLayout)
        
        
        self.traitsInfoMartialTab.setWidget(self.martialTabContainer)
        self.traitsInfoLeymancyTab.setWidget(self.leymancyTabContainer)
        self.traitsInfoProfessionTab.setWidget(self.professionTabContainer)
        self.traitsInfoSubtletyTab.setWidget(self.subtletyTabContainer)
        
        
        
        
        self.traitsInfoTabs.addTab(self.traitsInfoLeymancyTab,"Leymancy")
        self.traitsInfoTabs.addTab(self.traitsInfoMartialTab,"Martial")
        self.traitsInfoTabs.addTab(self.traitsInfoProfessionTab,"Profession")
        self.traitsInfoTabs.addTab(self.traitsInfoSubtletyTab,"Subtlety")
        self.traitsRightLayout.addWidget(self.traitsInfoTabs)
        
        self.traitsLeftLowerContainer = QWidget()
        self.traitsLeftLowerLayout = QVBoxLayout()
        self.traitsLeftLowerContainer.setLayout(self.traitsLeftLowerLayout)
        self.traitsLeftDelButton = QPushButton("Remove Trait")
        self.traitsLeftLowerLayout.addWidget(self.traitsLeftDelButton)
        self.traitsLeftLowerLabel = QLabel(" ")
        self.traitsLeftLowerLayout.addWidget(self.traitsLeftLowerLabel)
        
        self.traitsRightLowerContainer = QWidget()
        self.traitsRightLowerLayout = QVBoxLayout()
        self.traitsRightLowerContainer.setLayout(self.traitsRightLowerLayout)
        self.traitsRightAddButton = QPushButton("Add Trait")
        self.traitsRightLowerLayout.addWidget(self.traitsRightAddButton)
        self.traitsRightLowerLabel = QLabel(" ")
        self.traitsRightLowerLayout.addWidget(self.traitsRightLowerLabel)
        
        self.traitsRightLayout.addWidget(self.traitsRightLowerContainer)
        self.traitsLeftLayout.addWidget(self.traitsLeftLowerContainer)
        
        traitsMainLayout.addWidget(self.traitsLeftLayoutContainer)
        traitsMainLayout.addWidget(self.traitsRightLayoutContainer)
                
        skilltabLayout.addWidget(skillsWidget,0,0,1,1)
        
        #### COMBAT TAB WIDGETS
        
        
        #### TRAITS TAB WIDGETS
        
        updateButton = QPushButton()
        updateButton.setText("Update File")
        updateButton.setFixedWidth(100)
        updateButton.clicked.connect(lambda: self.update_file(show_update=True))
        
        ####
        
        chartabLayout.addWidget(nameContainer,0,0,1,1)
        chartabLayout.addWidget(attrsContainer,1,0,1,1)
        chartabLayout.addWidget(raceContainer,2,0,1,1)
        chartabLayout.addWidget(heritageContainer,3,0,1,1)
        chartabLayout.addWidget(imageContainer,0,1,7,1)
        chartabLayout.addWidget(rpStatsContainer,4,0,1,1)
        chartabLayout.addWidget(rpContainer,5,0,4,1)
        chartabLayout.addWidget(notesContainer,7,1,1,1)
        GridLayout.addWidget(self.tabs)
        GridLayout.addWidget(updateButton,1,0,1,3)
        self.setLayout(GridLayout)
        self.chartab.setLayout(chartabLayout)
        self.skilltab.setLayout(skilltabLayout)
        self.traitstab.setLayout(traitsMainLayout)
        
        
    
    def onOpen(self):
        self.fileName = self.browseFile(ftypes = [("json Files","*.json")],directory="./characters/")
        if len(self.fileName) > 0:
            print("File",self.fileName,"successfully loaded.")
            self.changed_list = []
            self.starting = True
            self.update_gui()
            self.update_file(show_update=False)
            self.update_gui()
            self.show()
        else:
            print("File not loaded.")
        
    def setImagePath(self):
        imagePath = self.browseFile(ftypes = [("image Files","*.jpg *.png *.bmp")],directory="./images/")
        if imagePath: 
            self.imagePath = imagePath
            self.update_file(show_update=False)
        else:
            pass
    
    def browseFile(self, ftypes,directory):
        currDir = os.getcwd()
        return filedialog.askopenfilename(filetypes = ftypes,initialdir = directory)
    
    
    def genRaceInfoWindow(self):
        self.raceInfoWindow = showRaceInfoWindow(file=self.file)
        self.raceInfoWindow.show()
        
    def genHeritageInfoWindow(self):
        self.heritageInfoWindow = showHeritageInfoWindow(file=self.file)
        self.heritageInfoWindow.show()
    
    def update_gui(self):
        if self.fileName == None:
            print("No file loaded")
            pass
        else:
            if self.file == None:
                self.file = get_json(self.fileName)  
                
            self.setWindowTitle(self.file["character"])#
                
            ### Widgets
                
            self.nameBox.setPlainText(self.file["character"])
            
            raceIndex = self.raceListBox.findText(self.file["race"])
            self.raceListBox.setCurrentIndex(raceIndex)
            heritage = self.file["heritage"]
            self.heritageList = []
            for i in info["races"][self.file["race"]]["heritages"]:
                self.heritageList.append(i)
            if self.heritageListBox.currentText() in self.heritageList:
                pass
            else:
                self.heritageListBox.clear()
                for j in self.heritageList:
                    self.heritageListBox.addItem(j)
            heritageIndex = self.heritageListBox.findText(self.file["heritage"])
            self.heritageListBox.setCurrentIndex(heritageIndex)
                
            age = int(self.file["rp_attributes"]["age"])
            self.ageBox.setValue(age)
            
            pixmap = QPixmap(self.file["rp_attributes"]["image"])
            self.charImage.setPixmap(pixmap)
            if self.imagePath == "":
                self.imagePath = self.file["rp_attributes"]["image"]
            
            height = self.file["rp_attributes"]["height"]
            self.heightBox.setText(height)
            weight = self.file["rp_attributes"]["weight"]
            self.weightBox.setText(weight)
            eyes = self.file["rp_attributes"]["eyes"]
            self.eyeBox.setText(eyes)
            skin = self.file["rp_attributes"]["skin"]
            self.skinBox.setText(skin)
            hair = self.file["rp_attributes"]["hair"]
            self.hairBox.setText(hair)
            
            for j in range(0,len(self.skillsNameWidgets)):
                # Name widgets
                skill = self.skillsNameWidgets[j].text()
                if self.starting:
                    if info["skills"][skill]["stat"] == "STAT:ANY":
                        # Add a selection of stat to add
                        self.skillsLayout.removeWidget(self.skillsStatsWidgets[j])
                        self.skillsStatsWidgets[j].setParent(None)
                        self.skillsStatsWidgets[j] = statSelectBox(stats = "Any")
                        self.skillsLayout.addWidget(self.skillsStatsWidgets[j],j+1,1,1,1)
                    elif info["skills"][skill]["stat"] == "STAT:PHYSICAL":
                        self.skillsLayout.removeWidget(self.skillsStatsWidgets[j])
                        self.skillsStatsWidgets[j].setParent(None)
                        self.skillsStatsWidgets[j] = statSelectBox(stats = "Any Physical")
                        self.skillsLayout.addWidget(self.skillsStatsWidgets[j],j+1,1,1,1)
                    elif info["skills"][skill]["stat"] == "STAT:MENTAL":
                        self.skillsLayout.removeWidget(self.skillsStatsWidgets[j])
                        self.skillsStatsWidgets[j].setParent(None)
                        self.skillsStatsWidgets[j] = statSelectBox(stats = "Any Mental")
                        self.skillsLayout.addWidget(self.skillsStatsWidgets[j],j+1,1,1,1)
                
                try:
                    self.skillsStatsWidgets[j].setCurrentIndex(self.skillsStatsWidgets[j].getIndex(self.file["skills"][skill]["stat"]))
                except:
                    self.skillsStatsWidgets[j].setText(parseStat(self.file["skills"][skill]["stat"]))
                    
                statName = self.skillsStatsWidgets[j].text()
                for stat,statDict in info["modifiers"].items():
                    if statDict["name"] == statName:
                        statModif = getMainStatModif(self.file["stats"][stat])
                self.skillsModifsWidgets[j].setText(str(statModif))
                
                proficiency = int(self.file["skills"][skill]["proficiency"])
                if self.starting:
                    self.skillsProfsWidgets[j].setCheckState(proficiency)
                    self.skillsProfsWidgets[j].stateChanged.connect(lambda: self.update_file(show_update=False))
                self.skillsProfsWidgets[j].setText(parseProficiency(proficiency))
                proficiencyModifier = int(self.file["stats"]["STAT:PROF"])
                proficiencyBonus = proficiency * proficiencyModifier
                
                manualVal = int(self.file["skills"][skill]["manual"])
                if self.starting:
                    self.skillsManualWidgets[j].setValue(manualVal)
                    self.skillsManualWidgets[j].valueChanged.connect(lambda: self.update_file(show_update=False))
                
                tempVal = self.skillsTempWidgets[j].value()
                if self.starting:
                    self.skillsTempWidgets[j].valueChanged.connect(lambda: self.update_file(show_update=False))
                
                total = proficiencyBonus + manualVal + tempVal + int(statModif)
                self.skillsTotalWidgets[j].setText(str(total))
                
                
            modifs = []
            for category in self.file["traits"]:
                for trait in self.file["traits"][category]:
                    if len(info["traits"][category][trait]["modifiers"]) > 0:    
                        modifs.append(info["traits"][category][trait]["modifiers"])
            for ability in info["races"][self.file["race"]]["abilities"]:
                if len(info["races"][self.file["race"]]["abilities"][ability]) > 0:
                    modifs.append(info["races"][self.file["race"]]["abilities"][ability]["modifiers"])
            try:
                if len(info["races"][self.file["race"]]["heritages"][self.file["heritage"]]["modifiers"]) > 0:
                    modifs.append(info["races"][self.file["race"]]["heritages"][self.file["heritage"]]["modifiers"])
            except:
                pass
            modifsDict = genModifsDict(modifs)
            # If there are any other things that give modifiers, add here!
            
                
            manualStatsTotals = 0
            for j in range(0,len(self.attrsLabels)):
                attr = self.attrsLabels[j].text()
                attrString = deParseStat(attr)
                race = self.file["race"]
                minVal = info["races"][race]["startingStats"][j]
                maxVal = info["races"][race]["maxStats"][j]
                self.attrsMinLabels[j].setText(str(minVal))
                self.attrsMaxLabels[j].setText(str(maxVal))
                try:
                    traits_val = modifsDict[attrString]
                except:
                    traits_val = 0
                self.attrsTraits[j].setText(str(traits_val))
                if self.starting:
                    self.attrsTraits[j].setAlignment(Qt.AlignCenter)
                    
                    total = self.file["stats"][attrString]
                    manualVal = total - minVal - traits_val
                    self.attrsTotals[j].setText(str(total))
                    self.attrsTotals[j].setAlignment(Qt.AlignCenter)
                    self.attrsManual[j].setValue(manualVal)
                    manualStatsTotals += manualVal
                    
                    
                    
                else:
                    manual = int(self.attrsManual[j].value())
                    manualStatsTotals += manual
                    total = minVal + manual + traits_val
                    
                    self.attrsTotals[j].setText(str(total))
                    self.attrsTotals[j].setAlignment(Qt.AlignCenter)
                
                if total > maxVal:
                    self.attrsTotals[j].setStyleSheet("QLabel {color:red}")
                else:
                    self.attrsTotals[j].setStyleSheet("QLabel {color:white}")
                self.attrsBonus[j].setText("(%+d" %getMainStatModif(int(self.attrsTotals[j].text()))+")")
                
            self.ptsSpent.setText("Points Spent: %i" %manualStatsTotals)
            
            # populate traits list
            
            # if starting: populate traits explorer
            
            if self.starting:
                self.traitsInfoWidgets = []
                for category,layout in [["leymancy",self.traitsInfoLeymancyTabLayout],["martial",self.traitsInfoMartialTabLayout,],["profession",self.traitsInfoProfessionTabLayout],["subtlety",self.traitsInfoSubtletyTabLayout]]:
                    traits = info["traits"][category]
                    for trait in traits.keys():
                        traitWidget = traitContainer(self,category=category,trait=trait)
                        # traitWidget.clicked.connect(self.update_gui())
                        self.traitsInfoWidgets.append(traitWidget)
                        layout.addWidget(self.traitsInfoWidgets[-1])
                        
                self.martialTabContainer.adjustSize()
                self.leymancyTabContainer.adjustSize()
                self.professionTabContainer.adjustSize()
                self.subtletyTabContainer.adjustSize()
            
            for traitWidget in self.traitsInfoWidgets:
                traitWidget.update()
            
            self.starting = False
            
            
    
    def update_file(self,show_update=False):
        if self.fileName == None:
            print("No file loaded")
            pass
        else:
            if self.file == None:
                self.file = get_json(self.fileName)
                
            ### Widgets
                
            if self.file["character"] != self.nameBox.toPlainText():
                self.file["character"] = self.nameBox.toPlainText()
                self.changed_list.append("".join(["Character name -> ", self.nameBox.toPlainText()]))
            
            
            if self.file["race"] != self.raceListBox.currentText():
                self.file["race"] = self.raceListBox.currentText()
                self.changed_list.append("".join(["Race -> ", self.raceListBox.currentText()]))
                self.update_gui()
            
            if self.file["heritage"] != self.heritageListBox.currentText():
                self.file["heritage"] = self.heritageListBox.currentText()
                self.changed_list.append("".join(["Heritage -> ", self.heritageListBox.currentText()]))
                
            if self.file["rp_attributes"]["age"] != self.ageBox.value():
                self.file["rp_attributes"]["age"] = self.ageBox.value()
                self.changed_list.append("".join(["Age -> ", str(self.ageBox.value())]))
                
            if self.file["rp_attributes"]["height"] != self.heightBox.toPlainText():
                self.file["rp_attributes"]["height"] = self.heightBox.toPlainText()
                self.changed_list.append("".join(["Height -> ", str(self.heightBox.toPlainText())]))
                
            if self.file["rp_attributes"]["weight"] != self.weightBox.toPlainText():
                self.file["rp_attributes"]["weight"] = self.weightBox.toPlainText()
                self.changed_list.append("".join(["Weight -> ", str(self.weightBox.toPlainText())]))
                
            if self.file["rp_attributes"]["eyes"] != self.eyeBox.toPlainText():
                self.file["rp_attributes"]["eyes"] = self.eyeBox.toPlainText()
                self.changed_list.append("".join(["Eye colour -> ", str(self.eyeBox.toPlainText())]))
                
            if self.file["rp_attributes"]["skin"] != self.skinBox.toPlainText():
                self.file["rp_attributes"]["skin"] = self.skinBox.toPlainText()
                self.changed_list.append("".join(["Skin colour -> ", str(self.skinBox.toPlainText())]))
                
            if self.file["rp_attributes"]["hair"] != self.hairBox.toPlainText():
                self.file["rp_attributes"]["hair"] = self.hairBox.toPlainText()
                self.changed_list.append("".join(["Hair colour -> ", str(self.hairBox.toPlainText())]))
                
            if self.file["rp_attributes"]["background"] != self.backgroundBox.toPlainText():
                self.file["rp_attributes"]["background"] = self.backgroundBox.toPlainText()
                self.changed_list.append("".join(["Background modified"]))
                
            if self.file["rp_attributes"]["notes"] != self.notesBox.toPlainText():
                self.file["rp_attributes"]["notes"] = self.notesBox.toPlainText()
                self.changed_list.append("".join(["Notes modified"]))
                
            if self.file["rp_attributes"]["image"] != self.imagePath:
                self.file["rp_attributes"]["image"] = self.imagePath
                self.changed_list.append("".join(["Image path -> ",str(self.imagePath)]))
                
            for index,skillWidget in enumerate(self.skillsNameWidgets):
                skill = skillWidget.text()
                if self.skillsProfsWidgets[index].checkState() != self.file["skills"][skill]["proficiency"]:
                    self.file["skills"][skill]["proficiency"] = self.skillsProfsWidgets[index].checkState()
                    self.changed_list.append("".join([skill," proficiency -> ",parseProficiency(self.file["skills"][skill]["proficiency"])]))
            # Update proficiencies
                if self.skillsStatsWidgets[index].text() != parseStat(self.file["skills"][skill]["stat"]):
                    try: 
                        self.file["skills"][skill]["stat"] = self.skillsStatsWidgets[index].text()
                        self.changed_list.append("".join([skill," stat -> ",self.file["skills"][skill]["stat"]]))
                    except:
                        pass
                if self.skillsManualWidgets[index].value() != int(self.file["skills"][skill]["manual"]):
                    self.file["skills"][skill]["manual"] = self.skillsManualWidgets[index].value()
                    
                if int(self.skillsTotalWidgets[index].text()) != self.file["skills"][skill]["value"]:
                    self.file["skills"][skill]["value"] = int(self.skillsTotalWidgets[index].text())
                    
            for index, totalWidget in enumerate(self.attrsTotals):
                if totalWidget.text() == "":
                    pass
                else:
                    total = int(totalWidget.text())
                    stat = self.attrsLabels[index].text()
                    stat_string = deParseStat(stat)
                    if total != self.file["stats"][stat_string]:
                        self.file["stats"][stat_string] = total
                
        with open(self.fileName,"w") as f:    
            json.dump(self.file,f,indent=4,sort_keys=True)
                    
        self.update_gui()
        if show_update:
            msg = QMessageBox()
            msg.setWindowTitle("Updater")
            msg.setText("File Updated!")
            msg.setDetailedText("\n".join(self.changed_list))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self.changed_list = []
        
      
class rollWidget(QLabel):
    clicked = pyqtSignal()
    def __init__(self,parent,file=None,skill="Athletics",index=0):
        super(rollWidget,self).__init__(parent)
        # self.file = file
        self.skill = skill
        self.index = index
        self.setFixedSize(25,25)
        dieImgFile = "./bin/d20.png"
        self.pixmap = QPixmap(dieImgFile)
        self.setPixmap(self.pixmap)
        self.clicked.connect(self.roll)
        
    def mouseReleaseEvent(self,QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()
        
    def roll(self):
        self.file = self.parent().parent().parent().parent().parent().file
        bonus = self.parent().parent().parent().parent().parent().skillsTotalWidgets[self.index].text()
        bonus = int(bonus)
        roll = math.ceil(np.random.rand()*20)
        total = int(bonus + roll)
        msg = QMessageBox()
        msg.setText("".join([self.skill," roll: \n",str(total), " (",str(roll) + "%+d" %bonus,")"]))
        msg.setWindowTitle(self.skill)
        msg.exec()
      
class showRaceInfoWindow(QDialog):
    def __init__(self,parent=None,file=None):
        super(showRaceInfoWindow, self).__init__(parent) 
        self.file = file
        self.setFixedWidth(600)
        
        mainLayout = QVBoxLayout()
        ### GET INFO
        race = self.file["race"]
        self.setWindowTitle(race)
        raceDescription = info["races"][race]["description"]
        baseHP = info["races"][race]["baseHP"]
        baseSpeed = info["races"][race]["baseSpeed"]
        size = info["races"][race]["size"]
        abilitiesNames = []
        abilitiesDescriptions = []
        abilitiesModifiers = []
        for ability in info["races"][race]["abilities"]:
            abilitiesNames.append(info["races"][race]["abilities"][ability]["name"])
            abilitiesDescriptions.append(info["races"][race]["abilities"][ability]["description"])
            abilitiesModifiers.append(info["races"][race]["abilities"][ability]["modifiers"])
        startingStats = []
        for ststat in info["races"][race]["startingStats"]:
            startingStats.append(ststat)
        maxStats = []
        for maxstat in info["races"][race]["maxStats"]:
            maxStats.append(maxstat)
        ### IMAGE
        imageLayout = QVBoxLayout()
        imageContainer = QWidget()
        imageContainer.setLayout(imageLayout)
        raceImage = QLabel()
        imageContainer.setFixedHeight(300)
        imageContainer.setFixedWidth(300)
        pixmap = QPixmap(info["races"][race]["image"])
        raceImage.setPixmap(pixmap)
            
        imageLayout.addWidget(raceImage)
        # imageLayout.addStretch()
        
        upperLayout = QHBoxLayout()
        upperContainer = QWidget()
        upperContainer.setLayout(upperLayout)
        
        ### DESCRIPTION
        RILayout = QGridLayout()
        RIContainer = QWidget()
        RIContainer.setLayout(RILayout)
        titleLabel1 = QLabel("Race: ")
        titleLabel2 = QLabel(race)
        descLabel1 = QLabel("Description: ")
        descLabel1.setAlignment(Qt.AlignTop)
        descLabel2=QLabel(raceDescription)
        descLabel2.setWordWrap(True)
        hpLabel1 = QLabel("Base HP: ")
        hpLabel2 = QLabel(str(baseHP))
        spdLabel1 = QLabel("Base Speed: ")
        spdLabel2 = QLabel(" ".join([str(baseSpeed),"ft"]))
        sizeLabel1 = QLabel("Size: ")
        sizeLabel2 = QLabel(str(size))
        
        
        upperLayout.addWidget(RIContainer)
        upperLayout.addWidget(imageContainer)
        
        RILayout.addWidget(titleLabel1,0,0,1,1)
        RILayout.addWidget(titleLabel2,0,1,1,1)
        RILayout.addWidget(descLabel1,1,0,1,1)
        RILayout.addWidget(descLabel2,1,1,1,1)
        RILayout.addWidget(hpLabel1,2,0,1,1)
        RILayout.addWidget(hpLabel2,2,1,1,1)
        RILayout.addWidget(spdLabel1,3,0,1,1)
        RILayout.addWidget(spdLabel2,3,1,1,1)
        RILayout.addWidget(sizeLabel1,4,0,1,1)
        RILayout.addWidget(sizeLabel2,4,1,1,1)
        ### ABILITIES
        abLayout = QGridLayout()
        abContainer = QWidget()
        abContainer.setLayout(abLayout)
        
        abTitle = QLabel("Abilities:")
        abDesc = QLabel("Description:")
        abMod = QLabel("Modifiers:")
        abilityNameWidgets = []
        abilityDescriptionWidgets = []
        abilityModifierWidgets = []
        if len(abilitiesNames) == len(abilitiesDescriptions) and len(abilitiesNames) == len(abilitiesModifiers):
            for i in range(0,len(abilitiesNames)):
                abilityNameWidgets.append(QLabel(abilitiesNames[i]))
                abilityNameWidgets[i].setAlignment(Qt.AlignTop)
                abilityDescriptionWidgets.append(QLabel(abilitiesDescriptions[i]))
                abilityDescriptionWidgets[i].setWordWrap(True)
                abilityModifierWidgets.append(QLabel(parseModifiers(abilitiesModifiers[i])))
                abLayout.addWidget(abilityNameWidgets[i],i+1,0,1,1)
                abLayout.addWidget(abilityDescriptionWidgets[i],i+1,1,1,1)
                abLayout.addWidget(abilityModifierWidgets[i],i+1,2,1,1)
                      
        abLayout.addWidget(abTitle,0,0,1,1)
        abLayout.addWidget(abDesc,0,1,1,1)
        abLayout.addWidget(abMod,0,2,1,1)
        ### STATS
        statsWrapperLayout = QHBoxLayout()
        statsWrapperContainer = QWidget()
        statsWrapperContainer.setLayout(statsWrapperLayout)
        
        statsLayout = QGridLayout()
        statsContainer = QWidget()
        statsContainer.setLayout(statsLayout)
        
        statsSTR = QLabel("Strength")
        statsDEX = QLabel("Dexterity")
        statsCON = QLabel("Constitution")
        statsINT = QLabel("Intelligence")
        statsWIS = QLabel("Wisdom")
        statsCHA = QLabel("Charisma")
        
        baseSTR = QLabel(str(startingStats[0]))
        baseDEX = QLabel(str(startingStats[1]))
        baseCON = QLabel(str(startingStats[2]))
        baseINT = QLabel(str(startingStats[3]))
        baseWIS = QLabel(str(startingStats[4]))
        baseCHA = QLabel(str(startingStats[5]))
        
        maxSTR = QLabel(str(maxStats[0]))
        maxDEX = QLabel(str(maxStats[1]))
        maxCON = QLabel(str(maxStats[2]))
        maxINT = QLabel(str(maxStats[3]))
        maxWIS = QLabel(str(maxStats[4]))
        maxCHA = QLabel(str(maxStats[5]))
        
        baseTitle = QLabel("Min")
        maxTitle = QLabel("Max")
        
        statsLayout.addWidget(statsSTR,1,0,1,1)
        statsLayout.addWidget(statsDEX,2,0,1,1)
        statsLayout.addWidget(statsCON,3,0,1,1)
        statsLayout.addWidget(statsINT,4,0,1,1)
        statsLayout.addWidget(statsWIS,5,0,1,1)
        statsLayout.addWidget(statsCHA,6,0,1,1)
        
        statsLayout.addWidget(baseSTR,1,1,1,1)
        statsLayout.addWidget(baseDEX,2,1,1,1)
        statsLayout.addWidget(baseCON,3,1,1,1)
        statsLayout.addWidget(baseINT,4,1,1,1)
        statsLayout.addWidget(baseWIS,5,1,1,1)
        statsLayout.addWidget(baseCHA,6,1,1,1)
        
        statsLayout.addWidget(maxSTR,1,2,1,1)
        statsLayout.addWidget(maxDEX,2,2,1,1)
        statsLayout.addWidget(maxCON,3,2,1,1)
        statsLayout.addWidget(maxINT,4,2,1,1)
        statsLayout.addWidget(maxWIS,5,2,1,1)
        statsLayout.addWidget(maxCHA,6,2,1,1)
        
        statsLayout.addWidget(baseTitle,0,1,1,1)
        statsLayout.addWidget(maxTitle,0,2,1,1)
        statsLayout.setHorizontalSpacing(20)
        statsLayout.setVerticalSpacing(0)
        
        statsWrapperLayout.addWidget(statsContainer)
        statsWrapperLayout.addStretch()
        ### CLOSE BUTTON
        closeButtonLayout = QHBoxLayout()
        closeButtonContainer = QWidget()
        closeButtonContainer.setLayout(closeButtonLayout)
        
        closeButton = QPushButton("Exit")
        closeButton.setFixedSize(100,25)
        closeButton.clicked.connect(self.close)
        closeButtonLayout.addStretch()
        closeButtonLayout.addWidget(closeButton)
        ### MAIN LAYOUT
        mainLayout.addWidget(upperContainer)
        mainLayout.addWidget(abContainer)
        mainLayout.addWidget(statsWrapperContainer)
        mainLayout.addWidget(closeButtonContainer)
        self.setLayout(mainLayout)


class showHeritageInfoWindow(QDialog):
    def __init__(self,parent=None,file=None):
        super(showHeritageInfoWindow, self).__init__(parent) 
        self.setFixedWidth(600)
        self.file = file
        race = self.file["race"]
        heritage = self.file["heritage"]
        self.setWindowTitle(heritage)
        
        maxLayout = QHBoxLayout()
        
        main2Widget = QWidget()
        main2Layout = QVBoxLayout()
        main2Widget.setLayout(main2Layout)
        
        mainWidget = QWidget()
        mainLayout = QGridLayout()
        mainWidget.setLayout(mainLayout)
        main2Layout.addWidget(mainWidget)
        main2Layout.addStretch()
        
        rightWidget=QWidget()
        rightLayout = QVBoxLayout()
        rightWidget.setLayout(rightLayout)
        
        nameLabel = QLabel("Name:")
        nameLabel.setAlignment(Qt.AlignTop)
        descLabel = QLabel("Description:")
        descLabel.setAlignment(Qt.AlignTop)
        modifiersLabel = QLabel("Modifiers:")
        modifiersLabel.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(nameLabel,0,0,1,1)
        mainLayout.addWidget(descLabel,1,0,1,1)
        mainLayout.addWidget(modifiersLabel,2,0,1,1)
        
        nameVal = info["races"][race]["heritages"][heritage]["name"]
        descVal = info["races"][race]["heritages"][heritage]["description"]
        modifiersVal = info["races"][race]["heritages"][heritage]["modifiers"]
        nameValLabel = QLabel(nameVal)
        nameValLabel.setAlignment(Qt.AlignLeft)
        descValLabel = QLabel(descVal)
        descValLabel.setAlignment(Qt.AlignLeft)
        descValLabel.setWordWrap(True)
        modifiersValLabel = QLabel(parseModifiers(modifiersVal))
        modifiersValLabel.setAlignment(Qt.AlignLeft)
        
        mainLayout.addWidget(nameValLabel,0,1,1,1)
        mainLayout.addWidget(descValLabel,1,1,1,1)
        mainLayout.addWidget(modifiersValLabel,2,1,1,1)
        
        imageLayout = QVBoxLayout()
        imageContainer = QWidget()
        imageContainer.setLayout(imageLayout)
        raceImage = QLabel()
        imageContainer.setFixedHeight(300)
        imageContainer.setFixedWidth(300)
        pixmap = QPixmap(info["races"][race]["heritages"][heritage]["image"])
        raceImage.setPixmap(pixmap)
            
        imageLayout.addWidget(raceImage)
        
        closeButtonLayout = QHBoxLayout()
        closeButtonContainer = QWidget()
        closeButtonContainer.setLayout(closeButtonLayout)
        
        closeButton = QPushButton("Exit")
        closeButton.setFixedSize(100,25)
        closeButton.clicked.connect(self.close)
        closeButtonLayout.addStretch()
        closeButtonLayout.addWidget(closeButton)
        
        rightLayout.addWidget(imageContainer)
        rightLayout.addWidget(closeButtonContainer)
        
        maxLayout.addWidget(main2Widget)
        maxLayout.addWidget(rightWidget)
        
        self.setLayout(maxLayout)
        
        
        
class statSelectBox(QComboBox):
    def __init__(self,parent=None,stats=None):
        super(statSelectBox,self).__init__(parent)
        self.activated.connect(lambda: self.parent().parent().parent().parent().parent().update_file(show_update=False))
        if stats == "Any" or stats == "Any Physical":
            self.addItem("Strength")
            self.addItem("Dexterity")
            self.addItem("Constitution")
        if stats == "Any" or stats == "Any Mental":
            self.addItem("Intelligence")
            self.addItem("Wisdom")
            self.addItem("Charisma")
            
    def text(self):
        return str(self.currentText())
    
    def getIndex(self,text):
        i = 0
        while i < 6:
            if self.itemText(i) == text:
                return i
            else:
                i += 1
        
class traitContainer(QFrame):
    def __init__(self,parent=None,category=None,trait=None):
        super(traitContainer,self).__init__(parent)
        traitDict = info["traits"][category][trait]
        # self.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        # self.setLineWidth(2)
        self.selected=False
        self.setFixedHeight(120)
        self.setFixedWidth(245)
        self.prerequisites_met = False
        self.trait_acquired = False
        self.category = category
        self.trait = trait
        self.setStyleSheet("background-color: rgb(80, 80, 80);border-radius: 8px;")
        if self.trait_acquired:
            self.setStyleSheet("background-color:rgb(80, 80, 80);border-radius: 8px;border: 1px solid darkGreen;")
        elif not self.prerequisites_met: 
            self.setStyleSheet("background-color:rgb(80, 80, 80);border-radius: 8px;border: 1px solid darkRed;")
        self.layout = QGridLayout()
        title = QLabel(info["traits"][category][trait]["name"])
        # title.setWeight()
        title.setStyleSheet("background-color:rgb(80, 80, 80);border:0px;font:bold")
        self.descContainer = QScrollArea()
        self.descContainer.setStyleSheet("background-color:rgb(80, 80, 80);border:0px;border-radius:0px")
        traitLabel = QLabel(trait)
        prerequisites = QLabel("".join(["Prerequisites: ","".join(info["traits"][self.category][self.trait]["prerequisites"])]))
        prerequisites.setStyleSheet("background-color:rgb(80, 80, 80);border:0px;color:darkGray")
        self.layout.addWidget(prerequisites,1,0,1,2)
        traitLabel.setStyleSheet("background-color:rgb(80, 80, 80);border:0px;color:darkGray")
        desc = QLabel(info["traits"][category][trait]["description"])
        desc.setStyleSheet("background-color:rgb(80, 80, 80);border:0px")
        desc.setWordWrap(True)
        self.layout.addWidget(title,0,0,1,1)
        self.layout.addWidget(traitLabel,0,1,1,1)
        self.descContainer.setWidget(desc)
        self.setLayout(self.layout)
    
    def update(self):
        self.prerequisites_met = self.checkPrerequisites()
        if self.selected:
            self.setStyleSheet("background-color:rgb(80,80,80);border-radius:8px;border:1px solid White;")
            desc = QLabel(info["traits"][self.category][self.trait]["description"])
            desc.setStyleSheet("background-color:rgb(80, 80, 80);border:0px")
            desc.setWordWrap(True)
            modifs = QLabel(parseModifiers(info["traits"][self.category][self.trait]["modifiers"]))
            modifs.setStyleSheet("background-color:rgb(80, 80, 80);border:0px;color:darkGray")
            self.layout.addWidget(self.descContainer,2,0,1,2)
            self.layout.addWidget(modifs,3,0,1,2)
            self.setFixedHeight(180)
        elif self.trait_acquired:
            self.setStyleSheet("background-color:rgb(80, 80, 80);border-radius: 8px;border: 1px solid darkGreen;")
        elif not self.prerequisites_met: 
            self.setStyleSheet("background-color:rgb(80, 80, 80);border-radius: 8px;border: 1px solid darkRed;")
        else:
            self.setStyleSheet("background-color: rgb(80, 80, 80);border-radius: 8px;")
            
        if not self.selected:
            self.setFixedHeight(120)
            self.layout.removeWidget(self.descContainer)
            self.descContainer.setParent(None)
            
        self.parent().adjustSize()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet("background-color:rgb(80,80,80);border-radius:8px;border:1px solid White;")
            if self.selected:
                self.selected = False
                self.update()
            else:
                for trait in self.parent().parent().parent().parent().parent().parent().parent().parent().parent().parent().traitsInfoWidgets:
                    if trait.selected:
                        trait.selected = False
                        trait.update()
                self.selected=True
                self.update()
        
        
    def checkPrerequisites(self):
        return True

def parseModifiers(modifiersDict):
    retnString = ""
    for i in modifiersDict:
        # print(info["modifiers"][i])
        retnString = "".join([retnString,info["modifiers"][i]["name"], ": ", "%+5d" %modifiersDict[i],"\n"])
    return retnString

def parseStat(statString):
    try:
        return info["modifiers"][statString]["name"]
    except:
        return statString
    

def deParseStat(statString):
    for key in info["modifiers"].keys():
        if info["modifiers"][key]["name"] == statString:
            return key


def getMainStatModif(statScore):
    return math.floor((statScore - 10)/2)

def parseProficiency(prof):
    if prof == 0:
        return ""
    elif prof == 1:
        return "Proficiency"
    elif prof == 2:
        return "Expertise"
    else:
        return ""
    
def getTotalModifier(modifiersList,attrString):
    total = 0
    for group in modifiersList:
        if attrString in group.keys():
            val = group[attrString]
            total += val
    return total

def genModifsDict(modifiersList):
    keys = []
    for group in modifiersList:
        for key in group.keys():
            if key not in keys:
                keys.append(key)
    modifsDict = dict()
    for key in keys:
        modifsDict[key] = 0
        for group in modifiersList:
            if key in group.keys():
                modifsDict[key] += group[key]
    return modifsDict
        
    
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    dark_palette = QPalette()
    
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    root = Tk()
    root.withdraw()
    charGen = mainWindow()
    charGen.show()
    sys.exit(app.exec_()) 
