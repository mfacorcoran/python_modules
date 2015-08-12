from bs4 import BeautifulSoup
import urllib2
import subprocess
import os
import glob
import webbrowser


def astroupdate_dict(url="http://heasarc.gsfc.nasa.gov/docs/heasarc/astro-update/"):
    """
    Creates a python dictionary based on the software version table in astro-update
    :param url:
    :return:
    """
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
    """
    If a specified software package is monitored in astro-update,
    this will returen the current version, date of last update, the
    software author, and the url to download the latest update

    :param software: name of software package to check
    :param chatter: verbosity
    :return:
    """
    aud=astroupdate_dict()
    softkey=software.strip().lower()
    try:
        aud[softkey]
    except KeyError:
        print "%s not monitored by Astro-Update" % software
        print "Valid entries are:"
        print aud.keys()
        return 0
    if chatter > 0:
        print "{0} was last updated to version {1} on {2} by {3}".format(software,
                                                                     aud[software]['Version'],
                                                                     aud[software]['Date'],
                                                                     aud[software]['Author'])
    """
    ver = str(aud[softkey]['Version'])
    date = str(aud[softkey]['Date'])
    author = str(aud[softkey]['Author'])
    updateurl = str(aud[softkey]['URL'])
    return ver, date, author, updateurl
    """
    return aud[softkey]



def auto_update(software):
    """
    for the specified software, notify the user if their installed version is up-to-date; if not,
    give the user the option of downloading the latest version (by taking the user to the
    software download page in their web browser)

    :param software: name of software to check
    :return:
    """
    ad = astroupdate_dict()
    software = software.strip().lower()
    try:
        current_vers = ad[software]['Version']
    except:
        print "{0} not found in Astro-Update Database; returning".format(software)
        return
    updateurl = ad[software]["URL"]
    if software=="heasoft":
        headasdir = os.getenv('HEADAS')
        if not headasdir:
            print "Environment variable $HEADAS is not defined; stopping"
            return
        try:
            fver_installed = subprocess.check_output(['fversion'])
        except:
            print "fversion failed; is HEASoft installed?"
            return
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

    if software=='sae':
        fermidir=os.getenv('FERMI_DIR')
        if not fermidir:
            print "Environment variable $FERMI_DIR is not defined; stopping"
            return
        STools= glob.glob(fermidir+'/../../ScienceTools*') # Find Science Tools directory
        #print STools
        if not STools:
            print "Problem finding {0}".format(fermidir+'/../..')
            return
        vers=STools[0].split('Tools-')[1].split('-fssc')[0].strip()
        #print SToolsver
        print "The current version of the Science Analysis Environment for Fermi is {0}; you have version {1}".format(current_vers.strip(), vers.strip())
        if current_vers<>vers:
            ans=raw_input("Would you like to update (Y/n)? ")
            if ans.strip()=='' or ans[0].lower()=='y':
                print "Opening Fermi SAE download page in your web browser"
                #webbrowser.open('http://fermi.gsfc.nasa.gov/ssc/data/analysis/software/')
                webbrowser.open(updateurl)

    if software =='xspec':
        headasdir = os.getenv('HEADAS')
        if not headasdir:
            print "Environment variable $HEADAS is not defined; stopping"
            return
        """
        Get installed primary version number from locally installed manual.html; this is defined as a constant in
        the file $HEADAS/../Xspec/src/XSUtil/Utils/XSutility.cxx in a line like this: static const string version = "12.9.0b";
        """
        xsutil=headasdir+'/../Xspec/src/XSUtil/Utils/XSutility.cxx'
        f=open(xsutil,'r')
        for line in f.readlines():
            #print line
            if 'version =' in line:
                #print line
                vers = line.split('=')[1].strip().split('"')[1]
                #print 'Vers = {0}'.format(vers.strip())
                foundversion=True
                break
        f.close()
        if not foundversion:
            print "Could not find local XSpec version; stopping"
            return
        print "The current version of XSpec is {0}; you have version {1}".format(current_vers.strip(), vers.strip())
        if current_vers<>vers:
            ans=raw_input("Would you like to update (Y/n)? ")
            if ans.strip()=='' or ans[0].lower()=='y':
                print "Opening the XSpec download page in your web browser"
                #webbrowser.open('http://fermi.gsfc.nasa.gov/ssc/data/analysis/software/')
                webbrowser.open(updateurl)

    if software == 'ciao':
        ascds = os.getenv('ASCDS_INSTALL')
        if not ascds:
            print "Environment variable $ASCDS_INSTALL is not defined; stopping"
            return
        os.system(ascds+'/contrib/bin/check_ciao_version')

    return


