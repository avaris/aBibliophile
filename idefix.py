# -.- encoding: utf-8 -.-
import urllib
from BeautifulSoup import BeautifulSoup, NavigableString, Comment

def CleanString(s):
    return s.replace("\r","").replace("\n"," ").replace("  "," ").strip().encode("utf-8")

def SearchBooksWithName(Data,ProgressHook): #ProgressHook(min,max,value) : Progress function
    results = 1
    page_no = 1
    titles  = []
    while len(titles)<results:
        Data["sayfa"]=str(page_no)
        link = "http://www.idefix.com/kitap/arama_sonuc.asp"
        page = BeautifulSoup(urllib.urlopen(link,urllib.urlencode(Data)),convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        if page_no == 1:
            if page.find("span",{"class":"fiyat"}):
                return []
            results = int(page.findAll("div",{"class":"contenttitle"})[1]
                          .findAll("b")[-2]
                          .text)
        
        for x in page.findAll("td",{"class":"listeinside"}):
            title     = CleanString(x.find("div",{"class":"listeurun"}).a["title"])
            url       = "http://www.idefix.com/"+x.find("div",{"class":"listeurun"}).a["href"]
            writer    = ",".join(CleanString(yazar.text) for yazar in x.findAll("a",recursive=False))
            publisher = CleanString(x.i.text)

            titles.append({"title"    : title,
                           "url"      : url,
                           "writer"   : writer,
                           "publisher": publisher})


        ProgressHook(0,results,len(titles))
        page_no += 1
    return titles

def SearchBooksWithKeyword(SearchTerm,ProgressHook):
    results = 1
    page_no = 1
    titles = []
    while len(titles)<results:
        link = "http://www.idefix.com/vitrin/aramasonuc.asp?Shop=1&Page="+str(page_no)+"&SearchTerm="+urllib.quote(SearchTerm)

        page = BeautifulSoup(urllib.urlopen(link),convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        if page_no == 1:
            results = int(page.find("a",{"class":"aramasiyah"})
                          .b
                          .contents[0]
                          .split("(")[1][:-1])
        
        for x in page.findAll("td",{"class":"listeinside"}):
            title     = CleanString(x.find("div",{"class":"listeurun"}).a["title"])
            url       = "http://www.idefix.com/"+x.find("div",{"class":"listeurun"}).a["href"]
            writer    = ",".join(CleanString(yazar.text) for yazar in x.findAll("a",recursive=False))
            publisher = CleanString(x.i.text)

            titles.append({"title"    : title,
                           "url"      : url,
                           "writer"   : writer,
                           "publisher": publisher})
        ProgressHook(0,results,len(titles))
        page_no += 1
    return titles

def DownloadBookInfo(url):
    page = BeautifulSoup(urllib.urlopen(url),convertEntities=BeautifulSoup.HTML_ENTITIES)

    if page.find("img",{"src":"http://static.ideefixe.com/images/idee_resimsiz.gif"}): # kitap resmi yok
        image_path = ""
    else:
        image_url = page.find("a",{"class":"thickbox"})["href"]
        image_path = "tmp/"+image_url.split("/")[-1]
        urllib.urlretrieve(image_url,image_path)
    title = CleanString(page.find("div",{"class":"boxTanimisim"}).div.contents[0])
    writers = "|".join([CleanString(x.contents[0]) for x in  page.find("h2",{"class":"boxTanimesersah"}).findAll("a")])
    publisher = CleanString(page.find("h3",{"class":"boxTanimyayinevi"}).a.b.contents[0])
    if page.find(id="tanimimagesfix"):
        excerpt = "".join((CleanString(x) if isinstance(x,NavigableString)
                           else " "+CleanString(x.text)+" " if x.name!="br" else "\n") for x in page.find(id="tanimimagesfix").contents)
    else:
        excerpt = ""
    categories = "|".join([" / ".join([CleanString(c.text) for c in cat.findAll("a")]) for cat in page.findAll("div",{"style":"float:left;display:inline;padding:1px;"})])

    c=1
    for x in page.find(id="tanitimbox").contents:
        if isinstance(x,NavigableString) and not isinstance(x,Comment) and x.strip():
            if c==1:
                language=CleanString(x.strip().split()[0])
            elif c==2:
                pages = x.strip().split()[0]
            else:
                break
            c += 1

    return {"title":title,
            "writers":writers,
            "publisher":publisher,
            "excerpt":excerpt,
            "categories":categories,
            "language":language,
            "pages":pages,
            "image_path":image_path}

