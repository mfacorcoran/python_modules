from bs4 import BeautifulSoup
import urllib2
import subprocess
import os
import glob
import webbrowser


def astroupdate_dict2(url="http://heasarc.gsfc.nasa.gov/docs/heasarc/astro-update/"):
    response = urllib2.urlopen('http://heasarc.gsfc.nasa.gov/docs/heasarc/astro-update/')
    html=response.read()
    soup=BeautifulSoup(''.join(html))
    table=soup.findAll('table')
    soft_table=table[1] # there are 3 tables on the page, the software version table is the 2nd table
    rows = soft_table.findAll('tr')
    au_dict=dict()
    for row in rows[1:]:
        cols = row.findAll('td')
        n   =''.join(cols[0].find(text=True))
        r   =''.join(cols[1].find(text=True))
        v   =''.join(cols[2].find(text=True))
        m   =''.join(cols[3].find(text=True))
        au_dict[n]=(v,m,r)
    return au_dict

def astroupdate_dict(url="http://heasarc.gsfc.nasa.gov/docs/heasarc/astro-update/"):
    response = urllib2.urlopen('http://heasarc.gsfc.nasa.gov/docs/heasarc/astro-update/')
    html=response.read()
    soup=BeautifulSoup(''.join(html))
    table=soup.findAll('table')
    soft_table=table[1] # there are 3 tables on the page, the software version table is the 2nd table
    rows = soft_table.findAll('tr')
    au_dict=dict()
    for row in rows[1:]:
        cols = row.findAll('td')
        n   =''.join(cols[0].find(text=True))
        r   =''.join(cols[1].find(text=True))
        v   =''.join(cols[2].find(text=True))
        uurl=cols[2].find("a") # get the url pointing to the software download page
        u   =''.join(uurl.attrs['href'])
        m   =''.join(cols[3].find(text=True))
        au_dict[str(n).lower().strip()]={'Version':str(v),'Date':str(m),'Author':str(r), 'URL': str(u)}
    return au_dict


def astroupdate(software, chatter=0):
    aud=astroupdate_dict()
    softkey=software.strip().lower()
    try:
        aud[softkey]
        if chatter > 0:
            print "{0} was last updated to version {1} on {2} by {3}".format(software,
                                                                         aud[software]['Version'],
                                                                         aud[software]['Date'],
                                                                         aud[software]['Author'])
        ver = str(aud[softkey]['Version'])
        date = str(aud[softkey]['Date'])
        author = str(aud[softkey]['Author'])
        updateurl = str(aud[softkey]['URL'])
        return ver, date, author, updateurl
    except KeyError:
        print "%s not monitored by Astro-Update" % software
        print "Valid entries are:"
        print aud.keys()


def auto_update(software):
    current_vers, moddate, resp, updateurl = astroupdate(software.strip().lower())

    if software=="HEASoft":
        fver_installed = subprocess.check_output(['fversion'])
        vers=fver_installed.strip("\n").split('_V')
        vers=vers[1].rstrip()
        print "Latest version of  HEASoft = %s; You currently have HEASoft version %s" % (current_vers, vers)
        if current_vers.strip()<> vers.strip():
            ans=''
            ans=raw_input("Would you like to update (Y/n)? ")
            if ans.strip()=='' or ans[0].lower()=='y':
                print "Opening HEASoft download page in your web browser"
                #webbrowser.open('http://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download.html')
                webbrowser.open(updateurl)

    if software=='SAE':
        fermidir=os.getenv('FERMI_DIR')
        if not fermidir:
            print "Environment variable $FERMI_DIR is not defined; stopping"
            return
        STools= glob.glob(fermidir+'/../../ScienceTools*') # Find Science Tools directory
        #print STools
        if not STools:
            print "Problem finding {0}".format(fermidir+'/../..')
            return
        SToolsver=STools[0].split('Tools-')[1].split('-fssc')[0]
        #print SToolsver
        print "The current version of the Science Analysis Environment for Fermi is {0}; you have version {1}".format(current_vers.strip(), SToolsver.strip())
        if current_vers<>SToolsver:
            ans=''
            ans=raw_input("Would you like to update (Y/n)? ")
            if ans.strip()=='' or ans[0].lower()=='y':
                print "Opening Fermi SAE download page in your web browser"
                #webbrowser.open('http://fermi.gsfc.nasa.gov/ssc/data/analysis/software/')
                webbrowser.open(updateurl)
    return

