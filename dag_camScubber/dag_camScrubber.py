'''
Script:		dag_camScrubber
Version:	1.0
Author:		dag
Website:	
E-mail:		thedagnode@gmail.com

Descr:		scrub between cameras. useful with photogrammetry

Usage: run:

import dag_camScrubber
reload(dag_camScrubber)

if __name__ == "__main__":
    try:
        ui.deleteLater()
    except:
        pass
    
    
    try:
        ui = dag_camScrubber.CamScrubber()
        ui.create()
        ui.show()
        
    except:
        ui.deleteLater()


Requires:	dag_stringArrayConverter.mel

'''

import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
import re
from maya import OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import __version__
from shiboken2 import wrapInstance

from PySide2.QtWidgets import *
from PySide2.QtCore import *



def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    
class CamScrubber(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(CamScrubber, self).__init__(parent)
        self.qtSignal = QtCore.Signal()
        #################################################################
        
    cams = []
    curCam = ''
    tglCam = True
    tglIP = True
    fileInfoExist = False
    
    def create(self):
    
        
        self.setWindowTitle('Cam Scrubber')        
        self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(310, 450) # re-size the window
        #self.setGeometry(50, 50, 310, 310) 
    
    
        # create layout
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setSpacing(0)
        #self.mainLayout.setMargin(0)
        
        
        
        # create menubar
        self.menuBar = QMenuBar(parent = maya_main_window()) # requires parent
        self.menu = QMenu(self)
        
        self.menu.setTitle("Menu")
        self.menuBar.addMenu(self.menu)
        
        self.menu.addAction("Delete file info node")
        self.menu.triggered[QAction].connect(self.delFileInfoNode)

        self.mainLayout.addWidget(self.menuBar)




        #Create combo box (drop-down menu) and add menu items 

        self.combo = QtWidgets.QComboBox(self)        
        self.combo.addItem( 'modelPanel1' )        
        self.combo.addItem( 'modelPanel2' )        
        self.combo.addItem( 'modelPanel3' )     
        self.combo.setCurrentIndex(0)
        #self.combo.move(20, 20)        
        self.combo.activated[str].connect(self.combo_onActivated)        


                            
        # create dial
        self.qDial = QtWidgets.QDial(self)
        self.qDial.setMinimum(0)
        self.qDial.setMaximum(0)
        self.qDial.setValue(0)
        self.qDial.valueChanged.connect(self.switchCam)
        # create intfield
        self.indexField = QtWidgets.QLineEdit(self)
        self.indexField.setFixedWidth(40)
        self.indexField.setText(str(self.qDial.value()))
        
        
        
        
        # create visibility controls
        self.visLabel = QtWidgets.QLabel("visibility        ")
        # create slider for visibility
        self.visSlider = QtWidgets.QSlider(self)
        self.visSlider.setOrientation(QtCore.Qt.Horizontal)
        self.visSlider.setRange(0, 100)
        self.visSlider.setValue(50)
        self.visSlider.valueChanged.connect(self.visSliderChanged)
        # create intfield
        self.visField = QtWidgets.QLineEdit(self)
        self.visField.setFixedWidth(40)
        self.visField.setText(str(self.visSlider.value()))
        
        # create image plane depth controls
        self.depthLabel = QtWidgets.QLabel("image depth ")
        # create slider for image plane depth
        self.imgDepthSlider = QtWidgets.QSlider(self)
        self.imgDepthSlider.setOrientation(QtCore.Qt.Horizontal)
        self.imgDepthSlider.setRange(1, 200)
        self.imgDepthSlider.setValue(1)
        self.imgDepthSlider.valueChanged.connect(self.depthSliderChanged)
        # create intfield
        self.imgDepthField = QtWidgets.QLineEdit(self)
        self.imgDepthField.setFixedWidth(40)
        self.imgDepthField.setText('1')
        
        # slidersLayout
        self.visSliderLayout = QtWidgets.QHBoxLayout(self)
        self.imgDepthSliderLayout = QtWidgets.QHBoxLayout(self)
        # add sliders to layouts
        self.visSliderLayout.addWidget(self.visLabel)
        self.visSliderLayout.addWidget(self.visSlider)
        self.visSliderLayout.addWidget(self.visField)
        #
        self.imgDepthSliderLayout.addWidget(self.depthLabel)
        self.imgDepthSliderLayout.addWidget(self.imgDepthSlider)
        self.imgDepthSliderLayout.addWidget(self.imgDepthField)




        # near clip plane control
        self.nearClipLabel = QtWidgets.QLabel("near clip plane")
        # near clip intfield
        self.nearClipField = QtWidgets.QLineEdit(self)
        self.nearClipField.setFixedWidth(40)
        self.nearClipField.setText('100')
        self.nearClipField.returnPressed.connect(self.nearClipFieldClicked)
        # near clip plane layout
        self.nearClipLayout = QtWidgets.QHBoxLayout(self)
        # add widgets to layouts
        self.nearClipLayout.addWidget(self.nearClipLabel)
        self.nearClipLayout.addWidget(self.nearClipField)




        # bottom buttons layout
        #self.btmBtnsLayout = QtWidgets.QHBoxLayout(self)
        #Load cameras button
        self.loadCamsButton = QtWidgets.QPushButton('Load Cameras', self)
        self.loadCamsButton.clicked.connect(self.loadCams)
        # toggle cameras button
        self.toggleCamsBtn = QtWidgets.QPushButton('Toggle Cameras', self)
        self.toggleCamsBtn.clicked.connect(self.toggleCams)
        # toggle image planes button
        self.toggleImagePlanesBtn = QtWidgets.QPushButton('Toggle Image Planes', self)
        self.toggleImagePlanesBtn.clicked.connect(self.toggleImagePlanes)
        # select current camera
        self.selectCurCamBtn = QtWidgets.QPushButton('Select Current Camera', self)
        self.selectCurCamBtn.clicked.connect(self.selectCurCam)       
        
        
        # add widgets to layout
        self.mainLayout.addWidget(self.combo)
        self.mainLayout.addWidget(self.qDial)
        self.mainLayout.addWidget(self.indexField)
        # add slider layouts to main layout
        self.mainLayout.addLayout(self.visSliderLayout)
        self.mainLayout.addLayout(self.imgDepthSliderLayout)
        #
        self.mainLayout.setAlignment(self.indexField, QtCore.Qt.AlignHCenter)
        self.mainLayout.addLayout(self.nearClipLayout)
        self.mainLayout.addWidget(self.loadCamsButton)
        self.mainLayout.addWidget(self.toggleCamsBtn)
        self.mainLayout.addWidget(self.toggleImagePlanesBtn)
        self.mainLayout.addWidget(self.selectCurCamBtn)
        
        
        # QPlainTextEdit
        self.cameraNameField = QtWidgets.QLabel('Camera: ')
        self.mainLayout.addWidget(self.cameraNameField)
        
        self.updateFileInfo()
        self.updateUI()


    def delFileInfoNode(self):
        try:
            pm.fileInfo(rm='photogrammetryCameras')
        except:
            pass
        self.cams = []
        self.updateUI()
        self.cameraNameField.setText('Camera: ')



    def updateUI(self):
        self.hideImagePlanes(self.cams)
        self.qDial.setMaximum(len(self.cams))
        self.qDial.setMinimum(1)
        self.qDial.setValue(1)
        if len(self.cams)>0:
            self.indexField.setText(str(self.qDial.value()))
        else:
            self.indexField.setText('0')
        try:
            self.curCam = self.cams[0]
        except:
            pass
        


    def updateFileInfo(self):
        
        # check to see if a fileInfo for cameras, exist
        infos = pm.fileInfo(q=1)
        for info in infos:
            print info
            if 'photogrammetryCameras' in info:
                self.fileInfoExist = True
        
        '''
        # read cameras from fileInfo
        if self.fileInfoExist == True:
        
            try:
                cams = pm.fileInfo('photogrammetryCameras', q=1).split(' ')
                for cam in cams:
                    # push as pymel object
                    cam = pm.ls(cam)
                    if len(cam)>0:
                        # and clean up as it comes back as a list. 
                        # We just want the pymel object
                        self.cams.append(cam)
            except:
                pass
            '''
        if self.fileInfoExist == True:
            # read from fileInfo
            camStr = pm.fileInfo('photogrammetryCameras', q=1)
            infoCams = camStr.split(',')
            cams = pm.ls([cam for cam in infoCams if len(cam)>0])    
            self.cams = cams
            
 

    #Change commmand string when combo box changes
    def combo_onActivated(self, text):        
        #self.cmd = 'poly' + text + '()'
        pm.select(self.curCam, r=1)
        mPanel = self.combo.currentText()
        cmd = ('lookThroughSelected("0", "%s")' % mPanel)
        mel.eval(cmd)
    
        




    def loadCams(self):
        self.delFileInfoNode()
        
        # add cameras
        sel = pm.ls(sl=1, type='transform')
        cams = [camera for camera in sel if camera.getShape().type()=='camera']
        cams.sort()
        camStr = ''
        if len(cams)>0:
            for cam in cams:
                camStr += cam + ','
            pm.fileInfo('photogrammetryCameras', str(camStr))

            self.cams = cams
            
        self.updateUI()
        '''
        # update ui
        self.hideImagePlanes(self.cams)
        self.qDial.setMaximum(len(self.cams))
        self.qDial.setMinimum(1)
        self.qDial.setValue(1)
        self.curCam = self.cams[0]
        '''

        #self.switchCam()
        self.cameraNameField.setText('Camera: ' + self.curCam.name())



    def switchCam(self):
    
        if len(self.cams)>0:
            val = self.qDial.value()
            self.indexField.setText(str(val))

            '''
            try:
                #self.curCam.setAttr('visibility', 0)
                pass
            except:
                pass
            '''
            
            # set previous camera's image plane visibility to 0
            try:
                ip = self.curCam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('visibility', 0)

            except:
                pass
            
            # set current camera's image plane visibility to 1
            try:
                self.curCam = self.cams[int(val-1)]
                #self.curCam.setAttr('visibility', 1)
                ip = self.curCam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('visibility', 1)
            except:
                pass
            
            try:
                # get current camera and set modelPanelView to this camera
                #pm.select(self.curCam, r=1)
                mPanel = self.combo.currentText()
                pm.lookThru(self.curCam, mPanel)
                #cmd = ('lookThroughSelected("0", "%s")' % mPanel)
                #mel.eval(cmd)
            except:
                pass
        
        self.cameraNameField.setText('Camera: ' + self.curCam.name())



    def visSliderChanged(self):
        
        val = self.visSlider.value()/100.0
        self.visField.setText(str(val))
        for cam in self.cams:
            try:
                ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('alphaGain', val)

            except:
                pass

    def depthSliderChanged(self):

        val = self.imgDepthSlider.value()
        self.imgDepthField.setText(str(val))
        
        for cam in self.cams:

            try:
                ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('depth', val)

            except:
                pass



    def toggleCams(self):
        
        cams = pm.ls(sl=1)
        cams = [camera for camera in cams if camera.getShape().type()=='camera']
        if self.tglCam:
            #for cam in self.cams:
            for cam in cams:
                try:
                    cam.setAttr('visibility', 1)
                    ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                    ip.setAttr('visibility', 1)
                except:
                    pass
                
                try:
                    ip = cam.getShape().listRelatives(type="transform")[0]
                    ip.setAttr('visibility', 1)
                except:
                    pass
            self.tglCam = False

        else:
            #for cam in self.cams:
            for cam in cams:
                try:
                    cam.setAttr('visibility', 0)
                    ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                    ip.setAttr('visibility', 0)
                except:
                    pass
                
                try:
                    ip = cam.getShape().listRelatives(type="transform")[0]
                    ip.setAttr('visibility', 0)
                except:
                    pass
            self.tglCam = True
                    


    def hideImagePlanes(self, cams):
        #cams = pm.ls(sl=1)
        #cams = [camera for camera in cams if camera.getShape().type()=='camera']

        for cam in cams:
            try:
                #cam.setAttr('visibility', 0)
                ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('visibility', 0)
            except:
                pass



    def toggleImagePlanes(self):
        
        sel = pm.ls(sl=1)
        cams = [camera for camera in sel if camera.getShape().type()=='camera']

        if self.tglIP:
            #for cam in self.cams:
            for cam in cams:
                try:
                    ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                    ip.setAttr('visibility', 1)
                except:
                    pass
            self.tglIP = False

        else:
            #for cam in self.cams:
            for cam in cams:
                try:
                    ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                    ip.setAttr('visibility', 0)
                except:
                    pass
            self.tglIP = True
            

    def selectCurCam(self):
        if len(self.curCam.name())>0:
            try:
                self.curCam.select(r=1)
            except:
                pass

    def nearClipFieldClicked(self):

        if len(self.cams)>0:
            for cam in self.cams:
                try:
                    camShape = cam.getShape()
                    camShape.setAttr('nearClipPlane', float(self.nearClipField.text()) )
                except:
                    pass


        
        
    '''
    # resetImgPlanes(10)
    def resetImgPlanes(self, val, *args):
    
        
        cams = pm.ls(sl=1)
        cams = [camera for camera in cams if camera.getShape().type() == 'camera']

        ips = pm.ls(sl=1)
        ips = [ip for ip in ips if ip.getShape().type() == 'imagePlane']
        
        for cam in cams:
            try:
                ip = cam.getShape().listConnections(type="imagePlane")[0].getShape()
                ip.setAttr('depth', val)
            except:
                pass

        for ip in ips:
            try:
                ip.setAttr('depth', val)
            except:
                pass
    
    '''