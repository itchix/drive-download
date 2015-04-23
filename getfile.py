# -\*- coding: utf-8 -\*-

import os, sys
from urllib2 import urlopen, URLError, HTTPError
from lxml import html
import json
import argparse

def dlfile(url, path,  name, verbose):
    try:
        f = urlopen(url)
        if verbose != 0:
            print "downloading " + url

        with open(os.path.join(path, name), "wb") as local_file:
            local_file.write(f.read())

    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url

def main(w, t, v):

    response = urlopen(w)
    headers = response.info()
    data = response.read()

    if v == 2:
        print 'RESPONSE:', response
        print 'URL     :', response.geturl()
        print 'DATE    :', headers['date']
        print 'HEADERS :'
        print '---------'
        print headers
        print 'LENGTH  :', len(data)
        print 'DATA    :'
        print '---------'
        print data

    tree = html.fromstring(data)
    id = tree.xpath("//div[@class='flip-entry']/@id")
    name = tree.xpath("//div[@class='flip-entry-title']/text()")
    title = tree.xpath("//div[@class='flip-folder-title']/span[@role=\"heading\"]/text()")
    img = tree.xpath("//div[@class='flip-entry-thumb']/img/@src")
    nomSousDossier = tree.xpath("//div[@class='flip-entry-icon']/div[@aria-label='Dossier']")

    try:
        if not os.path.exists(title[0]):
           os.makedirs(title[0])
    except OSError:
        pass

    nbSsDossier = len(nomSousDossier)
    print nbSsDossier

    i = 0
    if t == "img":
        for oneimg in img:
            print '---------- FETCH IMG -----------'
            oneimg = oneimg[:-5]
            dlfile(oneimg,title[0],name[i],v)
            i += 1

    i = 0
    if t == "pdf":
        id = id[nbSsDossier:]
        name = name[nbSsDossier:]
        for oneid in id:
            print '---------- FETCH PDF/TXT -----------'
            oneid = oneid[6:]
            response2 = urlopen('https://drive.google.com/st/viewurls?id=' + oneid + '&m=1440')
            data2 = response2.read()
            data2 = data2[12:-2]
            data2 = data2.replace("\u0026","&")
            data2 = data2.replace("\u003d","=")
            response3 = urlopen(data2)
            data3 = response3.read()
            data3 = data3[4:]
            parsed_json = json.loads(data3)
            dlfile(parsed_json[t],title[0],name[i],v)
            i += 1

    print '------------------------------------'
    print '-------------- FINISH --------------'
    sys.exit


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('w', help="Put you drive folder link")
    parser.add_argument('-v', '--verbose', help="Verbose mode (0,1,2) : Default 1", choices=[0,1,2], type=int, default="1", action="store")
    parser.add_argument('-t', '--type', help="Put the type of files you want to fetch (default type : doc/txt/pdf)", default="pdf", action="store", choices=["pdf", "zip", "all", "img"])
    args = parser.parse_args()
    main(args.w, args.type, args.verbose)
