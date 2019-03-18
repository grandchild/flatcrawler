# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.
from config import *

"""
name: name of site.
url: website url where offers should appear.
none-str: a string that appears in the website html in case nothing has been found.
success-str: a string that appears in the website html in case something has been found.
expose-url-pattern: regex for links that point to offer exposés and should be sent out
    via email.
notes: general notes on the site (currently not used).
expose-details: a mapping from keys to regex strings, used to extract further details
    from an exposé page.
"""
sites = [
    {
        "name": "Gewobag",
        "url": f"https://www.gewobag.de/mieten-7.html?zimmer_von={rooms_min}&zimmer_bis={rooms_max}&wohnung=1&ortsteil={gewobag_districts}&start=0&do=AKTUALISIEREN",
        "none-str": "Zur Zeit sind leider keine passenden Angebote verfügbar",
        "success-str": "Seite 1 von",
        "expose-url-pattern": r'href="(expose_.+?html)',
        "notes": "nur prenzlberg",
    },
    {
        "name": "Habitat e.G.",
        "url": "http://www.habitat-eg.de/index/110/",
        "none-str": "Derzeit können wir Ihnen leider&nbsp;keine freien Wohnungen anbieten.",
    },
    {
        "name": "Gesobau",
        "url": f"https://www.gesobau.de/mieten/wohnungssuche.html?list%5BzimmerMin%5D={rooms_min}&list%5BflaecheMin%5D={area_min}&list%5BmieteMax%5D={rent_max}",
        "none-str": "Zu Ihrer Suche konnten keine passenden Angebote gefunden werden.",
        "success-str": "<span>1</span> von",
        "expose-url-pattern": r'href="(/wohnung/.+?html)',
    },
    {
        "name": "EWG Pankow",
        "url": "https://www.ewg-pankow.de/wohnen/wohnungsangebote.html",
        "none-str": "Ihre Suche lieferte keine passenden Ergebnisse",
        "success-str": "zum Exposé",
        "expose-url-pattern": r'href="(wohnen/wohnungsangebote/wohnungsdetails/.+?html)',
    },
    {
        "name": "DeGeWo",
        "url": f"https://immosuche.degewo.de/de/search?size=10&page=1&property_type_id=1&categories%5B%5D=1&lat=&lon=&area=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district={degewo_districts}&property_number=&price_switch=true&price_radio=custom&price_from=0&price_to={rent_max}&qm_radio=custom&qm_from={area_min}&qm_to={area_max}&rooms_radio=custom&rooms_from={rooms_min}&rooms_to={rooms_max}&order=rent_total_without_vat_asc",
        "none-str": "0</span>\n Treffer anzeigen",
        "success-str": "<div class='merken merken__article-list js-merken' data-objectid=",
        "expose-url-pattern": r'href="(/de/properties/.+?)"><div class=\'article-list__image',
    },
    ### uses XHR dynamic reloading, but has own email subscription
    # {
    #     "name": "HoWoGe",
    #     "url": f"https://www.howoge.de/mieten/wohnungssuche.html",
    #     "none-str": "",
    #     "success-str": "",
    #     "expose-url-pattern": r'href="(.+?html)',
    # },
    {
        "name": "Gemeinnützige Baugenossenschaft Steglitz e.G.",
        "url": "https://www.gbst-berlin.de/Mietangebote/Freie-Wohnungen",
        "none-str": '<td class="cm_table cm_firstcol" style="text-align: left;"><p><br /></p></td>',
        "success-str": 'href="https://public.od.cm4allbusiness.de/.cm4all/uro/W4BOD0AVBPF3/aktuelle%20Mietangebote%20PDF',
        "expose-url-pattern": r'href="(https://public\.od\.cm4allbusiness\.de/\.cm4all/uro/W4BOD0AVBPF3/aktuelle%20Mietangebote%20PDF/.+?&amp;cdp=a)"',
    },
    {
        "name": "Vaterländischer Bauverein",
        "url": "http://www.vbveg.de/aktuelles/freie-wohnungen.html",
        "none-str": """\
<div class="ce_text block">
</div>
</div>
<!-- indexer::stop -->
<p class="back"><a href="javascript:history.go(-1)" title="Zurück">Zurück</a></p>""",
    },
    {
        "name": "Berolina",
        "url": "https://berolina.info/wohnungssuche/",
        "none-str": "Es tut uns leid, zur Zeit sind alle unsere Wohnungen vermietet und wir können Ihnen leider keine freien Wohnungen anbieten.",
    },
    {
        "name": "ebay Kleinanzeigen",
        "url": f"https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/berlin/anzeige:angebote/preis::{rent_max}/c203l3331+wohnung_mieten.etage_i:1,+wohnung_mieten.qm_d:{area_min},+wohnung_mieten.zimmer_d:{rooms_min},{rooms_max}",
        "none-str": "Es wurden leider keine Anzeigen gefunden.",
        "success-str": '<article class="aditem" data-adid="',
        "expose-url-pattern": r'<a class="ellipsis" (?:name="[0-9]+?")?\s+ href="(/s-anzeige/.+?)">',
        "expose-details": {
            "title": r'<h1 id="viewad-title" class="articleheader--title" itemprop="name">(.+?)</h1>',
            "total_rent": r'<dt class="attributelist--key">Warmmiete.+?:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
            "price": r'<h2 class="articleheader--price" id="viewad-price">Preis: (.+?)</h2>',
            "location": r'(?:<span id="street-address" itemprop="street-address">\s+(.+?)</span>,\s+)?<span id="viewad-locality" itemprop="locality">\s+(.+?)</span>',
            "rooms": r'<dt class="attributelist--key">Zimmer:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
            "area": r'<dt class="attributelist--key">Wohnfläche.+?:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
            "floor": r'<dt class="attributelist--key">Etage:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
        },
    },
    # ...? Send me PRs!
]
