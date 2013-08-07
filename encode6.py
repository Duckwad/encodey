#!/usr/bin/env python

#reencode script
version='PREv6.0'
#August-07-2013
#compatible with localhost web encode frontend
#sorta like a cock is compatible with an asshole

#TO DO:
#non-fronty encode reporting
#fix parse errors

#pass  -tl --move completed/  into the queue file
#call  ./encode5.py --filename queue.txt  	when starting a queue.

#TouhouMusicEveryDay

#imports
from subprocess import call, Popen, PIPE, STDOUT, check_output
from os import listdir, makedirs
from os.path import isdir, expanduser, isfile, devnull
from shutil import move
import sys
from time import sleep
import multiprocessing
#import traceback

#log name
logfname="encodelog.log"
#progress report log thing name
reportlog="progress.log"
#changes the frequency of log reporting (seconds)
logreportupdate=1

#colors
cRED='\033[0;31m'
cGREEN='\033[0;32m'
cYELLOW='\033[0;33m'
cBLUE='\033[0;34m'
cPURPLE='\033[0;35m'
cLBLUE='\033[0;36m'
cRESET='\033[0m'

#-help dialogue in order of precedence
def helpy():
 return """\033[1;32mThe Duckwad Auto Reencode Script %s
\033[0;32mArguments:
\033[0;36m--help, -h, -?:\033[0;32m Displays this dialogue.
\033[0;36m--check, -c:\033[0;32m Instead of encoding, checks the tracks and gives useful informations.
\033[0;36m--filename, -f [filename]:\033[0;32m Takes a single file or a .txt file with a list.  Overrides input extension arguments.
\033[0;36m--inext, -i [extension]:\033[0;32m Uses [extension] as input extension, default is \033[0mmkv\033[0;32m. Omit the dot.
\033[0;36m--oext, -o [extension]:\033[0;32m Uses [extension] as output, default is \033[0mavi\033[0;32m. Only \033[0mavi\033[0;32m and \033[0mmp4\033[0;32m allowed right now. Omit the dot.
\033[0;36m--bitrate, -b [number]k:\033[0;32m Forces a different mencoder bitrate. Defaults to \033[0m1000(k)\033[0;32m. Omit the 'k' from this argument. For mp4 encodes use the -crf argument.
\033[0;36m-crf [crf]:\033[0;32m Forces a different crf. Defaults to \033[0m23\033[0;32m.
\033[0;36m--resolution, -r [WxH]:\033[0;32m Forces a different resolution. Default for 16:9 is \033[0m704x400\033[0;32m and 4:3 is \033[0m640x480\033[0;32m. The 'x' is required; no spaces.
\033[0;36m-fps [fps]:\033[0;32m force a different fps. Default is \033[0m23.976 (24000/1001)\033[0;32m.
\033[0;36m-x [args]:\033[0;32m forces extra ffmpeg arguments. In case of spaces, enclose the arguments in quotations.
\033[0;36m--move, -m [folder/]:\033[0;32m moves the completed encode to [folder/]. Default is current folder; include the trailing forward slash unless you want to rename the file.
\033[0;36m--logfile, -l:\033[0;32m generate an encoding log \033[0m%s\033[0;32m (does not stop encoding).
\033[0;36m-tl:\033[0;32m generate a temporary log that is deleted after encoding finishes (does not stop encoding).
\033[0m""" % (version, logfname)

#check for the relevant programs, break if not found
def checkNecessaryFiles():
 errvar=0
 errstr=cPURPLE
 if not isfile('/usr/bin/mediainfo'):
  try:
   call('mediainfo',stdout=None)
  except OSError:
   errvar=1
   errstr=errstr + "Mediainfo is required to be installed for this to work! (apt-get install mediainfo)\n"

 if not isfile('/usr/bin/mkvextract'):
  try:
   call('mkvextract',stdout=None)
  except OSError:
   errvar=1
   errstr=errstr + "Mkvtoolnix is required to be installed for this to work! (apt-get install mkvtoolnix)\n"

 if not isfile('/usr/bin/mencoder'):
  try:
   call('mencoder',stdout=None)
  except OSError:
   errvar=1
   errstr=errstr + "Mencoder is required to be installed for this to work! (apt-get install mencoder)\n"

 if not isfile('/usr/bin/ffmpeg'):
  try:
   call('ffmpeg',stdout=None)
  except OSError:
   errvar=1
   errstr=errstr + "FFMPEG is required to be installed for this to work! (https://ffmpeg.org/trac/ffmpeg/wiki/UbuntuCompilationGuide)"

 if errvar == 1:
  sys.exit(errstr + cRESET)
#end program check

##########################################################################
#filestuff class: uses filename to get mkv info with mediainfo and parse it
#as sell as do other pretty much everything else in the functions
class FileStuff():
#variables
 metadata=[]
 vidStreamCount=0
 audStreamCount=0
 textStreamCount=0
 vidAR=''
 vidXRes=0
 vidYRes=0
 vidFPS=float(0.000)
 vidID=-1
 
 audStreamCount=0
 audLanguage=''
 audID=-1
 audFormat=''

 textStreamCount=0
 textFormat=''
 textID=-1

 #these are defaults and will change depending on the metadata (except for fps)
 ffvidmap='-map 0:0'
 ffaudmap='-map 0:1'
 fffps='-r 23.976 '
 ffres='-s 704x400 '
 ffcrf=23
 ffvfarg=''
 ffextra=''
 fflog=''
 fflog2=''
 mebitrate=1000
 meextra=''
 targetframecount=1.2345678
 #gets the metadata from mediainfo and puts it in the list and cleans it up
 def getMetadata(self, fname):
  templist=[]
  vidarg='mediainfo --inform="Video;~VIDSTREAMS~%%StreamCount%%~VIDID~%%ID%%~VIDAR~%%AspectRatio/String%%~FPS~%%FrameRate%%~XRES~%%Width%%~YRES~%%Height%%~" "%s"' %fname
  audarg='mediainfo --inform="Audio;~AUDSTREAMS~%%StreamCount%%~AUDID~%%ID%%~AUDLANGUAGE~%%Language/String%%~AUDFORMAT~%%Format%%~" "%s"' % fname
  textarg='mediainfo --inform="Text;~TEXTSTREAMS~%%StreamCount%%~TEXTID~%%ID%%~TEXTFORMAT~%%Format%%~" "%s"' % fname
  #video
  pipey = Popen(vidarg, stdout=PIPE, stderr=STDOUT, shell=True)
  tempstr=str(pipey.communicate())
  for x in tempstr.split('~'):
   if not x.startswith('(') and not x.startswith('\\n'):
    templist.append(x)

  #audio
  pipey = Popen(audarg, stdout=PIPE, stderr=STDOUT, shell=True)
  tempstr=str(pipey.communicate())
  for x in tempstr.split('~'):
   if not x.startswith('(') and not x.startswith('\\n'):
    templist.append(x)

  #text
  pipey = Popen(textarg, stdout=PIPE, stderr=STDOUT, shell=True)
  tempstr=str(pipey.communicate())
  for x in tempstr.split('~'):
   if not x.startswith('(') and not x.startswith('\\n'):
    templist.append(x)
  self.metadata=templist
 #end getMetadata

 #checks the video streams
 def getVideoStreams(self):
  try:
   self.vidStreamCount=int(self.metadata[self.metadata.index("VIDSTREAMS")+1])
  except ValueError:
   self.vidStreamCount=0
  return self.vidStreamCount
 #end getVideoStreams
 #checks audio streams
 def getAudioStreams(self):
  try:
   self.audStreamCount=int(self.metadata[self.metadata.index("AUDSTREAMS")+1])
  except ValueError:
   self.audStreamCount=0
  return self.audStreamCount
 #end getAudioStreams
 #chest the subtitle streams
 def getTextStreams(self):
  try:
   self.textStreamCount=int(self.metadata[self.metadata.index("TEXTSTREAMS")+1])
  except ValueError:
   self.textStreamCount=0
  return self.textStreamCount
 # end getTextStreams
 #gets the video metadata, only called if getvidestreams returns 1
 def getVideoMetadata(self):
  try:
   self.vidAR=str(self.metadata[self.metadata.index("VIDAR")+1])
   self.vidID=int(self.metadata[self.metadata.index("VIDID")+1])
   self.vidFPS=float(self.metadata[self.metadata.index("FPS")+1])
   self.vidXRes=int(self.metadata[self.metadata.index("XRES")+1])
   self.vidYRes=int(self.metadata[self.metadata.index("YRES")+1])
  except:
   pass
 #end getvideometadata

 #gets the audio metadata, only called if getvidstreams returns 1 and getaudstreams is > 0
 def getAudioMetadata(self, streamcount):
 #if 1 stream: all is well
 #if 2+ streams: find japanese track and use that
 #if 0 stream: flip the fuck out
  if streamcount == 0:
   return 0
  elif streamcount == 1:
   self.audID=int(self.metadata[self.metadata.index("AUDID")+1])
   self.audFormat=str(self.metadata[self.metadata.index("AUDFORMAT")+1])
   self.audLanguage=str(self.metadata[self.metadata.index("AUDLANGUAGE")+1])
   return 1
  elif streamcount > 1:
   self.audID=int(self.metadata[self.metadata.index("AUDID")+1])
   try:
    self.audID=int(self.metadata[self.metadata.index("Japanese")-2])
    self.audFormat=str(self.metadata[self.metadata.index("Japanese")+2])
    self.audLanguage="Japanese" #lol
   except:
    #print cYELLOW + "Unable to determine Japanese audio stream; using track %d as default." % self.audID + cRESET
    self.audFormat=str(self.metadata[self.metadata.index("AUDFORMAT")+1])
    self.audLanguage=str(self.metadata[self.metadata.index("AUDLANGUAGE")+1])
    return 3
   return 2
 #end getaudmetadata
 
 #gets the text metadata, this should always be called unless there are no video streams
 def getTextMetadata(self, streamcount):
  if streamcount == 0:
   return 0
  elif streamcount == 1:
   self.textID=int(self.metadata[self.metadata.index("TEXTID")+1])
   self.textFormat=str(self.metadata[self.metadata.index("TEXTFORMAT")+1])
  elif streamcount > 1:
   try:
    self.textID=int(self.metadata[self.metadata.index("ASS")-2])
    self.textFormat="ASS"
   except:
    self.textID=int(self.metadata[self.metadata.index("TEXTID")+1])
    self.textFormat=str(self.metadata[self.metadata.index("TEXTFORMAT")+1])
   return 1
 #end gettextmetadata

 #gets the sub format, changes the vf argument appropriately and extracts the subtitle track as sobs.ass
 def subtitleExtract(self,fname):
  if self.textFormat == "ASS":
   self.ffvfarg='-vf ass="sobs.ass" '
   call(['mkvextract','tracks',fname,'%d:sobs.ass' % self.textID])
  elif self.textFormat == "UTF-8":
   self.ffvfarg='-vf subtitles="sobs.srt" '
   call(['mkvextract','tracks',fname,'%d:sobs.srt' % self.textID])
  elif self.textFormat == "SSA":
   self.ffvfarg='-vf ass="sobs.ssa" '
   call(['mkvextract','tracks',fname,'%d:sobs.ssa' % self.textID])
  else:
   pass
 #end subtitleExtract

 #displays mediainfo stuff for the tracks
 def parseCheckData(self,fname):
  titlewarn=0
  #infolist=self.metadata
  #vid
  vido=''
  if self.vidStreamCount != 1:
   vido= cPURPLE + '%d video streams! FLIP THE FUCK OUT!' % self.vidStreamCount + cRESET
   titlewarn+=1000
  else:
   if self.vidAR == '16:9':
    pass
   elif self.vidAR == '4:3':
    self.ffres= '-s 640x480 '
    vido= cYELLOW + self.vidAR
    titlewarn+=10
   else:
    vido= cYELLOW + self.vidAR + ', using 16:9'
    titlewarn+=10
  #aud
  audo=''
  if self.audStreamCount == 0:
   audo= cPURPLE + 'No audio streams! FLIP THE FUCK OUT!'
   titlewarn+=1000
  elif self.audStreamCount == 1:
   pass
  else:
   audo+= cYELLOW
   for y in range(len(self.metadata)):
    if self.metadata[y] == 'AUDID':
     audo+= 'Track %s: %s %s, ' % (self.metadata[y+1], self.metadata[y+3], self.metadata[y+5])
   titlewarn+=10
  #subs
  subo=''
  if self.textStreamCount == 0:
   subo+= cRED + 'No subtitle tracks detected'
   titlewarn+=10
  elif self.textStreamCount == 1:
   pass
  else:
   subo+= cYELLOW
   for y in range(len(self.metadata)):
    if self.metadata[y] == 'TEXTID':
     audo+= 'Track %s: %s, ' % (self.metadata[y+1], self.metadata[y+3])
   titlewarn+=10
  #check the warn level
  if titlewarn < 10:
   tWARN= cBLUE
  elif titlewarn < 100:
   tWARN= cYELLOW
  else:
   tWARN= cPURPLE
  #put the string together
  tWARN+= '##' + fname + '\n'
  if len(vido) > 0:
   vido+= '\n'
  if len(audo) > 0:
   audo+= '\n'
  if len(subo) > 0:
   subo+= '\n'
  return tWARN + vido + audo + subo + cRESET
  #end of check function
#end MKVStuff class
###################################################################

#gets file list of passed type
def getFileList(fext, *addext):
 flist=[]
 for x in listdir('./'):
  if x[-3:].lower() == fext:
   #print x
   flist.append(x)
 return flist
#end getFileList

#font path thing
def handleFontPath(fp):
 if isdir(fp):
  print cLBLUE + "Font dir (%s) exists; will not create." % fp + cRESET
 else:
  print cYELLOW + "Font dir does not exist; creating..." + cRESET
  try:
   makedirs(fp)
   print cLBLUE + "Font dir created at %s" % fp + cRESET
  except OSError:
   print cRED + "ERROR 01: Font Path Creation Failurization" +cRESET
#end handleFontPath

#handles fonts
def handleFonts(fname,paff):
 mkvearg=['mkvextract','attachments',fname]
 mvarg=['mv','-f']
 fontlist=[]
 for x in xrange(30):
  mkvearg.append(str(x+1))
 
 call(mkvearg,stdout=PIPE)

 for x in listdir('./'):
  y=x[-3:]
  if y.lower() == 'ttf' or y.lower() == 'ttc' or y.lower() == 'otf':
   fontlist.append(x)
 #print mvarg
 mvarg = mvarg + fontlist + [paff]
 if len(fontlist) > 0:
  call(mvarg)
#end handleFonts
def flipthefuckout():
 print cRED + "FLIPPING THE FUCK OUT!" + cRESET

#build the ffmpeg argument

def buildFFMPEGarg(fname,vID,aID,vfarg,fps,AR,aformat,res,extra,exten,ofi,loggy):
 vmap='-map 0:%d' % (vID-1)
 amap='-map 0:%d' % (aID-1)
 ffstr='ffmpeg -i "%s" %s %s %s -q 0 ' % (fname, vmap, amap, fps)
 if AR == '16:9':
#  ffstr=ffstr + '-s 704x400 '
  ffstr=ffstr + res
 elif AR == '4:3':
#  ffstr=ffstr + '-s 640x480 '
  ffstr=ffstr + res
 else:
  print cYELLOW + "ASPECT RATIO IS FUNKY! USING 16:9!" + cRESET
  ffstr=ffstr + '-s 704x400 '
 ffstr=ffstr + vfarg
 if aformat != "MPEG Audio":
  ffstr=ffstr + '-acodec libmp3lame -ab 128k -ac 2 -ar 44100 '
 else:
  ffstr=ffstr + '-acodec copy '
 ffstr=ffstr + extra + ' -f %s -y "passzero.%s" ' % (exten,exten) + loggy
 return ffstr
#end ffmpeg build

#straight mp4 encode argument
#this should really be part of the other ffmpeg build function
def buildFFMPEGargmp4(fname,vID,aID,vfarg,fps,AR,aformat,res,extra,outty,crf,loggy,lolerskates):
 vmap='-map 0:%d' % (vID-1)
 amap='-map 0:%d' % (aID-1)
 if lolerskates == 0:
  res='-s 1280x720'
 ffstr='ffmpeg -i "%s" %s %s %s -vcodec libx264 -crf %s %s ' % (fname, vmap, amap, fps, str(crf), res)
 ffstr=ffstr + vfarg
 ffstr=ffstr + '-acodec libfdk_aac -ab 128k -ac 2 -ar 48000 '
 ffstr=ffstr + extra + ' -f mp4 -y "%s" ' % outty + loggy
 return ffstr
#end ffmpeg build mp4

#build the mencoder arguments
def buildMencoderarg(passy, bitrate, loggy):
 if passy == 1:
  mencstr='mencoder "passzero.avi" -ovc xvid -o /dev/null -nosound '
  mencstr=mencstr + '-xvidencopts pass=1:cartoon:turbo:profile=asp5:trellis:threads=1:nopacked:bitrate=%d ' % bitrate + loggy
  return mencstr
 elif passy == 2:
  mencstr='mencoder "passzero.avi" -ovc xvid -o "passtwo.avi" -nosound '
  mencstr=mencstr + '-xvidencopts pass=2:cartoon:profile=asp5:trellis:threads=1:nopacked:bitrate=%d ' % bitrate + loggy
  return mencstr

#this cleans stuff out of the file name that we dont want
def cleanFileName(fname,exten):
 strlen=len(fname)
 fname=fname.replace('.',' ')
 fname=fname.replace('_',' ')
 #haha almost did this the hard way
 if fname.count('(') == fname.count(')') and fname.count('(') > 0:
  fname=fname.replace('(','[')
  fname=fname.replace(')',']')
 #brackets
 brackopen=fname.count('[')
 brackclose=fname.count(']')
 if brackclose == brackopen and brackopen > 1:
  aftergroup=fname[(fname.index(']')+1):]
  for x in range(aftergroup.count('[')):
   b1=aftergroup.index('[')
   b2=aftergroup.index(']')+1
   aftergroup=aftergroup.replace(aftergroup[b1:b2],'')
 try:
  fname=fname[:(fname.index(']')+1)] + aftergroup
 except:
  pass
 fname=fname.rstrip().strip()

 return fname + '.' + exten

#begin the file handling loop
def fileloop(vidfile,*pipey):
#for fi in filelist:

 outtye='avi'

 if '--oext' in sys.argv:
  try:
   outtye=sys.argv[sys.argv.index('--oext')+1]
  except:
   pass
 elif '-o' in sys.argv:
  try:
   outtye=sys.argv[sys.argv.index('-o')+1]
  except:
   pass
 finalstatus=''
 mkvthing = FileStuff() 
 mkvthing.getMetadata(vidfile)

 vc=mkvthing.getVideoStreams()
 mkvthing.getVideoMetadata()
 ac=mkvthing.getAudioMetadata(mkvthing.getAudioStreams())

 #get the metadata for the text stream 
 mkvthing.getTextMetadata(mkvthing.getTextStreams())

 statusy= mkvthing.parseCheckData(vidfile)
 print statusy
 finalstatus+= statusy
 if CHECKY == True:
  return
 if ac == 0 or vc != 1:
  return
 #now that we wont FTFO anymore i can try to change the filename
 outfile=cleanFileName(vidfile[:-4],outtye)
 
 if inext == 'mkv':
  handleFonts(vidfile,fontpath)
  #extract subtitles
  mkvthing.subtitleExtract(vidfile)

 #check for bitrate override
 if '-b' in sys.argv:
  try:
   mkvthing.mebitrate=int(sys.argv[sys.argv.index('-b')+1])
  except:
   pass
 elif '--bitrate' in sys.argv:
  try:
   mkvthing.mebitrate=int(sys.argv[sys.argv.index('--bitrate')+1])
  except:
   pass

 rescheck=0
 #check for resolution override
 if '-r' in sys.argv:
  try:
   mkvthing.ffres='-s %s ' % sys.argv[sys.argv.index('-r')+1]
   rescheck=1
  except:
   pass
 elif '--resolution' in sys.argv:
  try:
   mkvthing.ffres='-s %s ' % sys.argv[sys.argv.index('--resolution')+1]
   rescheck=1
  except:
   pass

 #check for fps override and get total frame count
 srcfrms=int(check_output('mediainfo --inform="Video;%%Duration%%" "%s"' % vidfile,shell=True)[:-1])
 if '-fps' in sys.argv:
  try:
   overridefps=sys.argv[sys.argv.index('-fps')+1]
   mkvthing.fffps='-r %s ' % overridefps
   mkvthing.targetframecount=int((srcfrms/1000.0)*overridefps)+1
  except:
   pass
 else:
  mkvthing.targetframecount=int((srcfrms/1000.0)*23.976)+1

 #check for crf override
 if '-crf' in sys.argv:
  try:
   mkvthing.ffcrf=sys.argv[sys.argv.index('-crf')+1]
  except:
   pass

 logcheck=0
 #checks for log argument
 if '-l' in sys.argv or '--logfile' in sys.argv or '-tl' in sys.argv:
  try:
   mkvthing.fflog="2> %s" % logfname
   mkvthing.meextra=">> %s" % logfname
   mkvthing.fflog2="2>> %s" %logfname
   logcheck=1
  except:
   logcheck=2
   #lol i dunno

 #check for extra args
 if '-x' in sys.argv:
  try:
   mkvthing.ffextra=mkvthing.ffextra + sys.argv[sys.argv.index('-x')+1]
  except:
   pass

  #send the command to start reporting to the reporting daemon if there is a pipe available
 if pipey:
  pipey=pipey[0]
  try:
   pipey.send([mkvthing.targetframecount,outfile])
  except:
   #no pipe
   pass

 #build the ffmpeg args and stuff
 if outtye == 'avi':
  if pipey:
   pipey.send(4)
  ffmpegarg=buildFFMPEGarg(vidfile, mkvthing.vidID, mkvthing.audID, mkvthing.ffvfarg, mkvthing.fffps, mkvthing.vidAR, mkvthing.audFormat, mkvthing.ffres, mkvthing.ffextra,outtye,outfile,mkvthing.fflog)
  mencoderarg=buildMencoderarg(1,mkvthing.mebitrate,mkvthing.meextra)
  mencoderarg2=buildMencoderarg(2,mkvthing.mebitrate,mkvthing.meextra)
  #send pass 1
  if pipey:
   pipey.send(1)
  call(ffmpegarg,shell=True)
  if isfile('./passzero.avi'):
   #send pass 2
   if pipey:
    pipey.send(2)
   call(mencoderarg,shell=True)
   #send pass 3
   if pipey:
    pipey.send(3)
   call(mencoderarg2,shell=True)
   if isfile('./passtwo.avi'):
    #send pass 4
    if pipey:
     pipey.send(4)
    call('ffmpeg -i "passtwo.avi" -i "passzero.avi" -map 0:0 -map 1:1 -vcodec copy -acodec copy -f avi -y "%s" %s' % (outfile,mkvthing.fflog2),shell=True)
    #send pass 5 (finished)
    if pipey:
     pipey.send(5)
   else:
    print cRED + "mencoder pass(es) (one/two) failed" + cRESET
  else:
   print cRED + "FFMPEG pass (zero) failed" + cRESET
 elif outtye == 'mp4':
  if pipey:
   pipey.send(1)
  ffmpegarg=buildFFMPEGargmp4(vidfile, mkvthing.vidID, mkvthing.audID, mkvthing.ffvfarg, mkvthing.fffps, mkvthing.vidAR, mkvthing.audFormat, mkvthing.ffres, mkvthing.ffextra,outfile,mkvthing.ffcrf,mkvthing.fflog,rescheck)
  #send pass 1
  if pipey:
   pipey.send(1)
  call(ffmpegarg,shell=True)
  #send pass 5 (finished)
  if pipey:
   pipey.send(5)
 #cleanup
 call(['rm','sobs.ass','sobs.srt','passzero.avi','passtwo.avi','divx2pass.log'],stderr=None)
 if '--move' in sys.argv:
  try:
   move(outfile,sys.argv[sys.argv.index('--move')+1])
  except:
   print cRED + "Can't move %s to %s!" % (outfile,sys.argv[sys.argv.index('--move')+1]) + cRESET
 elif '-m' in sys.argv:
  try:
   move(outfile,sys.argv[sys.argv.index('-m')+1])
  except:
   print cRED + "Can't move %s to %s!" % (outfile,sys.argv[sys.argv.index('-m')+1]) + cRESET

 if CHECKY != 1:
  print finalstatus
#end the file loop thing
	
#description
def getArgvFromFile(inny):
 with open(inny, "r") as fo:
  x=fo.readline()
 if '\n' in x[-1:]:
  x=x[:-1]
 if '|' in x:
  mkvname,argy=str.split(x,"|")
 else:
  mkvname=x
 try:
  sys.argv=[__file__] + str.split(argy," ")
 except:
  sys.argv=[__file__]
 return mkvname

def getNextItemInQueue(inny):
 with open(inny, "r") as fo:
  x=fo.readlines()
 if len(x) == 0:
  return 0
 with open(inny, "w") as fo:
  for y in x[1:]:
   fo.write(y)
 return 1

#brutally murders the encoding process, ffmpeg, and mencoder
def KillMeBaby(processy):
 print cPURPLE + "KILLING ENCODE" + cRESET
 try:
  processy.terminate()
 except:
  print cYELLOW + "Error killing encode process, process already dead or worse" + cRESET
 call(['pkill','ffmpeg'])
 call(['pkill','mencoder'])
 print cRED + "RIP IN PIECE" + cRESET

#writes arg to the progress log file
def filemebaby(printmebaby):
 with open(reportlog,"w") as filey:
  filey.write(printmebaby)

#i dunno
def parselog():
 return filter(None,check_output("cat %s | sed -e 's/\\r/\\n/g' | tail -1" % logfname,shell=True)[:-1].split(' '))

#formats time from seconds to mm:ss
def timeformat(sex):
 minz=sex/60
 sex=sex-minz*60
 if minz < 10:
  minz='0' + str(minz)
 else:
  minz=str(minz)
 if sex < 10:
  sex='0' + str(sex)
 else:
  sex=str(sex)
 return minz + ":" + sex

def formatparse(currframe,fps,mframes,oname,cpass,mpass):
 currframe=str(currframe)
 fps=str(int(round(float(fps),0)))
 perc=str(round(float(currframe)/float(mframes)*100.0,1)) + "%"
 tleft=(mframes-int(currframe))/int(fps)
 return oname + '|' + perc + '|' + str(cpass) + '/' + str(mpass) + '|' + fps + '|' + currframe + '/' + str(mframes) + '|' + timeformat(tleft)

#this is the reportey function that runs in a process parallel to fileloop
#Pass: x/n   Frame: x/n   Time left: xxm:xxs
#xx.x%   xxxxxxxxx.out
#filename|%|pass|frame|time
def reportDaemon(pipey):
 currpass=0
 call(['rm',reportlog])
 filemebaby("STARTING ENCODE")
 maxframes,outfname=pipey.recv()
 passes=pipey.recv()

 ##AVI PASSES
 if passes == 4:
  while not pipey.poll():
   #wait for the pass number to come down the pipe
   sleep(.25)
  currpass=pipey.recv()
  filemebaby("CACHING FONTS")
  while currpass==1:
   parsey=parselog()[0:4]
   if 'frame=' in parsey:
    try:
     reporty=formatparse(parsey[1],parsey[3],maxframes,outfname,currpass,passes)
     filemebaby(reporty)
     print reporty
    except:
     filemebaby("Parse error @ %s" % parsey[1])
     print "Parse error @ %s" % parsey[1]
   sleep(logreportupdate)
   #check to see if encoder is passing the next pass
   if pipey.poll():
    currpass=pipey.recv()
  
  while currpass==2 or currpass==3:
   parsey=parselog()[0:5]
   if 'Pos:' in parsey:
    try:
     reporty=formatparse(parsey[2][:-1],parsey[4][:-3],maxframes,outfname,currpass,passes)
     filemebaby(reporty)
     print reporty
    except:
     filemebaby("Parse error @ %s" % parsey[2])
     print "Parse error @ %s" % parsey[2]
   sleep(logreportupdate)
   if pipey.poll():
    currpass=pipey.recv()
 
  while currpass==4:
   parsey=parselog()[0:4]
   if 'frame=' in parsey:
    try:
     reporty=formatparse(parsey[1],parsey[3],maxframes,outfname,currpass,passes)
     filemebaby(reporty)
     print reporty
    except:
     filemebaby("Parse error @ %s" % parsey[1])
     print "Parse error @ %s" % parsey[1]
   sleep(logreportupdate)
   #check to see if encoder is passing the next pass
   if pipey.poll():
    currpass=pipey.recv()

 ##MP4 PASS
 elif passes == 1:
  currpass=pipey.recv()
  sleep(2)
  while currpass==1:
   parsey=parseffmpeglog()
   if 'frame=' in parsey:
    try:
     reporty=formatparse(parsey[1],parsey[3],maxframes,outfname,currpass,passes)
     filemebaby(reporty)
     print reporty
    except:
     filemebaby("Parse error @ %s" % parsey[1])
     print "Parse error @ %s" % parsey[1]
   sleep(logreportupdate)
   #check for pass update
   if pipey.poll():
    currpass=pipey.recv()
 filemebaby("FINISHED %s" % outfname)
 #KillMeBaby(eproc)

#########################################
#  *MAIN*				#
#	lol				#
#########################################
checkNecessaryFiles()
CHECKY=False #has nothing to do with the checkNecessaryFiles function
inext='mkv'
outext='avi'
filelist=[]
inqueue=0
txtfile=''
fontpath=expanduser('~/.fonts')
ffmpegarg=''
mencoderarg=''


if '--help' in sys.argv or '-?' in sys.argv or '-h' in sys.argv:
 exit(helpy())
elif '--check' in sys.argv or '-c' in sys.argv:
 CHECKY=True
if '--inext' in sys.argv:
 try:
  inext=sys.argv[sys.argv.index('--inext')+1]
 except:
  pass
elif '-i' in sys.argv:
 try:
  inext=sys.argv[sys.argv.index('-i')+1]
 except:
  pass

#gets the input queue file or individual video file name from the arguments
#queue must be a txt file
#video files must not be a txt file 
if '--filename' in sys.argv:
 if sys.argv[sys.argv.index('--filename')+1][-3:] == 'txt':
  inqueue=1
  txtfile=sys.argv[sys.argv.index('--filename')+1]
 elif sys.argv[sys.argv.index('--filename')+1][-3:] != 'txt':
  filelist=[sys.argv[sys.argv.index('-f')+1]]
elif '-f' in sys.argv:
 if sys.argv[sys.argv.index('-f')+1][-3:] == 'txt':
  inqueue=1
  txtfile=sys.argv[sys.argv.index('-f')+1]
 elif sys.argv[sys.argv.index('-f')+1][-3:] != 'txt':
  filelist=[sys.argv[sys.argv.index('-f')+1]]
else:
 filelist=getFileList(inext)

#yes this one is already in the fileloop function
if '--oext' in sys.argv:
 try:
  outext=sys.argv[sys.argv.index('--oext')+1]
 except:
  pass
elif '-o' in sys.argv:
 try:
  outext=sys.argv[sys.argv.index('-o')+1]
 except:
  pass

if outext != 'avi' and outext != 'mp4':
 sys.exit(cPURPLE + "%s is an invalid output extension!" % outext + cRESET)

if len(filelist) == 0 and inqueue==0:
 exit(cPURPLE + "No files to reencode with extension %s" % inext + cRESET)

handleFontPath(fontpath)

if inqueue==0:
 for fi in filelist:
  fileloop(fi)
  if '-tl' in sys.argv:
   call(['rm',logfname])
else:
 while inqueue==1:
  Qtop=getArgvFromFile(txtfile)
  if Qtop != '':
   #multiprocessing starts here
   epipe,rpipe=multiprocessing.Pipe()
   eproc=multiprocessing.Process(name='Encoder', target=fileloop, args=(Qtop,epipe,))
   #start the encoding process
   eproc.start()
   rproc=multiprocessing.Process(name='Reporter',target=reportDaemon, args=(rpipe,))
   rproc.daemon=True
   rproc.start()
   #lock to encoder
   eproc.join()
   sleep(.666)
   #kill reporter
   rproc.terminate()
   while rproc.is_alive():
    sleep(.1)
   if '-tl' in sys.argv:
    call(['rm',logfname])
  inqueue=getNextItemInQueue(txtfile)
