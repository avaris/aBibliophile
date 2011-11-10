from lxml import html
import urllib

def GetBookDetails(url):
    parsed_page = html.parse(urllib.urlopen(url))

    book_names = parsed_page.xpath("//div[@class='boxTanimisim']/div")
    book_details = [x.strip() for x in parsed_page.xpath("//div[@id='tanitimbox']/text()") if x.strip()]    
    book_title = " ".join(book_names[0].text.split())
    #book_title_original = "" if len(book_names)<2 else book_names[-1].text.split(": ",1)[1].splitlines()[0]
    book_writers = [x.text for x in parsed_page.xpath("//h2[@class='boxTanimesersah']//a")]
    book_publisher = parsed_page.xpath("//h3[@class='boxTanimyayinevi']//a")[0].text_content()
    book_categories = [x.text_content().strip() for x in parsed_page.xpath("//ul[@class='aliste']/li/div[1]")]
    book_excerpt_div = parsed_page.xpath("//div[@id='tanimimagesfix']")
    if book_excerpt_div:
        book_excerpt = "".join("\n" if isinstance(el,html.HtmlElement) else el.strip() for el in book_excerpt_div[0].xpath("./br|./text()"))
    else:
        book_excerpt = ""
    book_language = book_details[0].split()[0]
    book_pages = book_details[1].split()[0]
    book_cover = parsed_page.xpath("//div[@class='tanimsol']/a[@class='thickbox']")
    book_cover_url = book_cover[0].get("href") if book_cover else ""

    return {"title":book_title,
            #"title_original":book_title_original,
            "writers":book_writers,
            "publisher":book_publisher,
            "categories":book_categories,
            "excerpt":book_excerpt,
            "language":book_language,
            "pages":book_pages,
            "cover_url":book_cover_url}

def SearchBook(keyword="", title="", writer="", hook=None):
    results = 1
    page_no = 1
    titles  = []
    while len(titles) < results:
        if keyword:
            link = "http://www.idefix.com/vitrin/aramasonuc.asp?Shop=1&Page=%d&SearchTerm=%s" % (page_no, urllib.quote(keyword.encode("iso-8859-9")))
            url_handle = urllib.urlopen(link)
            results, page_titles = ParseSimpleSearchPage(url_handle) 
        else:
            link = "http://www.idefix.com/kitap/arama_sonuc.asp"
            parameters = {"aranan_yer":"1",
                          "dukkan":"1",
                          "eser":title.encode("iso-8859-9"),
                          "kisi":writer.encode("iso-8859-9"),
                          "sayfa":str(page_no),
                          "sira":"4",
                          "yayID":"0"}
            url_handle = urllib.urlopen(link, urllib.urlencode(parameters))
            results, page_titles = ParseAdvancedSearchPage(url_handle)
        titles.extend(page_titles)
        hook(0, results, len(titles))
        page_no += 1
    return titles

def ParseSimpleSearchPage(html_content):
    parsed_page = html.parse(html_content)
    # xpath returns "Kitap (n)"
    results_no = int(parsed_page.xpath("//span[@class='aramakat']")[0].text_content().split("(")[1][:-1])
    return results_no, ParseBookList(parsed_page)

def ParseAdvancedSearchPage(html_content):
    parsed_page = html.parse(html_content)
    results_no = int(parsed_page.xpath("//div[@class='contenttitle']/b/text()")[-2])
    return results_no, ParseBookList(parsed_page)

def ParseBookList(search_page):
    book_list = search_page.xpath("//td[@class='listeinside']")
    titles = []
    for book in book_list:
        book_title = book.xpath("div[@class='listeurun']/a")[0].get("title").strip().replace("\n"," ")
        book_url = "http://www.idefix.com" + book.xpath("div[@class='listeurun']/a")[0].get("href")
        book_writers = [x.strip() for x in book.xpath("a/text()")]
        book_publisher = book.xpath("i")[0].text_content().strip()
        titles.append({"title":book_title,
                       "url":book_url,
                       "writers":book_writers,
                       "publisher":book_publisher})
    return titles

