# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import string
import numpy as npy
from numpy import *
import networkx as nx
import pickle
import os as os
import xml.etree.ElementTree as ET
import math
from osgeo import gdal
from scipy import ndimage
import shapefile
#from pylab import *
from scipy.signal import *
import json
from matplotlib import *
use("agg")
#from matplotlib.pyplot import *
import matplotlib.patheffects as PathEffects
from pylab import *
from mpl_toolkits.axes_grid.axislines import Subplot
import time
import random as random2
import datetime
#import simplekml
from scipy.misc import imread

response.menu = [['Create a Route', False, URL('start')],
                 ['Upload a Route', False, URL('uploadroute')],
                 ['Route Database', False, URL('routedatabase')],
                 ['Blog', False, A( XML('Blog'),_href='http://sierramapper.blogspot.com')],
                 ['Donate', False, A( XML('Donate'),_href='https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=W4T7GG4BQT2SQ&lc=US&item_name=For%20Good%20Karma%21&button_subtype=services&currency_code=USD&bn=PP%2dBuyNowBF%3abtn_buynowCC_LG%2egif%3aNonHosted')]]

    

def createHashFile():
    thisFilename = str(json.loads(request.post_vars.array)) + '.txt'
    thisFile =os.path.join(request.folder, 'uploads/XC', thisFilename)
    f = open(thisFile, 'wb')
    f.close()

def updateHashFile():
    inString = str(json.loads(request.post_vars.array)).split('/')
    thisSeg = inString[0]
    thisHash = inString[1]
    thisData = thisSeg + ', ' + inString[2]
    thisFilename = thisHash + '.txt'
    thisFile =os.path.join(request.folder, 'uploads/XC', thisFilename)
    f = open(thisFile, 'ab')
    f.write(thisData)
    f.close()

def clearDB():
    db.routes.truncate();
    #db.auth_user.truncate();

def createRoutes():
    # add instances of some well known routes
    redirect(URL('default/mapper','/n001/n050/m039/m043/k043/s018/m019')) # JMT
    redirect(URL('default/mapper','/n001/n011'))

def uploadroute():
     #filename = os.path.join(request.folder, 'static', 'gr.gpickle')
     #filename = os.path.join(request.folder, 'static', 'gr.gpickle')
     form = SQLFORM.factory(
        #Field('file_name', requires=IS_NOT_EMPTY()),
        Field('file', 'upload',uploadfolder=os.path.join(request.folder, 'uploads')),
        Field('name','string'))


     if form.accepts(request.vars, session):  #.process().accepted:
        session.file_name= form.vars.file_name
        orig_name = request.vars.file.filename
        #os.rename('static/' + coded_name, 'static/' + orig_name)
        key = ''
        for i in range(6):
            key += random2.choice(string.lowercase  + string.uppercase) #string.uppercase
        try:
            thisAuthor = auth.user.username
        except AttributeError:
            thisAuthor = 'Anonymous'

        db.routes.insert(   route_id = key,
                            filename = form.vars.file,
                            name = form.vars.name,
                            routetype = 'Uploaded',
                            author = thisAuthor,
                            orig_filename = orig_name,
                            inputstring = '')
        response.flash = 'Worked! ' + str(form.vars.file) + ', ' + key
        createProfile(key, form.vars.file)
        redirect('http://awhite4777.pythonanywhere.com/SierraMapperAlpha/default/kmlmapper/' + key)

     elif form.errors:
        response.flash = 'form has errors'


     return dict(form=form)

def routedatabase():
    def routeStrToURL(routeStr):
        newStr = ''
        for i in range(0, len(routeStr)/4):
            newStr = newStr + routeStr[4*i:4*i+4] + '/'
        return newStr[0:-1]

    def createSierraMapperLink(key):
        #return URL('SierraMapperAlpha/default','mapper',routeStrToURL(row.inputstring))
        row = db(db.routes.route_id==key).select().first()
        if row.routetype == 'Sierra Mapper':
            return URL('SierraMapperAlpha/default','mapper',routeStrToURL(row.inputstring))
        elif row.routetype == 'Uploaded':
            return URL('SierraMapperAlpha/default','kmlmapper',row.route_id)
        else:
            return 'Cannot!'

    def createCalTopoLink(key):
        #return URL('SierraMapperAlpha/default','mapper',routeStrToURL(row.inputstring))
        row = db(db.routes.route_id==key).select().first()
        calString = 'http://caltopo.com/map.html#kml='
        if row.routetype == 'Sierra Mapper':
            return A( XML('View at<br>CalTopo.com'),_href=calString + 'http://awhite4777.pythonanywhere.com/SierraMapperAlpha/static/routes/' + row.filename.split('/')[-1], _target="blank")
        elif row.routetype == 'Uploaded':
            return A( XML('View at<br>CalTopo.com'),_href=calString + 'http://awhite4777.pythonanywhere.com/SierraMapperAlpha/uploads/' + row.filename, _target="blank")
        else:
            return 'Cannot!'

    # create an insert form from the table
    #form = SQLFORM(db.routes).process()

    # if form correct perform the insert
    #if form.accepted:
    #    response.flash = 'new record inserted'

    # and get a list of all persons

    #records = SQLTABLE(db().select(db.routes.ALL),headers='fieldname:capitalize')

    thisURL = 'http://awhite4777.pythonanywhere.com/SierraMapperAlpha/static/profiles/'
    links=[lambda row: A(IMG(_src=thisURL+row.route_id+'_profile_thumb.png', _width=200, _height=80), _href=thisURL+row.route_id+'_profile.png')]
    #links=[lambda row: A(IMG(_src=thisURL+row.profile, _width=150, _height=50), _href=thisURL+row.profile)]
    thisURL2 = 'http://caltopo.com/'
    links2=[lambda row: createCalTopoLink(row.route_id)]
    links3=[lambda row: A( XML('<right>View at <br>Sierra Mapper'),_href=createSierraMapperLink(row.route_id))]
    #links=[lambda row: A(IMG(_src=URL('static', args=row.profile), _width=50, _height=50), _href=URL('static', args=row.profile))]
    for i in db.routes:
        i.writable = True

    db.routes.comments.writable = True
    db.routes.name.writable = True

    grid = SQLFORM.grid(db.routes,
                             fields = [db.routes.created, db.routes.name, db.routes.route_id, db.routes.routetype, db.routes.startlocation, db.routes.endlocation, db.routes.lineardistance, db.routes.ascent, db.routes.descent, db.routes.forecast],
                             headers = {'routes.created':XML('<center>Created on'),
                                        'routes.route_id':XML('<center>Route ID'),
                                        'routes.name':XML('<center>Route Name'),
                                        'routes.routetype':XML('<center>Route Type'),
                                        'routes.startlocation':XML('<center>Start Location'),
                                        'routes.endlocation':XML('<center>Finish Location'),
                                        'routes.lineardistance':XML('<center>Distance'),
                                        'routes.ascent':XML('<center>Ascent'),
                                        'routes.descent':XML('<center>Descent'),
                                        'routes.forecast':XML('<center>NOAA Forecast <br>for Trailhead')},

                             links=links+links2+links3,#+links3,#+links3,
                             user_signature=True,
                             maxtextlength = 50)

    #return dict(form=form, records=records, grid=grid)
    return dict(grid=grid)


def start():
    filename = os.path.join(request.folder, 'static', 'gr.gpickle')
    gr = nx.read_gpickle(filename)
    nodeCoords = nx.get_node_attributes(gr, 'Coordinates')
    nodeNicknames = nx.get_node_attributes(gr, 'Nicknames')
    nodeMarkerList = []
    for node in list(gr.nodes_iter()):
        nodeMarkerList.append(str(node))
        nodeMarkerList.append(nodeCoords[node][0])
        nodeMarkerList.append(nodeCoords[node][1])

        if len(nodeNicknames[node]) == 0:
            nodeMarkerList.append('Unnamed Jct.')
        else:
            nodeMarkerList.append(nodeNicknames[node][0])
        nodeMarkerList.append(nodeCoords[node][2]) # add elev

    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    response.flash = T("Welcome to web2py!")
    """
    return dict(nodeMarkers=json.dumps(nodeMarkerList))

def start2():
    filename = os.path.join(request.folder, 'static', 'gr.gpickle')
    gr = nx.read_gpickle(filename)
    nodeCoords = nx.get_node_attributes(gr, 'Coordinates')
    nodeNicknames = nx.get_node_attributes(gr, 'Nicknames')
    nodeMarkerList = []
    for node in list(gr.nodes_iter()):
        nodeMarkerList.append(str(node))
        nodeMarkerList.append(nodeCoords[node][0])
        nodeMarkerList.append(nodeCoords[node][1])

        if len(nodeNicknames[node]) == 0:
            nodeMarkerList.append('Unnamed Jct.')
        else:
            nodeMarkerList.append(nodeNicknames[node][0])
        nodeMarkerList.append(nodeCoords[node][2]) # add elev

    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    response.flash = T("Welcome to web2py!")
    """
    return dict(nodeMarkers=json.dumps(nodeMarkerList))

def getCoords(root2, markerList):
    if root2[0][2].tag == '{http://www.opengis.net/kml/2.2}Folder':

        for j in range(2, len(root2[0])):
            for i in root2[0][j]:
            
                if i.tag == '{http://www.opengis.net/kml/2.2}Placemark':        
                    k = 3 # index of meat -- changed when CalTopo changed .kml format
            
                    if i[k].tag == '{http://www.opengis.net/kml/2.2}Polygon':
                        print('A polygon')
                        inputCoords = i[k][2][0][0].text.split(',')
                        #inputCoords = i[3][2][0][0].text.split(',')
            
                    if i[k].tag == '{http://www.opengis.net/kml/2.2}LineString':
                        print('A Linestring')
                        inputCoords = i[k][2].text.split(',')
            
                    if i[k].tag == '{http://www.opengis.net/kml/2.2}Point':
                        print('A point: ' + i[0].text)
                        thisLat = float(i[k][0].text.split(',')[1].strip('0\n'))
                        thisLong = float(i[k][0].text.split(',')[0].strip('0\n'))
                        thisLake = Lake(i[0].text)
                        thisLake.coords = array([thisLong, thisLat])
                        thisLake.type = 'Custom'
                        markerList.append(thisLake)
    # old approach:
    else:
        for i in root2[0]:
    
            if i.tag == '{http://www.opengis.net/kml/2.2}Placemark':
    
                k = 3 # index of meat -- changed when CalTopo changed .kml format
                try:
                    i[k].tag
                except IndexError:
                    k = 2
    
                if i[k].tag == '{http://www.opengis.net/kml/2.2}Polygon':
                    print('A polygon')
                    inputCoords = i[k][2][0][0].text.split(',')
    
                if i[k].tag == '{http://www.opengis.net/kml/2.2}LineString':
                    print('A Linestring')
                    inputCoords = i[k][2].text.split(',')
    
                if i[k].tag == '{http://www.opengis.net/kml/2.2}Point':
                    print('A point: ' + i[0].text)
                    thisLat = float(i[k][0].text.split(',')[1].strip('0\n'))
                    thisLong = float(i[k][0].text.split(',')[0].strip('0\n'))
                    thisLake = Lake(i[0].text)
                    thisLake.coords = array([thisLong, thisLat])
                    thisLake.type = 'Custom'
                    markerList.append(thisLake)
    outCoordsArray = zeros(((len(inputCoords)-1)/2, 3))

    for i in range(0, len(outCoordsArray[:,0])):
        outCoordsArray[i,0] = float(inputCoords[2*i].strip('0\n'))
        outCoordsArray[i,1] = float(inputCoords[2*i+1].strip('0\n'))
        outCoordsArray[i,2] = 0
    return outCoordsArray

def snow():
    from time import *
### Begin script
    key = request.args[0]
    thisRecord = db(db.routes.route_id==key).select().first()
    routeFilename = thisRecord.filename
    #db.routes.insert(route_id = key, filename = routeFilename, name = 'Sierra Mapper Route', routetype = 'Uploaded',author = thisAuthor, orig_filename = routeFilename, inputstring = inputString)

    filename = os.path.join(request.folder, 'uploads', routeFilename)
    tree2 = ET.parse(filename)
    root2 = tree2.getroot()

    markerList = [] # used for custom markers found in kml file    
    outCoordsArray = getCoords(root2, markerList)
    profileFileName = os.path.join(request.folder, 'static', 'dataprofiles/' + key + '_profile_data.csv')
    profile = loadtxt(profileFileName, delimiter = ',')
    
    imList = []
    fileList = []
    dateList = []
    fileList.append('051316')
    fileList.append('052216')
    fileList.append('053116')
    fileList.append('060316')
    fileList.append('060716')
    fileList.append('061416')
    fileList.append('062316')
    
    for j in fileList:
        imList.append(os.path.join(request.folder, 'static', 'snow/' + j + '.png'))
        dateList.append(datetime.date(2016, int(j[0:2]), int(j[2:4])))
    
    arrList = []
    for j in imList:
        thisImage = imread(j, flatten = True)        
        th = 250.0
        lv = thisImage < th
        hv = thisImage >= th
        thisImage[lv] = 0
        thisImage[hv] = 1.0 
        arrList.append(flipud(thisImage))
    
    x0 = -120.5527
    x1 = -117.9393
    y0 = 36.0097
    y1 = 38.8192
    doThese = [1]
    
    dist = zeros(len(outCoordsArray[:,0]))  
    for i in range(1, len(outCoordsArray)):
        dist[i] = calcDist2(outCoordsArray[i-1,:], outCoordsArray[i,:]) + dist[i-1] 
    dist = 1.03*dist # not sure why I need this here...

    

    
    out = zeros( len(outCoordsArray[:,0]) )
    startDate = dateList[0]
    span = float((dateList[-1] - startDate).days)
    figwidth = max(max(dist)/8., 20)
    figure(figsize = [figwidth,4])
    text(0.5, 1.1, 'S N O W !', transform=gcf().transFigure, horizontalalignment='center', fontsize = 24, fontweight = 'bold')
    for j in range(0, len(imList)):
        thisColor = 0.9*((dateList[j] - startDate).days/span)
        elev = interp(dist, profile[:,0], profile[:,1])
        elevm = copy(elev)
        arr = arrList[j]
        for i in range(0, len(outCoordsArray[:,0])):
            thisX = len(arr[0,:])*(outCoordsArray[i,0] - x0)/(x1-x0)  
            thisY = len(arr[:,0])*(outCoordsArray[i,1] - y0)/(y1-y0)  
            #print(str(thisX), str(thisY))    
            out[i] = ndimage.map_coordinates(arr[thisY-20:thisY+20,thisX-20:thisX+20], [[20], [20]], order=3)[0] # make it out[i,j] when you iterate over j
    

    
    
        for i in range(0, len(elevm)):
            if out[i] < 0.1:
                elevm[i] = NaN
                
        xi = linspace(0, max(dist), 100001)
        outi = interp(xi, dist, out)
        covDist = round(trapz(outi, x = xi), 2)
        covPercent = round(100*covDist/max(dist),1)
        #subplot(3, 1, j+1)
        legendLabel = dateList[j].strftime('%m/%d/%Y') + ' ('+ str(round(abs(covPercent),1)) + '% snow-covered: ' + str(round(abs(covDist),1)) + ' of ' + str(round(max(dist),1)) + ' miles)'
        dy = (len(imList)-j-1)*((max(elev) - min(elev)))*.04
        plot(dist, elevm-dy, color = 'w', lw = 4, alpha = 1)        
        plot(dist, elevm-dy, color = cm.jet(thisColor), lw = 4, alpha = 0.5)
        plot(dist, elevm-dy, color = cm.jet(thisColor), lw = 2.5, alpha = 0.7, label = legendLabel) 
        plot(profile[:,0], profile[:,1]-dy, color = 'k', alpha = 0.3)
        #plot(dist, elevm, color = 'r', lw = 2.5, alpha = 0.7)
    fill_between(profile[:,0], profile[:,1], color = [0.5, 0.5, 0.5], alpha = 0.5)
    plot(profile[:,0], profile[:,1], color = 'k')
    
    #gcf().suptitle('Snow cover along the JMT deduced from 6/03/16 MODIS satellite imagery\n\n\n\n\n\n', fontsize = 16, fontweight = 'bold')
    grid(axis = 'both')
    title('S N O W !!', horizontalalignment='center', fontsize = 14, fontweight = 'bold')
    
    t = text(0.01, 0.05, 'Snow covered sections are highlighted in a color corresponding to imagery date', transform = gca().transAxes, horizontalalignment = 'left', va = 'top', fontsize = 8, fontstyle = 'italic')
    t.set_path_effects([PathEffects.Stroke(linewidth=2, foreground='white', alpha = 0.8), PathEffects.Normal()])
    
    #t = text(0.127, 0.82, 'Current coverage:', transform = gcf().transFigure, horizontalalignment = 'left', va = 'top', fontsize = 14, fontstyle = 'italic')
    #t.set_path_effects([PathEffects.Stroke(linewidth=4, foreground='white', alpha = 0.8), PathEffects.Normal()])
    

    #t = text(0.01, 0.9, str(covPercent) + '% (' + str(covDist) + ' of ' + str(round(max(dist),2)) + ' miles)' , transform = gca().transAxes, horizontalalignment = 'left', va = 'top', fontsize = 10, fontstyle = 'italic', fontweight = 'bold', color = 'r')
    #t.set_path_effects([PathEffects.Stroke(linewidth=4, foreground='white', alpha = 0.8), PathEffects.Normal()])
    legend(loc = 2, fontsize = 7, fancybox = True, framealpha = 0.7)
    opts = array([5, 2, 1, .5, .25, .1])
    this = opts > max(dist)/25.
    if len(opts[this]) < 1:
        xtickspacing = 5
    else:
        xtickspacing = opts[this][-1]
    xticks(arange(0, max(dist)+xtickspacing, xtickspacing))
    axis(xmax = max(dist), xmin = 0, ymin = 1000*int(min(profile[:,1]/1000)), ymax = 1000*ceil(max(profile[:,1]/1000)))
    xlabel('Distance [mi]')
    ylabel('Elevation [ft]')
    saveName = os.path.join(request.folder, 'static', 'snowprofiles', key + '_' + 'snow_profile.png')
    tight_layout()
    savefig(saveName, dpi = 200)
    close('all')
    return dict(key = key)

def snowOld():
### Begin script
    key = request.args[0]
    thisRecord = db(db.routes.route_id==key).select().first()
    routeFilename = thisRecord.filename
    #db.routes.insert(route_id = key, filename = routeFilename, name = 'Sierra Mapper Route', routetype = 'Uploaded',author = thisAuthor, orig_filename = routeFilename, inputstring = inputString)

    filename = os.path.join(request.folder, 'uploads', routeFilename)
    tree2 = ET.parse(filename)
    root2 = tree2.getroot()

    markerList = [] # used for custom markers found in kml file    
    outCoordsArray = getCoords(root2, markerList)
    profileFileName = os.path.join(request.folder, 'static', 'dataprofiles/' + key + '_profile_data.csv')
    profile = loadtxt(profileFileName, delimiter = ',')
    
    imList = []
    dateList = []
    dateList.append('060916')
    dateList.append('060316')
    dateList.append('052216')
    
    for j in dateList:
        imList.append(os.path.join(request.folder, 'static', 'snow/' + j + '.png'))
    
    arrList = []
    for j in imList:
        thisImage = imread(j, flatten = True)        
        th = 250.0
        lv = thisImage < th
        hv = thisImage >= th
        thisImage[lv] = 0
        thisImage[hv] = 1.0 
        arrList.append(flipud(thisImage))
    
    x0 = -120.5527
    x1 = -117.9393
    y0 = 36.0097
    y1 = 38.8192
    doThese = [1]
    
    dist = zeros(len(outCoordsArray[:,0]))  
    for i in range(1, len(outCoordsArray)):
        dist[i] = calcDist2(outCoordsArray[i-1,:], outCoordsArray[i,:]) + dist[i-1] 
    dist = 1.03*dist # not sure why I need this here...

    

    
    out = zeros( len(outCoordsArray[:,0]) )
    
    figure(figsize = [20,12])
    text(0.5, 1.1, 'S N O W !', transform=gcf().transFigure, horizontalalignment='center', fontsize = 24, fontweight = 'bold')
    for j in range(0, len(imList)):
        elev = interp(dist, profile[:,0], profile[:,1])
        elevm = copy(elev)
        arr = arrList[j]
        for i in range(0, len(outCoordsArray[:,0])):
            thisX = len(arr[0,:])*(outCoordsArray[i,0] - x0)/(x1-x0)  
            thisY = len(arr[:,0])*(outCoordsArray[i,1] - y0)/(y1-y0)  
            #print(str(thisX), str(thisY))    
            out[i] = ndimage.map_coordinates(arr[thisY-20:thisY+20,thisX-20:thisX+20], [[20], [20]], order=3)[0] # make it out[i,j] when you iterate over j
    

    
    
        for i in range(0, len(elevm)):
            if out[i] < 0.1:
                elevm[i] = NaN
                
        xi = linspace(0, max(dist), 100001)
        outi = interp(xi, dist, out)
        subplot(3, 1, j+1)
        
        #for j in range(0, len(JMT), 10):
        #    if out[j] > 0.1 and out[j+1] > 0.1:
        #        plot(dist[j:j+2], elev[j:j+2], color = 'r', lw = 5, alpha = 0.5*abs(out[j]))
        plot(dist, elevm, color = 'r', lw = 5, alpha = 0.2)
        plot(dist, elevm, color = 'r', lw = 4, alpha = 0.4)
        plot(dist, elevm, color = 'r', lw = 2.5, alpha = 0.7)
        fill_between(profile[:,0], profile[:,1], color = [0.5, 0.5, 0.5], alpha = 0.5)
        plot(profile[:,0], profile[:,1], color = 'k')
        
        #gcf().suptitle('Snow cover along the JMT deduced from 6/03/16 MODIS satellite imagery\n\n\n\n\n\n', fontsize = 16, fontweight = 'bold')
        grid(axis = 'y')
        title('Using imagery from ' + dateList[j][0:2] + '/' + dateList[j][2:4] + '/' + dateList[j][4::], horizontalalignment='center', fontsize = 14, fontweight = 'bold')
        
        t = text(0.01, 0.97, 'Snow covered sections are highlighted in red.', transform = gca().transAxes, horizontalalignment = 'left', va = 'top', fontsize = 10, fontstyle = 'italic')
        t.set_path_effects([PathEffects.Stroke(linewidth=4, foreground='white', alpha = 0.8), PathEffects.Normal()])
        
        #t = text(0.127, 0.82, 'Current coverage:', transform = gcf().transFigure, horizontalalignment = 'left', va = 'top', fontsize = 14, fontstyle = 'italic')
        #t.set_path_effects([PathEffects.Stroke(linewidth=4, foreground='white', alpha = 0.8), PathEffects.Normal()])
        
        covDist = round(trapz(outi, x = xi), 2)
        covPercent = round(100*covDist/max(dist),1)
        t = text(0.01, 0.9, str(covPercent) + '% (' + str(covDist) + ' of ' + str(round(max(dist),2)) + ' miles)' , transform = gca().transAxes, horizontalalignment = 'left', va = 'top', fontsize = 10, fontstyle = 'italic', fontweight = 'bold', color = 'r')
        t.set_path_effects([PathEffects.Stroke(linewidth=4, foreground='white', alpha = 0.8), PathEffects.Normal()])
    
        opts = array([20, 10, 5, 2, 1, .5, .25, .1])
        this = opts > max(dist)/25.
        xtickspacing = opts[this][-1]
        xticks(arange(0, max(dist)+xtickspacing, xtickspacing))
        axis(xmax = max(dist), xmin = 0, ymin = 1000*int(min(profile[:,1]/1000)), ymax = 1000*ceil(max(profile[:,1]/1000)))
        xlabel('Distance [mi]')
        ylabel('Elevation [ft]')
    saveName = os.path.join(request.folder, 'static', 'snowprofiles', key + '_' + 'snow_profile.png')
    tight_layout()
    savefig(saveName, dpi = 200)
    close('all')
    return dict(key = key)

def kmlmapper():
### Begin script
    key = request.args[0]
    thisRecord = db(db.routes.route_id==key).select().first()
    routeFilename = thisRecord.filename
    #db.routes.insert(route_id = key, filename = routeFilename, name = 'Sierra Mapper Route', routetype = 'Uploaded',author = thisAuthor, orig_filename = routeFilename, inputstring = inputString)

    filename = os.path.join(request.folder, 'uploads', routeFilename)
    tree2 = ET.parse(filename)
    root2 = tree2.getroot()

    markerList = [] # used for custom markers found in kml file

    for i in root2[0]:

        if i.tag == '{http://www.opengis.net/kml/2.2}Placemark':

            k = 3 # index of meat -- changed when CalTopo changed .kml format
            try:
                i[k].tag
            except IndexError:
                k = 2

            if i[k].tag == '{http://www.opengis.net/kml/2.2}Polygon':
                print('A polygon')
                inputCoords = i[k][2][0][0].text.split(',')
                #inputCoords = i[3][2][0][0].text.split(',')

            if i[k].tag == '{http://www.opengis.net/kml/2.2}LineString':
                print('A Linestring')
                inputCoords = i[k][2].text.split(',')
                #inputCoords = i[3][2].text.split(',')

            if i[k].tag == '{http://www.opengis.net/kml/2.2}Point':
                print('A point: ' + i[0].text)
                thisLat = float(i[k][0].text.split(',')[1].strip('0\n'))
                thisLong = float(i[k][0].text.split(',')[0].strip('0\n'))
                #thisLat = float(i[3][0].text.split(',')[1].strip('0\n'))
                #thisLong = float(i[3][0].text.split(',')[0].strip('0\n'))
                thisLake = Lake(i[0].text)
                thisLake.coords = array([thisLong, thisLat])
                thisLake.type = 'Custom'
                markerList.append(thisLake)
    outCoordsArray = zeros(((len(inputCoords)-1)/2, 3))

    for i in range(0, len(outCoordsArray[:,0])):
        outCoordsArray[i,0] = float(inputCoords[2*i].strip('0\n'))
        outCoordsArray[i,1] = float(inputCoords[2*i+1].strip('0\n'))
        outCoordsArray[i,2] = 0

    # try to pass all markers to kmlmapper.html
    filename = os.path.join(request.folder, 'static', 'gr.gpickle')
    gr = nx.read_gpickle(filename)
    #print('loaded nx file')
    nodeCoords = nx.get_node_attributes(gr, 'Coordinates')
    nodeNicknames = nx.get_node_attributes(gr, 'Nicknames')
    nodeMarkerList = []
    for node in list(gr.nodes_iter()):
        nodeMarkerList.append(str(node))
        nodeMarkerList.append(nodeCoords[node][0])
        nodeMarkerList.append(nodeCoords[node][1])

        if len(nodeNicknames[node]) == 0:
            nodeMarkerList.append('Unnamed Jct.')
        else:
            nodeMarkerList.append(nodeNicknames[node][0])
        nodeMarkerList.append(nodeCoords[node][2]) # add elev

    form4 = FORM.confirm('Download Route')
    form5 = FORM.confirm('View at CalTopo.com')
    #form6 = FORM.confirm('Edit this Route')
    form7 = FORM.confirm('Download Data Table')
    form8 = FORM.confirm('Download Elevation Data')
    form9 = FORM.confirm('Snow?!?')
    
    textProfileFilename = os.path.join(request.folder, 'static/textprofiles', key + '.txt')
    profileDataFileName = os.path.join(request.folder, 'static/dataprofiles', key + '_profile_data.txt')


    if form4.process(formname='form_four').accepted:
        response.stream(routeFilename,attachment=True,chunk_size=4096, filename = 'route.kml')

    if form5.process(formname='form_five').accepted:
        redirect('http://www.caltopo.com#kml=http://awhite4777.pythonanywhere.com/SierraMapperAlpha/uploads/'+routeFilename)
    
    if form7.process(formname='form_seven').accepted:
        response.stream(textProfileFilename,attachment=True,chunk_size=4096, filename = key + '_Table.csv')    
        
    if form8.process(formname='form_eight').accepted:
        response.stream(profileDataFileName,attachment=True,chunk_size=4096, filename = key + '_Profile.txt')
    if form9.process(formname='form_nine').accepted:
        # Call snow with the key
        redirect('http://awhite4777.pythonanywhere.com/SierraMapperAlpha/default/snow/' + key)
    return dict(form4 = form4, form5 = form5, form7 = form7, form8 = form8, form9 = form9, outCoords=json.dumps(outCoordsArray.tolist()), nodeMarkers=json.dumps(nodeMarkerList), key = key)
    # End of KML mapper!

    
def mapper():
    #request.folder = 'https://awhite4777.pythonanywhere.com/SierraMapperAlpha'
    def calcDist(coordArray):
    # Calculate distance in miles for a given Lat/Long array
    # Call with array of floats, return float
        totalDist = 0.
        rEarth = 3963.1676#  in miles
        for i in range(1, len(coordArray[:,0])):
            lat1 = coordArray[i-1,1]*(npy.pi/180.)
            lat2 = coordArray[i,1]*(npy.pi/180.)
            dLat =  lat2 - lat1
            dLong = (coordArray[i,0] - coordArray[i-1,0])*npy.pi/180.
            thisDist = 1.03*(2*rEarth*npy.arcsin(npy.sqrt( (npy.sin(dLat/2.))**2 + npy.cos(lat1)*npy.cos(lat2)*(npy.sin(dLong/2)**2))))
            totalDist = totalDist + thisDist

        return totalDist

    def calcDist2(pos1, pos2):
    # Calculate distance between in long lat format
        totalDist = 0.
        rEarth = 3963.1676#  in miles

        lat1 = pos1[1]*(npy.pi/180.)
        lat2 = pos2[1]*(npy.pi/180.)
        dLat =  lat2 - lat1
        dLong = (pos1[0] - pos2[0])*npy.pi/180.
        thisDist = 1.03*(2*rEarth*npy.arcsin(npy.sqrt( (npy.sin(dLat/2.))**2 + npy.cos(lat1)*npy.cos(lat2)*(npy.sin(dLong/2)**2))))
        totalDist = totalDist + thisDist

        return totalDist

    def calcRoute(n1, n2): # function used to generate display routes--call with two nodes 'n001' and 'n008', e.g., and it will save a file 'n001_n008.csv'
        outCoordsList = []
        thisPath = nx.dijkstra_path(gr, n1, n2, 'weight')
        thisPathLength = nx.dijkstra_path_length(gr, n1, n2, 'weight')
        #print(thisPath)
        for j in range(0, len(thisPath) - 1):
            node1 = thisPath[j]
            node2 = thisPath[j+1]
            if gr.node[node1]['id'] < gr.node[node2]['id']: # Good
                outCoordsList.append(gr.edge[node1][node2]['Coordinates'])
            if gr.node[node1]['id'] > gr.node[node2]['id']: # Flip 'er over
                outCoordsList.append(flipud(gr.edge[node1][node2]['Coordinates']))

        # Covert outCoordsList to array
        numCoords = 0
        for i in range(0,len(outCoordsList)):
            numCoords = numCoords + size(outCoordsList[i][:,0])
            #print(numCoords)

        outCoordsArray = zeros((numCoords,3))

        startRow = 0
        for i in range(0, len(outCoordsList)):
            thisEndRow = startRow + size(outCoordsList[i][:,0])
            outCoordsArray[startRow:thisEndRow,:] = outCoordsList[i]
            startRow = thisEndRow
        if thisPath[0] > thisPath[-1]:
            outCoordsArray = flipud(outCoordsArray)
        displayRouteString = str(round(thisPathLength,2)) + ',' + str(round(outCoordsArray[0,1],5))+ ',' +str(round(outCoordsArray[0,0],5)) + ','
        lastPoint = outCoordsArray[0,:]
        for i in range(0, len(outCoordsArray)):
            if calcDist2(lastPoint, outCoordsArray[i,:]) > 0.05 or i == len(outCoordsArray-1):
                displayRouteString = displayRouteString + str(round(outCoordsArray[i,1],5))+ ',' +str(round(outCoordsArray[i,0],5)) + ','
                lastPoint = outCoordsArray[i,:]
        displayRouteString = displayRouteString[:-1]
        thisRoute = min(n1,n2) + '_' + max(n1,n2)+ '.csv'
        filename = os.path.join(request.folder, 'static/displayRoutes', thisRoute)
        f = open(filename,'w')
        f.write(displayRouteString)
        f.close()

    def readXC(thisHash):
        thisFile = thisHash[1:4] + '.txt'
        filename = os.path.join(request.folder, 'uploads/XC', thisFile)
        f = open(filename,'rb')
        b = f.readlines()[0].replace(' ','').replace('(','').split(')')
        c, d  = [], []

        for i in b:
            c.append(i.split(','))
        c.pop() # get ride of /n

        for i in c:
            i[0] = float(i[0])
            i[1] = float(i[1])
            i[2] = float(i[2])
        c.sort()
        g = len(c)-1
        i = 0
        while i < len(c)-1:
            noChange = 1
            thisLoc = array([c[i][2], c[i][1]])
            nextLoc = array([c[i+1][2], c[i+1][1]])
            if calcDist2(thisLoc, nextLoc) > 0.03:
                c.insert(i+1, [(c[i][0]+c[i+1][0])/2, 0.5*(c[i][1]+c[i+1][1]), 0.5*(c[i][2]+c[i+1][2])])
                noChange = 0
            if noChange:
                i = i + 1

        d = zeros((len(c)-1,3))

        for i in range(0, len(d)):
            d[i,0] = c[i][0]
            d[i,1] = c[i][1]
            d[i,2] = c[i][2]

        e = zeros((len(d),3))
        e[:,0] = d[:,2]
        e[:,1] = d[:,1]

        return e

    def returnCoordinates(inputList): # call with list ['n001','xsdf','n010'] and return an array of the coordinates of the route
        outList = []

        # insert fake nodes if route starts or ends XC

        if inputList[0][0] == 'x':
            inputList.insert(0, 'z000')
        if inputList[-1][0] == 'x':
            inputList.insert(len(inputList), 'z000')

        i = 1
        indexList = [] # where to insert x's
        for i in range(0, len(inputList)-1):
            if inputList[i][0] != 'x' and inputList[i+1][0] != 'x':
                #inputList.insert(i+1, 'x')
                indexList.append(i+1)
        counter = 0
        for i in range(0, len(indexList)):
            inputList.insert(indexList[i]+counter, 'x')
            counter = counter + 1
        for i in range(1, len(inputList),2):
            if inputList[i] == 'x':
                outList.append(['Trail',inputList[i-1],inputList[i+1]])
            else:
                outList.append(['XC',inputList[i][0:4]])

        outCoordsList = []
        for i in outList:
            if i[0] == 'Trail':
                outCoordsList.append(calcRoute2(i[1],i[2]))
            if i[0] == 'XC':
                outCoordsList.append(readXC(i[1]))


        numCoords = 0
        for i in range(0,len(outCoordsList)):
            numCoords = numCoords + npy.size(outCoordsList[i][:,0])

        outCoordsArray = npy.zeros((numCoords,3))

        startRow = 0
        for i in range(0, len(outCoordsList)):
            thisEndRow = startRow + npy.size(outCoordsList[i][:,0])
            outCoordsArray[startRow:thisEndRow,:] = outCoordsList[i]
            startRow = thisEndRow

        return outCoordsArray

    def calcRoute2(n1, n2): #calculates route and returns array
        outCoordsList = []
        thisPath = nx.dijkstra_path(gr, n1, n2, 'weight')
        thisPathLength = nx.dijkstra_path_length(gr, n1, n2, 'weight')
        #print(thisPath)
        for j in range(0, len(thisPath) - 1):
            node1 = thisPath[j]
            node2 = thisPath[j+1]
            if gr.node[node1]['id'] < gr.node[node2]['id']: # Good
                outCoordsList.append(gr.edge[node1][node2]['Coordinates'])
            if gr.node[node1]['id'] > gr.node[node2]['id']: # Flip 'er over
                outCoordsList.append(flipud(gr.edge[node1][node2]['Coordinates']))

        # Covert outCoordsList to array
        numCoords = 0
        for i in range(0,len(outCoordsList)):
            numCoords = numCoords + size(outCoordsList[i][:,0])
            #print(numCoords)

        outCoordsArray = zeros((numCoords,3))

        startRow = 0
        for i in range(0, len(outCoordsList)):
            thisEndRow = startRow + size(outCoordsList[i][:,0])
            outCoordsArray[startRow:thisEndRow,:] = outCoordsList[i]
            startRow = thisEndRow

        return outCoordsArray
    ### Begin scripts
    inputList = []
    for i in request.args:
        inputList.append(i)

    # Test to see if we need to generate the profile and route
    inputString = ''
    for i in range(0, len(inputList)):
        inputString= inputString + inputList[i]
    #profileString = inputString + '_profile.png'
    generate = 1    # key to determine if profile/route files should be generated and saved

    key = ''
    for i in range(6):
        key += random2.choice(string.lowercase  + string.uppercase) #string.uppercase

    try:
        thisAuthor = auth.user.username
    except AttributeError:
        thisAuthor = 'Anonymous'

    if db(db.routes.inputstring == inputString).isempty():
    #if True: # using this to force generation always
        profileString = key + '_profile.png'
        routeString = key + '_route.kml'
        profileFilename = os.path.join(request.folder, 'static/profiles', profileString)
        routeFilename = os.path.join(request.folder, 'static/routes', routeString)
        textProfileFilename = os.path.join(request.folder, 'static/textprofiles', key + '.txt')
        profileDataFileName = os.path.join(request.folder, 'static/dataprofiles', key + '_profile_data.csv')
        db.routes.insert(route_id = key, filename = routeFilename, name = '', routetype = 'Sierra Mapper',author = thisAuthor, orig_filename = routeFilename, inputstring = inputString)
        generate = 1
        #db.routes.insert(route_id = key, filename = routeFilename, name = 'Sierra Mapper Route', routetype = 'Uploaded',author = thisAuthor, orig_filename = routeFilename)
    else:
        key = db(db.routes.inputstring==inputString).select().first().route_id
        generate = 0
        profileString = key + '_profile.png'
        routeString = key + '_route.kml'
        profileFilename = os.path.join(request.folder, 'static/profiles', profileString)
        routeFilename = os.path.join(request.folder, 'static/routes', routeString)
        textProfileFilename = os.path.join(request.folder, 'static/textprofiles', key + '.txt')
        profileDataFileName = os.path.join(request.folder, 'static/dataprofiles', key + '_profile_data.csv')
    #db.routes.insert(route_id = key, filename = routeFilename, name = 'Sierra Mapper Route', routetype = 'Uploaded',author = thisAuthor, orig_filename = routeFilename, inputstring = inputString)


    filename = os.path.join(request.folder, 'static', 'gr.gpickle')
    gr = nx.read_gpickle(filename)

    # generate display routes. Throw out cross country routes ('xYYY'). Also collect segments for which cross-country routes are needed
    displayRoutesList = []


    for i in range(0, len(inputList)):
        if inputList[i][0] == 'x':
            pass
        else:
            displayRoutesList.append(inputList[i])
    """
    for i in range(0, len(displayRoutesList)-1):
        if displayRoutesList[i] != displayRoutesList[i+1]:
            calcRoute(displayRoutesList[i], displayRoutesList[i+1])
    """
    nodesToVisitList = []
    for i in range(0, len(inputList)):
        inStr = inputList[i]
        if inStr in list(gr.nodes_iter()):
            nodesToVisitList.append(inStr)
        else:
            print('Node not recognized: '+ inStr)



    outCoordsArray = returnCoordinates(inputList)

    CoordsString = ''
    displayRouteString = str(outCoordsArray[0,1])+ ',' +str(outCoordsArray[0,0]) + ','
    lastPoint = outCoordsArray[0,:]

    for i in range(0, len(outCoordsArray)):
        CoordsString = CoordsString + str(outCoordsArray[i,0])+ ',' +str(outCoordsArray[i,1]) + ',0\n'

    #filename = os.path.join('https://awhite4777.pythonanywhere.com/SierraMapperAlpha', 'static', 'blank_edge.kml')
    filename = os.path.join(request.folder, 'static', 'blank_edge.kml')
    tree2 = ET.parse(filename)
    root2 = tree2.getroot()

    #name = str(raw_input('Enter a name for the route: '))
    root2[0][1].text = 'Another Excellent Route by Adam!'
    root2[0][0].text = 'Temporary Title'
    root2[0][2][1].text = 'Custom Route'
    root2[0][2][2][2].text = CoordsString


    routeList = []
    for i in inputList:
        if i[0] != 'x' and i[0] != 'z':
            try:
                routeList.append(gr.node[i]['Nicknames'][0])
            except IndexError:
                routeList.append('Unnamed Jct.')

    # Generate a list to pass for the start, via, stop markers to mapper.html
    inputMarkerList = []
    for i in inputList:
        if i[0] != 'x'and i[0] != 'z':
            inputMarkerList.append(i)
            inputMarkerList.append(gr.node[i]['Coordinates'][0])
            inputMarkerList.append(gr.node[i]['Coordinates'][1])

    # try to pass all markers to mapper.html
    nodeCoords = nx.get_node_attributes(gr, 'Coordinates')
    nodeNicknames = nx.get_node_attributes(gr, 'Nicknames')
    nodeMarkerList = []
    for node in list(gr.nodes_iter()):
        nodeMarkerList.append(str(node))
        nodeMarkerList.append(nodeCoords[node][0])
        nodeMarkerList.append(nodeCoords[node][1])

        if len(nodeNicknames[node]) == 0:
            nodeMarkerList.append('Unnamed Jct.')
        else:
            nodeMarkerList.append(nodeNicknames[node][0])
        nodeMarkerList.append(nodeCoords[node][2]) # add elev


    if generate:
        routeFilename = os.path.join(request.folder, 'static/routes', routeString)
        tree2.write(routeFilename)
        createProfile(key, routeFilename)


    form4 = FORM.confirm('Download Route')
    form5 = FORM.confirm('View at CalTopo.com')
    form6 = FORM.confirm('Edit this Route')
    form7 = FORM.confirm('Download Data Table')
    form8 = FORM.confirm('Download Elevation Data')
    form9 = FORM.confirm('Snow?!?')

    if form4.process(formname='form_four').accepted:
        response.stream(routeFilename,attachment=True,chunk_size=4096, filename = 'route.kml')

    if form5.process(formname='form_five').accepted:
        redirect('http://www.caltopo.com#kml=http://awhite4777.pythonanywhere.com/SierraMapperAlpha/static/routes/'+routeString)


    if form6.process(formname='form_six').accepted:
        outputList = request.args
        # Test to see if we need to generate the profile and route
        outputString = '/'
        for i in range(0, len(outputList)):
            outputString= outputString + outputList[i] + '/'
        redirect('http://awhite4777.pythonanywhere.com/SierraMapperAlpha/default/start/' + '#' + outputString)

    if form7.process(formname='form_seven').accepted:
        response.stream(textProfileFilename,attachment=True,chunk_size=4096, filename = key + '_Table.csv')    
        
    if form8.process(formname='form_eight').accepted:
        response.stream(profileDataFileName,attachment=True,chunk_size=4096, filename = key + '_Profile.csv')
    if form9.process(formname='form_nine').accepted:
        # Call snow with the key
        redirect('http://awhite4777.pythonanywhere.com/SierraMapperAlpha/default/snow/' + key)
    return dict(form4 = form4, form5 = form5, form6 = form6, form7 = form7, form8 = form8, form9 = form9, outCoords=json.dumps(outCoordsArray.tolist()), routeDescription=routeList, inputList=json.dumps(inputMarkerList), nodeMarkers=json.dumps(nodeMarkerList), key = key)

# nodeMarkers is list of all nodes
########

def index():
    return dict()

def node_input2():
    b = 12
    return dict(b=b)

class Lake:
    def __init__(self, name):
        self.name = name

def calcDist(coordArray):
    # Calculate distance in miles for a given Lat/Long array
    # Call with array of floats, return float
    totalDist = 0.
    rEarth = 3963.1676#  in miles
    for i in range(1, len(coordArray[:,0])):
        lat1 = coordArray[i-1,1]*(pi/180.)
        lat2 = coordArray[i,1]*(pi/180.)
        dLat =  lat2 - lat1
        dLong = (coordArray[i,0] - coordArray[i-1,0])*pi/180.
        thisDist = 1.03*2*rEarth*arcsin(sqrt( (sin(dLat/2.))**2 + cos(lat1)*cos(lat2)*(sin(dLong/2)**2)))
        totalDist = totalDist + thisDist

    return totalDist

def calcDist2(pos1, pos2):
    # Calculate distance between in long lat format
    rEarth = 3963.1676#  in miles

    lat1 = pos1[1]*(pi/180.)
    lat2 = pos2[1]*(pi/180.)
    dLat =  lat2 - lat1
    dLong = (pos1[0] - pos2[0])*pi/180.
    thisDist = (2*rEarth*arcsin(sqrt( (sin(dLat/2.))**2 + cos(lat1)*cos(lat2)*(sin(dLong/2)**2))))
    return thisDist

def calcDist3(pos1, pos2):
    return (pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2

def calcElev(point, geo):
    t1 = time.time()
    thisLat = point[1]
    thisLong = point[0]
    upperLat = int(point[1])+1
    upperLong = int(abs(point[0]))+1

    P = linspace(0,10811,10812) # pixels

    tf = geo.GetGeoTransform()
    latmin = tf[3]+tf[5]*10811
    latmax = tf[3]#+tf[5]*min(P)
    lonmax = tf[0]+tf[1]*10811
    lonmin = tf[0]#+tf[1]*min(P)
    px = (thisLong-lonmin)/tf[1]
    py = (thisLat-latmin)/abs(tf[5])
    x1 = int(max(0, (px - 20)))
    x2 = int(min(10811, (px + 20)))
    y1 = int(max(0, (py - 20)))
    y2 = int(min(10811, (py + 20)))
    arr = 3.28084*flipud(geo.ReadAsArray(xoff = x1, yoff = 10811 - y1-(y2-y1), xsize = x2 - x1, ysize = y2 - y1))
    thisElev = ndimage.map_coordinates(arr, [[py-max(y1,0)], [px-max(x1,0)]], order=3)[0]
    return thisElev

class Point:
    def __init__(self, name):
        self.name = name

def plotShape(shape):
    figure()
    for i in range(0, len(shape.points)):
        plot(shape.points[i][0], shape.points[i][1], 'bo')
    show()

def isNear(lake, point, tol):
    if (point[0] > lake.extents[0] - tol) and (point[0] < lake.extents[1] + tol):
        if (point[1] > lake.extents[2] - tol) and (point[1] < lake.extents[3] + tol):
            #print('you might be near ' + lake.name)
            return True

def isNearLoc(lake, routeExtents, tol):
    if (lake.coords[0] > routeExtents[0] - tol) and (lake.coords[0] < routeExtents[1] + tol):
        if (lake.coords[1] > routeExtents[2] - tol) and (lake.coords[1] < routeExtents[3] + tol):
            #print('you might be near ' + lake.name)
            return True

def minDist(lake, point):
    minDistance = 1e9
    for i in range(0, len(lake.coords),16):
        thisDist = calcDist3(lake.coords[i,:], point)
        if thisDist < minDistance:
            minDistance = thisDist
    return minDistance

def intersects(A, B, C, D):
    # line segment A-B, C-D
    def ccw(A, B, C):
        return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def getBounds(point):
    # call with outCoordsArray row, return nw corner of 0.5 degree quad
    wBound = str(int(10*abs(int(point[0]*2)/2.)+5))
    nBound = str(int(10*abs(int(point[1]*2)/2.)+5))
    return('n'+nBound+'w'+wBound)

def overlaps(lake, routeExtents, tol):
    if (routeExtents[0]-tol <= lake.extents[0] <= routeExtents[1]+tol) or (routeExtents[0]-tol <= lake.extents[1] <= routeExtents[1]+tol):
        if (routeExtents[3]+tol >= lake.extents[2] >= routeExtents[2]-tol) or (routeExtents[3]+tol >= lake.extents[3] >= routeExtents[2]-tol):
            #print('Bounding boxes overlap')
            return True

def createProfile(key, filename):
    def runLocations(shapes=[], records=[], tol=.001, lakeList = []):
        routeExtents = array([min(outCoordsArray[:,0]), max(outCoordsArray[:,0]), min(outCoordsArray[:,1]), max(outCoordsArray[:,1])])
        t1 = time.time()
        if len(lakeList) == 0:
            for i in range(0, len(shapes)):
                thisLake = Lake(records[i][0])
                thisLake.coords = shapes[i].points[0]
                if isNearLoc(thisLake, routeExtents, tol = 0.001):
                    thisLake.type = records[i][1]
                    lakeList.append(thisLake)
        t2 = time.time()
        print('=== ' + str(t2-t1) + ' seconds elapsed for location parsing')
        for lake in lakeList:
            labelCounter = 0
            updated = 0
            thisLabel = lake.name
            thisMinDist = 1e9
            if labelDict.has_key(thisLabel):
                pass
            else:
                i = 0
                #for i in range(0,len(outCoordsArray),1):
                while i < len(outCoordsArray):
                    if abs(lake.coords[0] - outCoordsArray[i,0]) < tol and abs(lake.coords[1] - outCoordsArray[i,1]) < tol:
                        thisDist = calcDist3(lake.coords, outCoordsArray[i,:])
                        if thisDist < thisMinDist:
                            thisMinDist = thisDist
                            if labelCounter == 0:
                                labelDict.update({thisLabel:str(i)})
                                labelTypeDict.update({thisLabel:lake.type})

                            else:
                                newLabel = thisLabel + '~'
                                labelDict.update({newLabel:str(i)})
                                labelTypeDict.update({thisLabel:lake.type})
                            updated = 1
                        i = i + 1
                    else:
                        if updated:
                            labelCounter = labelCounter + 1
                            updated = 0
                        thisMinDist = 1e9
                        thisDist = calcDist3(lake.coords, outCoordsArray[i,:]) # looks like dist**2 in degrees
                        i = i + max(1,int(2000*sqrt(thisDist)))
        t3 = time.time()
        print(' == ' + str(t3-t2) + ' seconds elapsed for locations')
        ### Done with RunLocations()

    def runLakes(shapes, records, tol, body):
        t1 = time.time()
        lakeList = []
        routeExtents = array([min(outCoordsArray[:,0]), max(outCoordsArray[:,0]), min(outCoordsArray[:,1]), max(outCoordsArray[:,1])])
        for i in range(0, len(shapes)):
            if records[i][4][0] == ' ':
                thisName = 'Unnamed'
            else:
                thisName = records[i][4]

            thisLake = Lake(thisName)
            if body == 'lake':
                thisLake.type = records[i][8]
            if body == 'stream':
                thisLake.type = records[i][9]
                if records[i][10] == 46003: #intermittent
                    thisLake.name = thisLake.name + ' (intermittent)'

            thisLake.coords = zeros((len(shapes[i].points),2))
            for j in range(0, len(shapes[i].points)):
                thisLake.coords[j,:] = shapes[i].points[j]
            thisLake.extents = [min(thisLake.coords[:,0]), max(thisLake.coords[:,0]), min(thisLake.coords[:,1]), max(thisLake.coords[:,1])]
            if overlaps(thisLake, routeExtents,.001):
                lakeList.append(thisLake)

        t2 = time.time()
        print('== ' + str(t2-t1) + ' seconds elapsed for parsing')
        if body == 'lake':
            print('=== Running lake')
            for lake in lakeList:
                labelCounter = 0
                updated = 0
                thisLabel = lake.name

                if thisLabel == 'Unnamed':
                    thisLabel = 'Unnamed Lake/Pond'

                while labelDict.has_key(thisLabel):
                    thisLabel = thisLabel + '~'

                thisMinDist = 1e9
                i = 0
                while i < len(outCoordsArray):
                    if isNear(lake, outCoordsArray[i,:], tol):
                        thisDist = minDist(lake, outCoordsArray[i,:])
                        if thisDist < thisMinDist:
                            thisMinDist = thisDist
                            if labelCounter == 0:
                                labelDict.update({thisLabel:str(i)})
                                labelTypeDict.update({thisLabel:lake.type})

                            else:
                                labelDict.update({thisLabel:str(i)})
                                labelTypeDict.update({thisLabel:lake.type})
                            updated = 1
                        i = i + 1
                    else: # if not near
                        if updated: # but you WERE near
                            labelCounter = labelCounter + 1
                            thisLabel = thisLabel + '~'
                            updated = 0
                        thisDist = minDist(lake, outCoordsArray[i,:]) # looks like dist**2 in degrees
                        i = i + max(1,int(1e3*sqrt(thisDist)))
                        #print(thisLabel + ', '+ str(1e3*thisDist))
                        thisMinDist = 1e9 # reset minDist
        t3 = time.time()
        print(' == ' + str(t3 - t2) + ' seconds elapsed for Lakes <------')
        if body == 'stream':
            print('=== Running stream ===')
            for lake in lakeList:
                labelCounter = 0
                updated = 0
                thisLabel = lake.name + ' Crossing'
                while labelDict.has_key(thisLabel):
                    thisLabel = thisLabel + '~'
                thisMinDist = 1e9
                i = 0
                if lake.type != 'ArtificialPath':
                    #for i in range(0,len(outCoordsArray)-1,1):
                    while i < len(outCoordsArray)-1:
                        if isNear(lake, outCoordsArray[i,:], tol):
                            for j in range(0, len(lake.coords)-1,1):
                                if intersects(outCoordsArray[i,:], outCoordsArray[i+1,:], lake.coords[j,:], lake.coords[j+1,:]):
                                    if labelCounter == 0:
                                        labelDict.update({thisLabel:str(i)})
                                        labelTypeDict.update({thisLabel:lake.type})

                                    else:
                                        thisLabel = thisLabel + '~'
                                        labelDict.update({thisLabel:str(i)})
                                        labelTypeDict.update({thisLabel:lake.type})
                                    updated = 1
                            i = i + 1
                        else:
                            if updated:
                                labelCounter = labelCounter + 1
                                updated = 0
                            thisDist = minDist(lake, outCoordsArray[i,:]) # looks like dist**2 in degrees
                            i = i + max(1,int(1000*sqrt(thisDist)))
                            thisMinDist = 1e9
        t4 = time.time()
        print(' == ' + str(t4 - t3) + ' seconds elapsed for Streams')
    ### End of function

    # Start of script

    thisDBEntry = db((db.routes.filename == filename)&
            (db.routes.route_id==key)).select().first()
    if thisDBEntry.routetype == 'Uploaded':
        thisFile = os.path.join(request.folder, 'uploads', filename)
    else:
        thisFile = os.path.join(request.folder, 'static/routes', filename)

    ##################
    t0 = time.time()
    blue = [0, 0, 1]
    red = [1, 0, 0]
    black = [0, 0, 0]
    purple = [1, 0, 1]
    green = [0, 1, 0]
    yellow = [.7, .7, 0]

    colorDict = ({  'Lake':blue,
                    'LakePond':blue,
                    'SwampMarsh':blue,
                    'Ice Mass':blue,
                    'Reservoir':blue,
                    'Stream':blue,
                    'StreamRiver':blue,
                    'Falls':blue,
                    'Glacier':blue,
                    'Spring':blue,
                    'Crossing':blue,
                    'Cliff':red,
                    'Gap':red,
                    'Pass':red,
                    'Summit':red,
                    'Ridge':red,
                    'Peak':red,
                    'Pillar':red,
                    'Range':red,
                    'Valley':green,
                    'Canyon':green,
                    'Crater':green,
                    'Flat':green,
                    'Plain':green,
                    'Meadow':green,
                    'Basin':green,
                    'Island':green,
                    'Connector':yellow,
                    'Reserve':yellow,
                    'Locale':yellow,
                    'Building':yellow,
                    'Park':yellow,
                    'Tunnel':yellow,
                    'Mine':yellow,
                    'Trail':yellow,
                    'Populated Place':yellow,
                    'Bridge':yellow,
                    'Dam':yellow,
                    'Custom':red
                    })
    colorDict = ({  'Lake':True,
                    'LakePond':True,
                    'SwampMarsh':True,
                    'Ice Mass':True,
                    'Reservoir':True,
                    'Stream':True,
                    'StreamRiver':True,
                    'Falls':True,
                    'Glacier':True,
                    'Spring':True,
                    'Crossing':True,
                    'Cliff':False,
                    'Gap':False,
                    'Pass':False,
                    'Summit':False,
                    'Ridge':False,
                    'Peak':False,
                    'Pillar':False,
                    'Range':False,
                    'Valley':False,
                    'Canyon':False,
                    'Crater':False,
                    'Flat':False,
                    'Plain':False,
                    'Meadow':False,
                    'Basin':False,
                    'Island':False,
                    'Connector':False,
                    'Reserve':False,
                    'Locale':False,
                    'Building':False,
                    'Park':False,
                    'Tunnel':False,
                    'Mine':False,
                    'Trail':False,
                    'Populated Place':False,
                    'Bridge':False,
                    'Dam':False,
                    'Census':False,
                    'Custom':False,
                    'Post Office':False,
                    'Slope':False
                    })

    tree2 = ET.parse(thisFile)
    root2 = tree2.getroot()
    markerList = [] # used for custom markers found in kml file

    for i in root2[0]:
        if i.tag == '{http://www.opengis.net/kml/2.2}Placemark':
            k = 3 # index of meat -- changed when CalTopo changed .kml format
            try:
                i[k].tag
            except IndexError:
                k = 2

            if i[k].tag == '{http://www.opengis.net/kml/2.2}Polygon':
                print('A polygon')
                #inputCoords = i[2][2][0][0].text.split(',')
                inputCoords = i[k][2][0][0].text.split(',')

            if i[k].tag == '{http://www.opengis.net/kml/2.2}LineString':
                print('A Linestring')
                inputCoords = i[k][2].text.split(',')
                #inputCoords = i[3][2].text.split(',')


            if i[k].tag == '{http://www.opengis.net/kml/2.2}Point':
                print('A point: ' + i[0].text)
                thisLat = float(i[k][0].text.split(',')[1].strip('0\n'))
                thisLong = float(i[k][0].text.split(',')[0].strip('0\n'))
                #thisLat = float(i[3][0].text.split(',')[1].strip('0\n'))
                #thisLong = float(i[3][0].text.split(',')[0].strip('0\n'))
                thisLake = Lake(i[0].text)
                thisLake.coords = array([thisLong, thisLat])
                thisLake.type = 'Custom'
                markerList.append(thisLake)
    outCoordsArray = zeros(((len(inputCoords)-1)/2, 2))

    for i in range(0, len(outCoordsArray[:,0])):
        outCoordsArray[i,0] = float(inputCoords[2*i].strip('0\n'))
        outCoordsArray[i,1] = float(inputCoords[2*i+1].strip('0\n'))

    # Create map list
    mapList = []
    for i in range(0, len(outCoordsArray)):
        if getBounds(outCoordsArray[i,:]) not in mapList:
            mapList.append(getBounds(outCoordsArray[i,:]))

    labelDict = {}
    labelTypeDict = {}
    elevArray = zeros(len(outCoordsArray))
    t1 = time.time()
    topoDict = {}

    for i in range(0,len(outCoordsArray)):
        upperLat = int(outCoordsArray[i,1])+1
        upperLong = int(abs(outCoordsArray[i,0]))+1
        thisString = 'n' + str(upperLat) + 'w' + str(upperLong)
        #print('right before gdal, ' + thisString + ', ' + os.getcwd())
        if topoDict.has_key(thisString):
            pass
        else:
            # https://awhite4777.pythonanywhere.com
            topoDict.update({thisString: gdal.Open('/home/awhite4777/data/NED/img' + thisString + '_13.img')})
        #print('right after gdal; topodict = '); print(topoDict)
        elevArray[i] = calcElev(outCoordsArray[i,:], topoDict[thisString])

    print(str(time.time()-t1))
    cumDistance = npy.zeros(len(outCoordsArray[:,0]))
    cumClimbing = npy.zeros(len(outCoordsArray[:,0]))
    cumDescent = npy.zeros(len(outCoordsArray[:,0]))
    terrDist = npy.zeros(len(outCoordsArray[:,0]))
        # Calculate distances
    for i in range(1, len(outCoordsArray)):
        cumDistance[i] = cumDistance[i-1] + calcDist(outCoordsArray[i-1:i+1,0:2])
        cumClimbing[i] = cumClimbing[i-1] + max(0, elevArray[i] - elevArray[i-1])
        cumDescent[i] = cumDescent[i-1] + max(0, elevArray[i-1] - elevArray[i])
        terrDist[i] = terrDist[i-1] + npy.sqrt(calcDist(outCoordsArray[i-1:i+1,0:2])**2 + ((elevArray[i]-elevArray[i-1])/5280.)**2)

    # parse all data
    for i in mapList:
        sf = shapefile.Reader('/home/awhite4777/data/NHD/' + i + "/hydrography/NHDWaterbody.shp")
        runLakes(sf.shapes(), sf.records(), .001, 'lake')
        sf = shapefile.Reader('/home/awhite4777/data/NHD/' + i + "/hydrography/NHDFlowlineSlim.shp")
        runLakes(sf.shapes(), sf.records(), .002, 'stream')
        sf = shapefile.Reader('/home/awhite4777/data/LOC/' + i + '.shp')
        runLocations(shapes = sf.shapes(), records = sf.records(), tol = .0015, lakeList = []) # USGS location shapes
        sf = shapefile.Reader('/home/awhite4777/data/LOCSM/' + i + '.shp')
        runLocations(shapes = sf.shapes(), records = sf.records(), tol = .0015, lakeList = []) # Sierra Mapper shapes
        runLocations(lakeList = markerList) # any markers from the kml file




    #print('got here')
    # Interpolate and filter
    newDist = linspace(0, max(cumDistance), max(cumDistance)/.02)
    elevationInterp = interp(newDist, cumDistance, elevArray)
    #[b,a] = butter(5,.5) cuz it's broken
    b = array([ 0.0527864 ,  0.26393202,  0.52786405,  0.52786405,  0.26393202, 0.0527864 ])
    a = array([1.00000000e+00,  -3.75069963e-16,   6.33436854e-01, 1.87534981e-16,   5.57280900e-02,  -9.37674907e-17])
    ef = filtfilt(b,a,elevationInterp)
    tempElev = interp(cumDistance, newDist, ef) # use for calculating climbing, descent, etc
    #print('got here2')
    # Calculate cumuative amounts with filtering
    for i in range(1, len(outCoordsArray)):
        cumClimbing[i] = cumClimbing[i-1] + max(0, tempElev[i] - tempElev[i - 1])
        cumDescent[i] = cumDescent[i-1] + max(0, tempElev[i-1] - tempElev[i])
        terrDist[i] = terrDist[i-1] + npy.sqrt(calcDist(outCoordsArray[i-1:i+1,0:2])**2 + ((tempElev[i]-tempElev[i-1])/5280.)**2)


    # update database
    thisDBEntry.update_record(
                lineardistance = round(max(cumDistance),1),
                terraindistance = round(max(terrDist),1),
                ascent = round(max(cumClimbing),1),
                descent = round(max(cumDescent),1),
                created = str(datetime.datetime.now()).split('.')[0])
    # Need to create nodesIndex and labelList because dict labelDict can be called with iterater int (as is done ~8 lines below)
    nodesIndex = []
    labelList = []

    for i in labelDict:
        labelList.append(i)
        nodesIndex.append(int(labelDict[i]))

    # derive routestring for database
    routeStringList = []
    for i in labelList:
        if i.strip('~') in routeStringList or i[0:7] == 'Unnamed':
            pass
        else:
            routeStringList.append(i.strip('~'))
    #print(routeStringList)
    thisDBEntry.update_record(
                    routestring = str(routeStringList))

    nodeLabelsList = []
    # add start and finish labels
    nodeLabelsList.append([0, 0-1e-16, elevArray[0], 'Route Start', True, 'Locale', ['0.00'], [str(round(elevArray[0]))]])
    for i in range(0, npy.size(nodesIndex)):
        # index of label, distance of label, elevation of label, label itself, whether or not to display, label type, list for distances, list for elevations
        nodeLabelsList.append([ int(nodesIndex[i]), cumDistance[nodesIndex[i]], elevArray[nodesIndex[i]], labelList[i], True, labelTypeDict[labelList[i].strip('~')],  [str(.01*round(100*cumDistance[nodesIndex[i]]))], [str(round(elevArray[nodesIndex[i]]))] ])

    nodeLabelsList.sort()
    nodeLabelsList.append([ len(cumDistance)-1, cumDistance[-1], elevArray[-1], 'Route Finish', True, 'Locale',  [str(.01*round(100*cumDistance[-1]))], [str(round(elevArray[-1]))] ])

    if len(nodeLabelsList) > 0:
        thisDBEntry.update_record(
                    startlocation = nodeLabelsList[0][3].strip('~'),
                    endlocation = nodeLabelsList[-1][3].strip('~'))
    else:
        thisDBEntry.update_record(
                startlocation = 'unknown',
                endlocation = 'unknown')

    tooClose = min(max(cumDistance)/30.,1)
    for i in range(0, len(nodeLabelsList)-2): # should it be -1? if I'm not combining final node labels, this is probably the problem
        thisDist = abs(nodeLabelsList[i][1] - nodeLabelsList[i+1][1])
        keepGoing = True
        j = 0
        combine = 0
        while keepGoing:
            if abs(nodeLabelsList[i][1] - nodeLabelsList[i+j+1][1]) < tooClose and nodeLabelsList[i][3].strip('~') == nodeLabelsList[i+1+j][3].strip('~'):
                j = j + 1
                combine = 1
                if len(nodeLabelsList) < i + j + 2:
                    keepGoing = False
            else:
                keepGoing = False
        if combine:
            #if nodeLabelsList[i][3].strip('~') == 'Unnamed Lake/Pond' or nodeLabelsList[i][3].strip('~') == 'Unnamed Crossing':
            # temp - do it for all
            for k in range(i+1, i+j+1):
                nodeLabelsList[k][4] = False
                nodeLabelsList[i][6].append(nodeLabelsList[k][6][0]) # add the distances for the label string
            nodeLabelsList[i][3] = nodeLabelsList[i][3].strip('~')+ ' (' + str(j+1) + 'x)'

    # Omit SwampMarsh
    for i in nodeLabelsList:
        if i[5] == 'SwampMarsh':
            i[4] = False

    # Omit unnamed unnamed lakes, crossings and intermittent crossings
    labelCounter = 0
    lakeFlag = False
    streamFlag = False
    interStreamFlag = False

    for i in nodeLabelsList:
        if i[4] == True:
            labelCounter = labelCounter + 1

    labelCounterThresholds = [1, 1, 1]


    if labelCounter < labelCounterThresholds[2]:
        lakeFlag = True
        streamFlag = False
        interStreamFlag = False

    if labelCounter < labelCounterThresholds[1]:
        lakeFlag = True
        streamFlag = True
        interStreamFlag = False

    if labelCounter < labelCounterThresholds[0]:
        lakeFlag = True
        streamFlag = True
        interStreamFlag = True

    for i in nodeLabelsList:
        if i[3][0:10] == 'Unnamed La':
            i[4] = lakeFlag
        if i[3][0:10] == 'Unnamed Cr':
            i[4] = streamFlag
        if i[3][0:10] == 'Unnamed (i':
            i[4] = interStreamFlag

    streamCounter = 0
    for i in nodeLabelsList:
        #print(i[5])
        if i[5] == 'StreamRiver':
            streamCounter = streamCounter + 1


    # Look at the beginning of strings, to combine things like "Cartridge Creek" an "Cartridge Creek Crossing"
    for i in range(0, len(nodeLabelsList)-1):
        thisStr = nodeLabelsList[i][3].strip('~')[0:10]
        
        for j in range(i, min(i+10, len(nodeLabelsList))):
            nextStr = nodeLabelsList[j][3].strip('~')[0:10]
            #if 'CROSSING' in nodeLabelsList[i][3].upper() or 'CROSSING' in nodeLabelsList[j][3].upper():
            if colorDict[nodeLabelsList[i][5]]: # if it's water
                distThresh = min(0.05*max(cumDistance), 5)
            else:
                distThresh = min(0.01*max(cumDistance), 1)
            if abs(nodeLabelsList[i][1] - nodeLabelsList[j][1]) < distThresh and thisStr == nextStr and thisStr[0:7] != 'Unnamed' and nodeLabelsList[i][4] and nodeLabelsList[j][4] and i != j and colorDict[nodeLabelsList[i][5]] == colorDict[nodeLabelsList[j][5]]:
                nodeLabelsList[i][3] = nodeLabelsList[i][3].strip('~') + ' and ' + nodeLabelsList[j][3].strip('~')
                for k in nodeLabelsList[j][6]:
                    nodeLabelsList[i][6].append(k)
                #nodeLabelsList[i][6].append([i for i in nodeLabelsList[j][6]]) # removed [0]
                #print('I combined: ' + nodeLabelsList[i][3])
                nodeLabelsList[j][4] = False

    # Repeat, but combine ANYTHING that's really close and the same type
    for i in range(0, len(nodeLabelsList)-1):
        try:
            thisColor = colorDict[nodeLabelsList[i][5]]
        except KeyError:
            thisColor = [0.3, 0.3, 0.3]
        try:
            nextColor = colorDict[nodeLabelsList[i+1][5]]
        except KeyError:
            nextColor = [0.3, 0.3, 0.3]
        #thisColor = colorDict[nodeLabelsList[i][5]]
        #nextColor = colorDict[nodeLabelsList[i+1][5]]

        if abs(nodeLabelsList[i][1] - nodeLabelsList[i+1][1]) < .1 and thisColor == nextColor and nodeLabelsList[i][4] and nodeLabelsList[i+1][4]:
            nodeLabelsList[i][3] = nodeLabelsList[i][3].strip('~') + ' and ' + nodeLabelsList[i+1][3].strip('~')
            nodeLabelsList[i][6].append(nodeLabelsList[i+1][6][0])
            #print('I combined: ' + nodeLabelsList[i][3])
            nodeLabelsList[i+1][4] = False


# Create plot
    fig = figure(figsize = [32, 8])
    rcParams['xtick.labelsize'] = 'small'
    rcParams['ytick.labelsize'] = 'small'
    figWidth = max(24, max(cumDistance)/1.5)
    overSize = 0    # test to see if need to use oversize specs
    if figWidth > 24:
        overSize = 1
    overSizeScale = 16./(max(cumDistance)/1.5)
    ax1 = Subplot(fig, 211)
    fig.add_subplot(ax1)
    ax1.axis["top"].set_visible(False)
    ax1.axis["right"].set_visible(False)
    plot(cumDistance, elevArray, 'k-',linewidth=1.5)
    fill_between(cumDistance, elevArray, 0, color = [0.5, 0.5, 0.5], alpha = .5)
    xtickLocs = arange(0, max(cumDistance),int(max(cumDistance)/50)+1)
    corrFlag = 1    # Use for more fidgeting with <30 mile distance
    if overSize:
        xtickLocs = arange(0, max(cumDistance), 1)
    elif max(cumDistance) < 15:
        xtickLocs = arange(0, max(cumDistance), 0.5)
    elif max(cumDistance) < 30:
        #overSizeScale = .5
        #corrFlag = 2
        pass

    xticks(xtickLocs)
    ytickLocs = arange(100*int(0.01*min(elevArray))-100, 100*int(.01*max(elevArray))+100, int(max(.001*elevArray)-min(.001*elevArray)+1)/.01)
    yticks(ytickLocs, map(lambda x: str(int(x)) + ' ft', ytickLocs))
    yrange = max(ytickLocs) - min(ytickLocs)


    for i in range(0, len(ytickLocs)/2): # add rectangles to profile
        gca().add_patch(Rectangle((0, ytickLocs[2*i]), max(cumDistance), ytickLocs[1]-ytickLocs[0], fc='w', edgecolor='None', alpha = 0.5))

    xlabel('D I S T A N C E [mi]',fontsize = 11, fontweight = 'bold')
    ylabel('E L E V A T I O N [ft]', fontsize = 11, fontweight = 'bold')
    axis([0, max(cumDistance), ytickLocs[0], max(elevArray+500)])

    def reduceLabel(label): # use this to clean up combined labels
        s = label.strip('~').split(' and ')
        sout = list(s)
        #print(s)
        l = len(s)
        sout = [s[0]]
        for i in range(1, l):
            getout = 0
            #print(sout)
            for k in range(0, len(sout)):
                if s[i].upper() in sout[k].upper():
                    getout = 1
            for j in range(0, len(sout)):
                if sout[j].upper() in s[i].upper():
                    sout[j] = s[i]
                    getout = 1
            if not getout:
                sout.append(s[i])
            
        stringout = ''
        for i in range(0, len(sout)-1):
            stringout = stringout + sout[i] + ' and '
        stringout = stringout + sout[-1]
        #print(label)
        #print(stringout.strip(' and '))
        return stringout
    
    labelHeightList = []
    xList, yList, sList, s2List, isWaterList = [], [], [], [], []   # lists to store x, y and string in and stroke color in
    for i in range(0, len(nodeLabelsList)):
        if nodeLabelsList[i][4]: # if display is True
            xList.append(nodeLabelsList[i][1])
            yList.append(nodeLabelsList[i][2])
            sList.append(str(len(sList)+1) + '. ' + reduceLabel(nodeLabelsList[i][3].strip('~')))
            thisDist = nodeLabelsList[i][6][0] # string representation of distance
            if len(nodeLabelsList[i][6]) > 1: # if we combined them (17.3, 17.4, e.g.)
                for j in range(1, len(nodeLabelsList[i][6])-1):
                    thisDist = thisDist + ', ' + nodeLabelsList[i][6][j]
                thisDist = thisDist + ' and ' + nodeLabelsList[i][6][-1]
                

            s2List.append(' mile ' + thisDist + ', elev. ' + str(format(int(yList[-1]), ",d")) +' ft. ')
            labelHeightList.append(yList[-1]+500) # initialize to the last yList element + 1000 ft
            try:
                isWaterList.append(colorDict[nodeLabelsList[i][5]]) # add the colorDict lookup of the type
            except KeyError:
                isWaterList.append(False) # add the colorDict lookup of the type

    # Now go over lists and derive label heights
    deltax = 2 # made up?
    a = 1000 #577
    b = 577 #1000
    yheight = 4.5   # guess at height in inches

    if overSize:
        dx = (max(cumDistance))*.015*overSizeScale*corrFlag
    else:
        dx = 0.01*max(cumDistance)

    for i in range(1, len(xList)):

            if not overSize:
                thisDx = ((xList[len(xList)-i]-xList[len(xList)-i-1])/max(cumDistance))*24.0 # distance between next point and this one in x
                thisDy = 1.6*thisDx*(1000/577.)*(yrange/yheight) - 1.5*(yrange/yheight) # what distance should be in y
                labelHeightList[len(xList)-i-1] = max(labelHeightList[len(xList)-i] - thisDy, yList[len(xList)-i-1]+.1*yrange) # adjust for that, but don't put it below yList + 0.1*yrange

            else:
                thisDx = ((xList[len(xList)-i]-xList[len(xList)-i-1])/max(cumDistance))*figWidth # in inches
                thisDy = 1.6*thisDx*(1000/577.)*(yrange/yheight) - 1.5*(yrange/yheight)
                labelHeightList[len(xList)-i-1] = max(labelHeightList[len(xList)-i] - thisDy, yList[len(xList)-i-1]+.1*yrange)

    
    # function to create sigmoid when there are multiple labels
    def createSigmoid(x, y):
        yu = min(y[1], y[0] + 1000) # limit sigmoid to 1000 feet
        yi = linspace(y[0], yu, 1e3)
        sf = 10./(yu-y[0])
        xi = tanh(sf*(yi-mean([y[0], yu])))*0.5*(x[1]-x[0])+mean(x)# will be mapped to -1, 1
        out = zeros((len(yi),2))
        out[:,0] = xi
        out[:,1] = yi
        if yu < y[1]:
            out[-1,1] = y[1]
        return out
    for i in range(0, len(xList)):
        if len(sList[i]) > 60:
            ts = sList[i]
            ts = ts.replace('Lake', 'Lk')
            ts = ts.replace('Lakes', 'Lks')
            ts = ts.replace('Creek', 'Ck')
            ts = ts.replace('Fork', 'Fk')
            ts = ts.replace('North', 'N')
            ts = ts.replace('Middle', 'M')
            ts = ts.replace('South', 'S')
            ts = ts.replace('River', 'Riv')
            ts = ts.replace('Station', 'Sta')
            ts = ts.replace('Meadow', 'Mdw')
            ts = ts.replace('Meadows', 'Mdws')
            ts = ts.replace('Canyon', 'Cyn')
            ts = ts.replace('Intermittent', 'Intermitt.')
            ts = ts.replace('Crossing', 'Xing')
            ts = ts.replace('Trailhead', 'TH')
            sList[i] = ts
            if len(sList[i]) > 90:
                sList[i] = sList[i][0:89] + '...'
    for i in range(0, len(xList)):
        thisColor = [0, 0, 0]
        if isWaterList[i]:
            thisColor = [0, 0, 0.5]
        if 'and' in s2List[i]:
            thisEntry = s2List[i].split(' ')
            thisXList = []
            plot([xList[i], xList[i]],[yList[i]+0.05*(labelHeightList[i]-yList[i])+50, labelHeightList[i]], color = 'w', lw = 5, alpha = 0.7)
            d = Line2D([xList[i], xList[i]],[yList[i], labelHeightList[i]], color = thisColor, lw = 1.5)
            gca().add_line(d)

            
            if len(thisEntry) <= 9: # two labels
                thisXList = [float(thisEntry[4][0:-1])]
            if len(thisEntry) == 10: # three labels
                thisXList = [float(thisEntry[3][0:-1]), float(thisEntry[5][0:-1])]
            if len(thisEntry) == 11: # four labels
                thisXList = [float(thisEntry[3][0:-1]), float(thisEntry[4][0:-1]), float(thisEntry[6][0:-1])]
            if len(thisEntry) == 12: # 5 labels
                thisXList = list(map(lambda x: float(thisEntry[x][0:-1]), [3, 4, 5, 7]))
            if len(thisEntry) == 13: # 6 labels
                thisXList = list(map(lambda x: float(thisEntry[x][0:-1]), [3, 4, 5, 6, 8]))
            if len(thisEntry) == 14: # 7 labels
                thisXList = list(map(lambda x: float(thisEntry[x][0:-1]), [3, 4, 5, 6, 7, 9]))
            for thisX in thisXList:
                thisY =  1*(labelHeightList[i]-yList[i])+yList[i]
                thisY0 = interp(thisX, cumDistance, elevArray)
                thisY0 = thisY0+0.00*(thisY-thisY0)
                b = createSigmoid([thisX, xList[i]], [thisY0, thisY])
                plot(b[:,0], b[:,1], color = thisColor, lw = 1.5, alpha = 1)
                #if interp(float(thisEntry[2][0:-1]), cumDistance, elevArray) > labelHeightList[i]:
                #    oldy = interp(float(thisEntry[2][0:-1]), cumDistance, elevArray)
                #    plot( (xList[i], xList[i]), (oldy, thisY), color = thisColor, lw = 1.5, alpha = 1) 
                #plot([thisX, thisX], [thisY0, thisY], color = thisColor, lw = 1.5, alpha = 1)
                #plot([thisX, xList[i]], [thisY, thisY], color = thisColor, lw = 1.5, alpha = 1)
        if isWaterList[i]:
            annotate(sList[i], (xList[i], yList[i]),xytext = (xList[i],labelHeightList[i]), rotation = 60, horizontalalignment='left',verticalalignment='bottom', arrowprops=dict(width = 0.6, headwidth = 0.1, shrink = 0.01,alpha = 1, color = [0, 0, 0.5]),path_effects=[PathEffects.withStroke(linewidth=4,foreground='w',alpha=.8)],alpha = 1, fontsize = 11, fontstyle = 'oblique', fontweight = 'semibold', color = [0, 0, 0.5])
            annotate(s2List[i], (xList[i], yList[i]),xytext = (xList[i]+dx,labelHeightList[i]), rotation = 60, horizontalalignment='left',verticalalignment='bottom', arrowprops=dict(width = 0.1, headwidth = 0.1, shrink = 0.05,alpha = 0.0),path_effects=[PathEffects.withStroke(linewidth=4,foreground="w",alpha=.8)],alpha = 0.9, fontsize = 11, fontstyle = 'oblique', color = [0, 0, 0.5])
        else:
            annotate(sList[i], (xList[i], yList[i]),xytext = (xList[i],labelHeightList[i]), rotation = 60, horizontalalignment='left',verticalalignment='bottom', arrowprops=dict(width = 0.6, headwidth = 0.1, shrink = 0.01,alpha = 1),path_effects=[PathEffects.withStroke(linewidth=4,foreground='w',alpha=.8)],alpha = 1, fontsize = 11, fontweight = 'bold', color = 'k')
            annotate(s2List[i], (xList[i], yList[i]),xytext = (xList[i]+dx,labelHeightList[i]), rotation = 60, horizontalalignment='left',verticalalignment='bottom', arrowprops=dict(width = 1.5, headwidth = 0.1, shrink = 0.05,alpha = 0),path_effects=[PathEffects.withStroke(linewidth=4,foreground="w",alpha=.8)],alpha = 0.9, fontsize = 11)
        # Add multiple lines for cases where labels were combined
        if 'and' not in s2List[i]:
            plot([xList[i], xList[i]],[yList[i]+0.05*(labelHeightList[i]-yList[i])+50, labelHeightList[i]], color = 'w', lw = 5, alpha = 0.7)
            d = Line2D([xList[i], xList[i]],[yList[i], labelHeightList[i]], color = thisColor, lw = 1.5)
            gca().add_line(d)
    plot(cumDistance, elevArray, 'k-',linewidth=1.5) # one last time
    
    xlabel('D I S T A N C E [mi]',fontsize = 11, fontweight = 'bold')
    ylabel('ELEVATION', fontsize = 11, fontweight = 'bold')
    #gca().tick_params(axis='both', which='minor', labelsize=40)
    
    ax2 = subplot(2,1,2)
    
    xlabel('D I S T A N C E [mi]',fontsize = 11)
    ylabel('ELEVATION CHANGE', fontsize = 11)
    plot(cumDistance, cumClimbing, 'r-',linewidth=1.5)
    plot(cumDistance, cumDescent, 'b-', linewidth=1.5)
    rangeMax = 1.05*max(max(cumClimbing),max(cumDescent))
    def calcRotVa(y, other): # function to calculate how to rotate text
        if y < 0.9*rangeMax:
            rot = 60
            va = 'bottom'
        else: 
            rot = -60
            va = 'top'
        if other > 0.9*rangeMax and y > 0.5*rangeMax:
            rot = -60
            va = 'top'
        if abs((other-y)/float(rangeMax)) < 0.04:
            if y < other:
                y = other - 0.035*rangeMax
            if y >= other:
                y = other + 0.035*rangeMax
        return( (rot, va, y))        

    
    
    def addPoint(ay, dy, x, point, idx):
        # place text point number
        
        ap = ay/rangeMax
        dp = dy/rangeMax
        if ap < 0.6 and dp < 0.6:
            thisY = max(ay, dy) + 0.30*rangeMax
        if max(ap, dp) >= 0.6 and min(ap, dp) < 0.3:
            thisY = min(ay, dy) + 0.7*(max(ay,dy)-min(ay, dy))
        if max(ap, dp) >= 0.6 and min(ap, dp) >= 0.3:
            thisY = 0.5*min(ay, dy)
        if ap >= 0.6 and dp >= 0.6:
            thisY = 0.5*min(ay, dy)
        if x < 0.1:
            ha = 'left'
        else:
            ha = 'center'
        text(x, 0.99*rangeMax, str(point) + '.', ha = ha, va = 'center', fontsize = 10, rotation = 0, fontweight = 'bold', path_effects=[PathEffects.withStroke(linewidth=3,foreground='w',alpha=.9)])

        #text(x, thisY, str(point) + '.', ha = ha, va = 'center', fontsize = 10, rotation = 0, path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
        return (x, thisY, idx)
    counter = 0
    listLoc = []
    lastIdx = 0
    for i in range(0, len(nodeLabelsList)):
        if nodeLabelsList[i][4]:
            lastIdx = i
    for i in range(0, len(nodeLabelsList)):
        if nodeLabelsList[i][4]: # if display is True
            
            counter = counter + 1
            x = nodeLabelsList[i][1]
            ay = interp(nodeLabelsList[i][1], cumDistance, cumClimbing)
            dy = interp(nodeLabelsList[i][1], cumDistance, cumDescent)
            #plot(nodeLabelsList[i][1], interp(nodeLabelsList[i][1], cumDistance, cumClimbing), 'ro', markersize = '3')
            if nodeLabelsList[lastIdx][1] - x <= 1 and i != lastIdx:
                pass # skip cuz we're too close to the last one
            elif i == 0:
                lastx = x
                listLoc.append(addPoint(ay, dy, x, counter, i))
                plot((x, x), (0, 1.1*max( max(cumClimbing), max(cumDescent))), 'k', linewidth = 1.5, alpha = 0.4)
                plot(x, dy, 'bo', markersize = 3, markeredgecolor = 'b')
                plot(x, ay, 'ro', markersize = 3, markeredgecolor = 'r')
                text(x, calcRotVa(ay, dy)[2], str(int(round(ay,0))), rotation = calcRotVa(ay, dy)[0], color = 'r', fontsize = 10, ha = 'left', va = calcRotVa(ay, dy)[1], path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
                text(x, calcRotVa(dy, ay)[2], str(int(round(dy,0))), rotation = calcRotVa(dy, ay)[0], color = 'b', fontsize = 10, ha = 'left', va = calcRotVa(dy, ay)[1], path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
            elif x - lastx > 1.0:
                lastx = x
                listLoc.append(addPoint(ay, dy, x, counter, i))
                plot((x, x), (0, 1.1*max( max(cumClimbing), max(cumDescent))), 'k', linewidth = 1.5, alpha = 0.4)
                plot(x, dy, 'bo', markersize = 3, markeredgecolor = 'b')
                plot(x, ay, 'ro', markersize = 3, markeredgecolor = 'r')
                text(x, calcRotVa(ay, dy)[2], str(int(round(ay,0))), rotation = calcRotVa(ay, dy)[0], color = 'r', fontsize = 10, ha = 'left', va = calcRotVa(ay, dy)[1], path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
                text(x, calcRotVa(dy, ay)[2], str(int(round(dy,0))), rotation = calcRotVa(dy, ay)[0], color = 'b', fontsize = 10, ha = 'left', va = calcRotVa(dy, ay)[1], path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
    # add more stuff (mileage, etc)
    for i in range(1, len(listLoc)):
        plot((listLoc[i-1][0], listLoc[i][0]), (listLoc[i-1][1], listLoc[i-1][1]), 'k-', linewidth = 1.5, alpha = 0.4)
        thisX = mean([listLoc[i-1][0], listLoc[i][0]])
        thisY = listLoc[i-1][1]
        thisClimb = interp(nodeLabelsList[listLoc[i][2]][1], cumDistance, cumClimbing) - interp(nodeLabelsList[listLoc[i-1][2]][1], cumDistance, cumClimbing)
        thisDescent = interp(nodeLabelsList[listLoc[i][2]][1], cumDistance, cumDescent) - interp(nodeLabelsList[listLoc[i-1][2]][1], cumDistance, cumDescent)

        #dy = interp(nodeLabelsList[listLoc[i][2]][1], cumDistance, cumDescent)
        text(thisX, thisY, str(round(listLoc[i][0]-listLoc[i-1][0],2)) + ' miles', fontsize = 9, ha = 'center', va = 'bottom', path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
        text(thisX, thisY-.065*rangeMax, '+' + str(int(round(thisClimb,0))) + ' ft', color = 'r', fontsize = 9, ha = 'center', va = 'bottom', path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
        text(thisX, thisY-.12*rangeMax, '-' + str(int(round(thisDescent,0))) + ' ft', color = 'b', fontsize = 9, ha = 'center', va = 'bottom', path_effects=[PathEffects.withStroke(linewidth=2,foreground='w',alpha=.5)])
            
    grid(1)
    legend(['Cumulative Ascent','Cumulative Descent'],loc=(0.005, 0.75),fontsize = 9, framealpha = 0.5)
    xticks(xtickLocs)
    #tick_params(axis='both', which='major', labelsize=12)
    
    yticks(yticks()[0], map(lambda x: str(int(x)) + ' ft', yticks()[0]))
    axis([0, max(cumDistance), 0, 1.05*max(max(cumClimbing),max(cumDescent))])
    fig.set_size_inches(figWidth,6) # use later when saving
    profileFileName = os.path.join(request.folder, 'static/profiles', key + '_profile.png')

    savefig(profileFileName, dpi = 100, bbox_inches='tight')

    # add thumbnail code
    fig = figure(figsize = [5, 1.5])
    ax1 = Subplot(fig, 111)
    fig.add_subplot(ax1)
    ax1.axis["top"].set_visible(False)
    ax1.axis["right"].set_visible(False)
    xticks([])
    if max(elevArray) - min(elevArray) < 6000:
        ytickLocs2 = arange(int(.001*min(elevArray))*1000, (int(.001*max(elevArray))+1)*1000+1000, 1000)
    else: 
        ytickLocs2 = arange(int(.001*min(elevArray))*1000, (int(.001*max(elevArray))+1)*1000+2000, 2000)
    yticks(ytickLocs2)
    yrange = max(ytickLocs2) - min(ytickLocs2)
    tick_params(axis='both', which='major', labelsize=12)
    for i in range(0, len(ytickLocs)/2):
        gca().add_patch(Rectangle((0, ytickLocs[2*i]), max(cumDistance), ytickLocs[1]-ytickLocs[0], fc='w', edgecolor='None', alpha = 0.5))

    axis([0, max(cumDistance), ytickLocs2[0], ytickLocs2[-1]])
    plot(cumDistance, elevArray, 'k-',linewidth=1.5)
    fill_between(cumDistance, elevArray, 0, color = [0.5, 0.5, 0.5], alpha = .5)
    profileFileName = os.path.join(request.folder, 'static/profiles', key + '_profile_thumb.png')
    savefig(profileFileName, dpi = 80, bbox_inches='tight')
    close()
    
    forecast = 'lon=' + str(outCoordsArray[0,0]) + '&lat=' + str(outCoordsArray[0,1])
    thisDBEntry.update_record(
                profile = str(key + '_profile.png'))
    thisDBEntry.update_record(
                maxelevation = int(max(tempElev)),
                minelevation = int(min(tempElev)),
                forecast = forecast,
                streamcrossings = streamCounter)
    close('all')
    
    # save the elevation data
    out = zeros((len(newDist), 4))
    out[:,0] = newDist
    out[:,1] = ef
    out[:,2] = interp(newDist, cumDistance, cumClimbing)
    out[:,3] = interp(newDist, cumDistance, cumDescent)
    profileDataFileName = os.path.join(request.folder, 'static/dataprofiles', key + '_profile_data.csv')
    thisHeader = '# Distance in miles, elevation in feet, cumulative ascent in feet, cumulative descent in feet'
    savetxt(profileDataFileName, out, fmt = ['%1.3f', '%1.2f', '%1.1f', '%1.1f'], delimiter = ',', header = thisHeader)

    # save the profile table
    textProfileFilename = os.path.join(request.folder, 'static/textprofiles', key + '.txt')
    f = open(textProfileFilename, 'wb')
    k = 0
    f.write('# Profile Label Number, Point Number, Cum. Distance [mi], Cum. Terr. Distance [mi], elevation [ft], Cum. Ascent [ft], Cum. Descent [ft], Label, Lat, Long' + '\n')
    for i in nodeLabelsList:
        if i[4]:
            k = k + 1
            thisLabelNumber = str(k)
        else:
            thisLabelNumber = '-'
        # get point number in ef
        thisPoint = str( int(round(interp(i[1], newDist, linspace(0, len(newDist)-1, len(newDist))),0) ) )
        f.write(thisLabelNumber + ', ' + thisPoint + ', ' + str(round(i[1],2)) + ', ' + str(round(terrDist[i[0]],2)) +  ', '+ str(int(i[2])) + ', ' + str(round(cumClimbing[i[0]],1)) + ', ' + str(round(cumDescent[i[0]],1)) + ', ' + str(i[3]).strip('~') + ', '  + str(round(outCoordsArray[i[0],1],6)) + ', ' + str(round(outCoordsArray[i[0],0],6)) + '\n')
    f.close()
"""
def nodes_selector():
    #if not request.vars.nodes:
    #    return ''
    if len(request.vars.nodes) > 1:
        pattern = '%' +request.vars.nodes.capitalize() + '%'
        selected = [row.nickname for row in db(db.nodes.nickname.like(pattern)).select()]
        return ''.join([DIV(k,
                     _onclick="jQuery('#nodes').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ).xml() for k in selected])
    else:
        return ''
"""

def nodes_selector():
    if len(request.vars.nodes) > 0:
        pattern = '%' +request.vars.nodes.capitalize() + '%'
        #selected = [row.nickname for row in db(db.nodes.nickname.like(pattern)).select()]
        selected = []
        for row in db(db.nodes.nickname.like(pattern)).select():
            thisStr = [row.nickname, ', ' + row.locale, row.nodeID]
            selected.append(thisStr)
        #selected = [row.nickname for row in db(db.nodes.nickname.like(pattern)).select()]

        outStr = ''.join([DIV(k[0:2],
                     _onclick="jQuery('#nodes').val('%s')" % k[0],
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ).xml() for k in selected])
        return outStr
    else:
        return ''



def nodesReturn():
    #pattern = '%' +request.vars.nodes.capitalize() + '%'
    pattern = request.vars.nodes.capitalize()
    thisName = [row.nickname for row in db(db.nodes.nickname.like(pattern)).select()][0]
    thisLat =  [row.latitude for row in db(db.nodes.nickname.like(pattern)).select()][0]
    thisLong = [row.longitude for row in db(db.nodes.nickname.like(pattern)).select()][0]
    outStr = ''.join([DIV(thisLat).xml(),DIV(thisLong).xml()])
    outStr = str(thisName) + ',' + str(thisLat) + ',' + str(thisLong)
    #outStr = 'apples'
    return outStr

def createDB():
    db.nodes.truncate()
    filename = os.path.join(request.folder, 'static', 'gr.gpickle')
    gr = nx.read_gpickle(filename)
    nodeCoords = nx.get_node_attributes(gr, 'Coordinates')
    nodeNicknames = nx.get_node_attributes(gr, 'Nicknames')
    nodeMarkerList = []
    for node in list(gr.nodes_iter()):

        if len(nodeNicknames[node]) == 0:
            thisNick = ('Unnamed Jct.')
        else:
            thisNick = nodeNicknames[node][0]

        if str(node)[0] == 'n':
            thisLocale = 'Yosemite National Park'
        elif str(node)[0] == 'm':
            thisLocale = 'Inyo National Forest'
        elif str(node)[0] == 'k':
            thisLocale = 'Kings Canyon National Park'
        elif str(node)[0] == 's':
            thisLocale = 'Sequoia National Park'
        elif str(node)[0] == 'r':
            thisLocale = 'Sierra National Forest'
        elif str(node)[0] == 'l':
            thisLocale = 'Stanislaus National Forest'
        elif str(node)[0] == 't':
            thisLocale = 'Toiyabe National Forest'
        else:
            thisLocale = 'Nowhere???'
        db.nodes.insert(nodeID=str(node), nickname = thisNick, latitude=nodeCoords[node][1], longitude=nodeCoords[node][0], elevation = nodeCoords[node][2], locale = thisLocale)
    grid = SQLFORM.smartgrid(db.nodes)
    return dict(grid=grid)

"""
def createDB2(): # Routes DB
    db.routes.truncate()
    db.routes.insert(node1 = 'n001', node2 = 'n006', nodeList = 'n001,n002,n004,n006')
    grid = SQLFORM.smartgrid(db.routes)
    return dict(grid=grid)
"""
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def returnDisplayCoords(): # for dynamically displaying the route
    #coords=db(db.balloonprices.type==request.vars.typeSelected).select(db.balloonprices.cost)
    row = db(db.displayroutes.name==str(request.post_vars.array.strip('"'))).select().first()
    coords = row.coords
    return coords

def calcRouteDB(): # function used to generate display routes--call with two nodes 'n001' and 'n008', e.g., and it will save a file 'n001_n008.csv'
    gr = nx.read_gpickle(os.path.join(request.folder, 'static', 'gr.gpickle'))
    outCoordsList = []
    nodes = request.post_vars.array.strip('"').split('_')
    #print(nodes)
    n1 = nodes[0]
    n2 = nodes[1]
    thisPath = nx.dijkstra_path(gr, n1, n2, 'weight')
    thisPathLength = 1.03*nx.dijkstra_path_length(gr, n1, n2, 'weight') # 1.03 is fudge factor
    #print(thisPath)
    for j in range(0, len(thisPath) - 1):
        node1 = thisPath[j]
        node2 = thisPath[j+1]
        if gr.node[node1]['id'] < gr.node[node2]['id']: # Good
            outCoordsList.append(gr.edge[node1][node2]['Coordinates'])
        if gr.node[node1]['id'] > gr.node[node2]['id']: # Flip 'er over
            outCoordsList.append(flipud(gr.edge[node1][node2]['Coordinates']))

            
    # Covert outCoordsList to array
    numCoords = 0
    for i in range(0,len(outCoordsList)):
        numCoords = numCoords + size(outCoordsList[i][:,0])
        #print(numCoords)

    outCoordsArray = zeros((numCoords,3))
    startRow = 0
    for i in range(0, len(outCoordsList)):
        thisEndRow = startRow + size(outCoordsList[i][:,0])
        outCoordsArray[startRow:thisEndRow,:] = outCoordsList[i]
        startRow = thisEndRow
    if thisPath[0] > thisPath[-1]:
        outCoordsArray = flipud(outCoordsArray)
    displayRouteString = str(round(thisPathLength,2)) + ',' + str(round(outCoordsArray[0,1],5))+ ',' +str(round(outCoordsArray[0,0],5)) + ','
    lastPoint = outCoordsArray[0,:]
    for i in range(0, len(outCoordsArray)):
        if calcDist2(lastPoint, outCoordsArray[i,:]) > 0.05 or i == len(outCoordsArray-1):
            displayRouteString = displayRouteString + str(round(outCoordsArray[i,1],5))+ ',' +str(round(outCoordsArray[i,0],5)) + ','
            lastPoint = outCoordsArray[i,:]
    displayRouteString = displayRouteString[:-1]
    thisRoute = min(n1,n2) + '_' + max(n1,n2)
    db.displayroutes.insert(name = thisRoute, node1 = min(n1,n2), node2 = max(n1,n2), coords = displayRouteString)

def cleardisplayroutesDB():
    db.displayroutes.truncate();
    
    
def calcRouteDBFill(): # Autopopulate display routes database
    gr = nx.read_gpickle(os.path.join(request.folder, 'static', 'gr.gpickle'))
    f = open(os.path.join(request.folder, 'static', 'displayroutes.csv'))
    f.readline()

    def calcThisRoute(n1, n2):
        
        outCoordsList = []
        thisPath = nx.dijkstra_path(gr, n1, n2, 'weight')
        thisPathLength = 1.03*nx.dijkstra_path_length(gr, n1, n2, 'weight') # 1.03 is fudge factor
        for j in range(0, len(thisPath) - 1):
            node1 = thisPath[j]
            node2 = thisPath[j+1]
            if gr.node[node1]['id'] < gr.node[node2]['id']: # Good
                outCoordsList.append(gr.edge[node1][node2]['Coordinates'])
            if gr.node[node1]['id'] > gr.node[node2]['id']: # Flip 'er over
                outCoordsList.append(flipud(gr.edge[node1][node2]['Coordinates']))
    
                
        # Covert outCoordsList to array
        numCoords = 0
        for i in range(0,len(outCoordsList)):
            numCoords = numCoords + size(outCoordsList[i][:,0])
            #print(numCoords)
    
        outCoordsArray = zeros((numCoords,3))
        startRow = 0
        for i in range(0, len(outCoordsList)):
            thisEndRow = startRow + size(outCoordsList[i][:,0])
            outCoordsArray[startRow:thisEndRow,:] = outCoordsList[i]
            startRow = thisEndRow
        if thisPath[0] > thisPath[-1]:
            outCoordsArray = flipud(outCoordsArray)
        displayRouteString = str(round(thisPathLength,2)) + ',' + str(round(outCoordsArray[0,1],5))+ ',' +str(round(outCoordsArray[0,0],5)) + ','
        lastPoint = outCoordsArray[0,:]
        for i in range(0, len(outCoordsArray)):
            if calcDist2(lastPoint, outCoordsArray[i,:]) > 0.05 or i == len(outCoordsArray-1):
                displayRouteString = displayRouteString + str(round(outCoordsArray[i,1],5))+ ',' +str(round(outCoordsArray[i,0],5)) + ','
                lastPoint = outCoordsArray[i,:]
        displayRouteString = displayRouteString[:-1]
        thisRoute = min(n1,n2) + '_' + max(n1,n2)
        db.displayroutes.insert(name = thisRoute, node1 = min(n1,n2), node2 = max(n1,n2), coords = displayRouteString)
    for m in range(0,3000):
        thisLine = f.readline().split(',')
        calcThisRoute(thisLine[2], thisLine[3])
        
def displayroutedatabase():
    grid = SQLFORM.smartgrid(db.displayroutes)
    return dict(grid=grid)

