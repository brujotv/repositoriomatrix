# -*- coding: utf-8 -*-

""" Plexus  (c)  2015 enen92

    This file contains the function that brigdes the addon to the acecore.py file
    
    Functions:
    
    load_local_torrent() -> Load a local .torrent file
    acestreams(name,iconimage,chid) -> Function that interprets the received url (acestream://,*.acelive,ts://) and sends it to acestreams_builtin
    acestreams_builtin(name,iconimage,chid -> Bridge to acecore.py file
   	

"""
    
import xbmc,xbmcgui,xbmcplugin,urllib,xbmcvfs,os,subprocess
from plexusutils.pluginxbmc import *
from history import *

aceport=62062

def load_local_torrent():
	torrent_file = xbmcgui.Dialog().browse(1, translate(30037),'video', '.torrent')
	if torrent_file:
		if xbmc.getCondVisibility('system.platform.windows'):
			acestreams("Local .torrent ("+str("file:\\" + torrent_file) +")","",'file:\\' + torrent_file)
		else:
			acestreams("Local .torrent ("+str("file://" + torrent_file) +")","",'file://' + urllib.quote(torrent_file))
	else: pass

def acestreams(name,iconimage,chid):
	if not iconimage: iconimage=os.path.join(addonpath,'resources','art','acestream-menu-item.png')
	else: iconimage = urllib.unquote(iconimage)
	if settings.getSetting('addon_history') == "true":
		try: add_to_history(name, str(chid),1, iconimage)
		except: pass
	if settings.getSetting('engine_app') != '1' and settings.getSetting('engine_app') != '2':
		if settings.getSetting('aceplay_type') == "1":
			pDialog = xbmcgui.DialogProgress()
			ret = pDialog.create(translate(30000), translate(30038),translate(30039),translate(30040))
			pDialog.update(0)
			xbmc.sleep(3000)
			pDialog.update(100)
			pDialog.close()
			ip_adress = settings.getSetting('ip_addr')
			proxy_port = settings.getSetting('aceporta')
			chid=chid.replace('acestream://','').replace('ts://','')
			strm = "http://" + ip_adress + ":" + proxy_port + "/ace/getstream?id=" + chid
			listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
			listitem.setLabel(name + " (" + chid + ")")
			listitem.setInfo('video', {'Title': name + " (" + chid + ")"})
			xbmc.Player().play(strm,listitem)
		else: acestreams_builtin(name,iconimage,chid)
	else:
		if '.acelive' in chid: pass
		elif '.torrent' in chid: pass
		else:
			if 'acestream://' in chid: pass
			else: chid = 'acestream://' + chid
		if settings.getSetting('engine_app') == '1':
			xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream.media","android.intent.action.VIEW","","'+chid+'")')
		elif settings.getSetting('engine_app') == '2':
			xbmc.executebuiltin('XBMC.StartAndroidActivity("ru.vidsoftware.acestreamcontroller.free","android.intent.action.VIEW","","'+chid+'")')

def acestreams_builtin(name,iconimage,chid):
    if xbmc.getCondVisibility('system.platform.windows'):
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\AceStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            print needed_value.replace('\\','\\\\')
            subprocess.Popen("wmic process where ExecutablePath='"+needed_value.replace('\\','\\\\')+"' delete",shell=True)
            xbmc.sleep(200)
            subprocess.Popen('taskkill /F /IM ace_player.exe /T',shell=True)
            xbmc.sleep(200)
        except: pass
    elif xbmc.getCondVisibility('System.Platform.OSX'):
        if settings.getSetting('shutdown-engine') == "true":
            os.system("kill $(ps aux | grep '[s]tart.py')")
    try:from acecore import TSengine as tsengine
    except:
        mensagemok(translate(30000),translate(30041))
        return
    xbmc.executebuiltin('Action(Stop)')
    lock_file = xbmc.translatePath('special://temp/'+ 'ts.lock')
    if xbmcvfs.exists(lock_file):
    	xbmcvfs.delete(lock_file)
    if chid != '':
        chid=chid.replace('acestream://','').replace('ts://','')
        print("Starting Player Ace hash: " + chid)
        TSPlayer = tsengine()
        out = None
        if chid.find('http://') == -1 and chid.find('.torrent') == -1:
            out = TSPlayer.load_torrent(chid,'PID',port=aceport)
        elif chid.find('http://') == -1 and chid.find('.torrent') != -1:
            out = TSPlayer.load_torrent(chid,'TORRENT',port=aceport)
        else:
            out = TSPlayer.load_torrent(chid,'TORRENT',port=aceport)
        if out == 'Ok':
            TSPlayer.play_url_ind(0,name + ' (' + chid + ')',iconimage,iconimage)
            TSPlayer.end()
            return
        else:    
            mensagemok(translate(30000),translate(30042))
            TSPlayer.end()
            return
    else:
        mensagemprogresso.close()
