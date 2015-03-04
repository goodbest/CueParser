import cueparser as cp
import csv, sqlite3
import sys
import os
reload(sys)
sys.setdefaultencoding("utf-8")

CDoffset={}
CDoffset['KSLA-0005']=26
CDoffset['KSLA-0013']=20
CDoffset['KSLA-0014']=37
CDoffset['KSLA-0017']=10
CDoffset['KSLA-0024']=10
CDoffset['KSLA-0031']=7
CDoffset['KSLA-0034']=20
CDoffset['KSLA-0035']=40
CDoffset['KSLA-0040']=8
CDoffset['KSLA-0046']=17
CDoffset['KSLA-0060']=27
CDoffset['KSLA-0062']=14
CDoffset['KSLA-0063']=30
CDoffset['KSLA-0074']=22
CDoffset['KSLA-0075']=45
CDoffset['KSLA-0083']=12

CDTrack={}
CDTrack['KSLA-0004']=26
CDTrack['KSLA-0012']=20
CDTrack['KSLA-0013']=17
CDTrack['KSLA-0016']=10
CDTrack['KSLA-0023']=10
CDTrack['KSLA-0030']=7
CDTrack['KSLA-0033']=20
CDTrack['KSLA-0034']=20
CDTrack['KSLA-0039']=8
CDTrack['KSLA-0045']=17
CDTrack['KSLA-0059']=27
CDTrack['KSLA-0061']=14
CDTrack['KSLA-0062']=16
CDTrack['KSLA-0073']=22
CDTrack['KSLA-0074']=23
CDTrack['KSLA-0082']=12


conn = sqlite3.connect("::memory::")
curs = conn.cursor()
curs.execute("DROP TABLE IF EXISTS ksl_itunes;")
curs.execute("CREATE TABLE ksl_itunes (title TEXT, playtime TIME, songwriter TEXT, track INTEGER, trackcount INTEGER, performer TEXT, genre TEXT, album TEXT, comment TEXT);")
reader = csv.reader(open('ksl_itunes.txt', 'r'), delimiter='\t')
for row in reader:
    trackinfo=row[3].split('/')
    
    if row[7] in CDoffset:
        if row[7] in CDTrack:
            to_db = [unicode(row[0], "utf8"), unicode(row[1], "utf8"), unicode(row[2], "utf8"), int(trackinfo[0]) - CDoffset[row[7]], CDTrack[row[7]], unicode(row[4], "utf8"), unicode(row[5], "utf8"), unicode(row[6], "utf8"), unicode(row[7], "utf8")]
        else:
            to_db = [unicode(row[0], "utf8"), unicode(row[1], "utf8"), unicode(row[2], "utf8"), int(trackinfo[0]) - CDoffset[row[7]], int(trackinfo[1]) - CDoffset[row[7]], unicode(row[4], "utf8"), unicode(row[5], "utf8"), unicode(row[6], "utf8"), unicode(row[7], "utf8")]
    else:
        if row[7] in CDTrack:
            to_db = [unicode(row[0], "utf8"), unicode(row[1], "utf8"), unicode(row[2], "utf8"), int(trackinfo[0]), CDTrack[row[7]], unicode(row[4], "utf8"), unicode(row[5], "utf8"), unicode(row[6], "utf8"), unicode(row[7], "utf8")]
        else:
            to_db = [unicode(row[0], "utf8"), unicode(row[1], "utf8"), unicode(row[2], "utf8"), int(trackinfo[0]), int(trackinfo[1]), unicode(row[4], "utf8"), unicode(row[5], "utf8"), unicode(row[6], "utf8"), unicode(row[7], "utf8")]
            
    curs.execute("INSERT INTO ksl_itunes (title, playtime, songwriter, track, trackcount, performer, genre, album, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
conn.commit()


header = '%rem%\n' + \
    'PERFORMER "%performer%"\n' + \
    'SONGWRITER "%songwriter%"\n' +\
    'TITLE "%title%"\n' + \
    'FILE "%file%" %format%\n'+ \
    '%tracks%'

track='  TRACK %number% AUDIO\n' + \
    '    TITLE "%title%"\n' + \
    '    PERFORMER "%performer%"\n' + \
    '    SONGWRITER "%songwriter%"\n' + \
    '    INDEX %index% %offset%'


conn = sqlite3.connect("::memory::")
curs = conn.cursor()

for file in os.listdir('.'):
    if file.find('.cue')>-1:
        cuesheet = cp.CueSheet()
        cuesheet.setOutputFormat(header, track)
        cuefile=file
        SN=file.replace('.cue','')
        with open(cuefile, "r") as f:
            cuesheet.setData(f.read())
            cuesheet.parse()

            conn = sqlite3.connect("::memory::")
            curs = conn.cursor()

            for track in cuesheet.tracks:
                curs.execute("select * from ksl_itunes where track=%s and comment='%s';"%(int(track.number), SN)) #%(unicode(track.title, "utf8")))
                result=curs.fetchone()
                if result:
                    if track.title != result[0]:
                        print '%s\t%s\t%s\t%s' %(result[8], track.number, track.title, result[0])
                    if result[2]:
                        track.songwriter=result[2]
                    else:
                        track.songwriter=''
                    # else:
 #                        print '%d %d' %(len(cuesheet.tracks), result[4])
                else:
                    print '%sr\t%s not in itunes' %(SN, track.title)
        #print result[2]
        #print track.songwriter
        #print track.title

        #print(cuesheet.output())

#TODO many index

