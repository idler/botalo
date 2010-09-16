#!/usr/bin/env python
# -*- coding:utf-8 -*-


from jabberbot.jabberbot import JabberBot, botcmd
import datetime,os,sys,threading,time,socket
from ConfigParser import ConfigParser
#from io import open

class EventThread(threading.Thread):
  canserve = True
  def __init__(self, bot):
    self.bot = bot
    try:
      os.remove('/tmp/jabberbot')
    except OSError:
      pass
    threading.Thread.__init__(self)
    
  def run(self):
       
    try:
      os.remove("/tmp/jabberbot")
    except OSError:
      pass
    
    
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2);
    s.bind("/tmp/jabberbot")
    s.listen(1)
    while self.canserve:
      try:
        conn,addr = s.accept()
      except socket.timeout:
        print "it is timeout"
        continue
      try:
        d = conn.recv(1024)
      except socket.error:
        print "cannot read"
      if not d:  
        print "no data"
        break
      self.bot.broadcast(d)
      conn.send('ok, thanks')
    conn.close()


class ClientThread(threading.Thread):
  def __init__(self,bot,client,cmd):
    self.bot = bot
    self.client = client
    self.cmd = cmd
    threading.Thread.__init__(self)
    
    
  def run(self):
    
    bot.send(self.client,u"<br/><b>Start to run:</b> "+self.cmd)
        
    pipe = os.popen(self.cmd);
    out = "<br/>" + pipe.read().replace("\n","<br/>")
    
    if(len(out)>1024):
      out=out[:512]+"<br/>....<br/>....<b>skiped</b>....<br/>....<br/>"+out[-512:]
    
    
    bot.send(self.client,u"<br/><b>Task finished:</b> "+self.cmd)
    out =  "<br/>Output:<br/>----------------------------<br/>"+out
    

    bot.send(self.client,out.decode('utf-8'))



class SystemInfoJabberBot(JabberBot):
    def __init__(self, username, password, res=None, debug=False):        
      self.start_time = time.localtime()      
      self.msg = EventThread(self)
      self.msg.start()
      JabberBot.__init__(self, username, password, res, debug)
      
      
    def shutdown(self):
      print "I will down!"
      self.msg.canserve = False
      self.msg.join(2)
    @botcmd
    def info( self, mess, args):
        """Displays information about the server"""
        version = "<br/><b>Version</b>:  " +  open('/proc/version').read().strip()
        loadavg = "<br/><b>LOAD AVG</b>: " + open('/proc/loadavg').read().strip()

        return '%s\n%s' % ( version, loadavg, )
    
    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        return time.strftime("<br/><b>Current time: </b>%a, %d %b %Y %H:%M:%S +0000",time.localtime())

    @botcmd
    def uptime( self, mess, args):
        """Displays when bot started"""
        thread = ClientThread(self,mess.getFrom(),'uptime')
        thread.start()
        return "<br/>"+ time.strftime("<b>Running since: </b>%a, %d %b %Y %H:%M:%S +0000",self.start_time) + self.time('time','')

    @botcmd
    def sys( self, mess, args):
        """perform system command via pipe
        
you must specify more, than one command
Example: cd /var/www && ls; cd /var/backup && ./create-backup 

Executing of your command will go in background and bot will send message to you, when finished 
        """
        
        thread = ClientThread(self,mess.getFrom(),args)
        thread.start()
        return 'Task started, I will send to you part of output, when it finished.'
      
      
      
    @botcmd
    def sm( self, mess, args):
        """perform symfony command via pipe
        
Executing of your command will go in background and bot will send message to you, when finished 
        """
        conf =  ConfigParser()
        conf.read('bot.conf');
        key,value = conf.items('symfony')[0]
        cmd = 'cd '+value+'; ./symfony '+args
        thread = ClientThread(self,mess.getFrom(),cmd)
        thread.start()
        return 'Task started, I will send to you part of output, when it finished.'
      
      
#    @botcmd
#    def paused(self,mess,args):
#      th = ClientThread(self,mess.getFrom())
#      th.start()
#      return 'started'
 
if(len(sys.argv)<3):
  print """ Usage:
  ./bot2.py name@server.com password """
  exit(0) 
 
username = sys.argv[1]
password = sys.argv[2]
bot = SystemInfoJabberBot(username,password,debug=True)
bot.serve_forever()
