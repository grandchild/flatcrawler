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
        "name": "Wohnungsbaugenossenschaft DPF eG",
        "url": "https://www.dpfonline.de/interessenten/immobilien/",
        "success-str": '<div class="immo-a-info">',
        "expose-url-pattern": r'<a href="https://www\.dpfonline\.de/(immobilien/.+?)/">',
        "expose-details": {
            "title": r'<h1 class="immo-caption">\s+?(.+?)\s+?</h1>',
            "price": r'<td>Kaltmiete</td>\s+?<td>\s+?(.+?)\s+?</td>',
            "total_rent": r'<td>Gesamtmiete</td>\s+?<td>\s+?(.+?)\s+?</td>',
            "safety": r'<td>Genossenschaftsanteile</td>\s+?<td>\s+?(.+?)\s+?</td>',
            "rooms": r'<td>Zimmer</td>\s+?<td>\s+?(.+?)\s+?</td>',
            "area": r'<td>Wohnfläche</td>\s+?<td>\s+?(.+?) m<sup>2</sup>\s+?</td>',
            "floor": r'<td>\s+?(.+?)\. Etage\s+?</td>',
            "location": r'<td>Straße</td>\s+?<td>\s+?(.+?)\s+?</td>',
            "quarter": r'<td>Stadtteil</td>\s+?<td>\s+?(.+?)\s+?</td>',
        },
    },
    {
        "name": "Bau- und Siedlungsgenossenschaft Postheimstätte eG",
        "url": "https://www.postheimstätte.de/properties/",
        "none-str": "Es tut uns leid, es wurden keine Objekte gefunden.",
    },
    {
        "name": "Wohnungsbaugenossenschaft Zentrum eG",
        "url": "https://www.wbg-zentrum.de/wohnen/wohnungsangebot-2/wohnungsangebot/",
        "success-str": '<div class="wpb_text_column wpb_content_element ">',
        "expose-url-pattern": r'href="(https://www\.wbg-zentrum\.de/wp\-content/uploads/.+?/.+?/.+?\.pdf)" title="" target="_blank">weiter</a>',
    },
    {
        "name": "Wohnungsbaugenossenschaft Altglienicke eG",
        "url": "https://www.wg-altglienicke.de/wohnungen",
        "none-str": "Zur Zeit stehen keine Wohnungsangebote zur Verfügung.",
    },
    {
        "name": "Wohnungsbaugenossenschaft Solidarität eG",
        "url": "https://wg-solidaritaet.de/wohnen/mietangebote/",
        "none-str": "Aktuell stehen leider keine Mietangebote zur Verfügung.",
    },
    {
        "name": "Wohnungsbaugenossenschaft Bremer Höhe eG",
        "url": "https://www.bremer-hoehe.de/Vermietung:_:90.html?sub=1",
        "none-str": "Leider liegen zur Zeit keine Vermietungsangebote vor.",
    },
    {
        "name": "Beamten-Wohnungs-Verein zu Berlin eG",
        "url": "https://www.bwv-berlin.de/wohnungsangebote.html",
        "none-str": "Derzeit können wir Ihnen leider keine Wohnungen zur Vermietung anbieten.",
    },
    {
        "name": "Bewohnergenossenschaft FriedrichsHeim eG",
        "url": "https://www.friedrichsheim-eg.de/category/freie-wohnungen/",
        "none-str": "Zur Zeit sind leider keine Wohnungen im Angebot.",
    },
    {
        "name": "Gewobag",
        "url": (
            "https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/?nutzungsarten%5B%5D=wohnung"
            f"&zimmer_von={rooms_min}&zimmer_bis={rooms_max}"
            f"&bezirke%5B%5D={gewobag_districts}"
            f"{'keineg=1' if floor_min >= 1 else ''}"
            # "&start=0"
        ),
        "none-str": "Zur Zeit sind leider keine passenden Angebote verfügbar",
        "success-str": '<div class="angebot-content">',
        "expose-url-pattern": r'<a href="https://www\.gewobag\.de/(fuer-mieter-und-mietinteressenten/mietangebote/[0-9-]+/)" class="read-more-link">Mietangebot ansehen',
        "expose-details": {
            "title": r'<h1 class="entry-title">(.+?)</h1>',
            "price": r'<div class="detail-label">Grundmiete</div>\s+<div class="detail-value">(.+?) Euro</div>',
            "total_rent": r'<div class="detail-label">Gesamtmiete</div>\s+<div class="detail-value">(.+?) Euro</div>',
            "safety": r'<div class="detail-label">Kaution</div>\s+<div class="detail-value">(.+?) (?:€|Euro)</div>',
            "location": r'<div class="detail-label">Anschrift</div>\s+<div class="detail-value">(.+?)</div>',
            "quarter": r'<div class="detail-label">Bezirk/Ortsteil</div>\s+<div class="detail-value">(.+?)</div>',
            "description": r'<div class="detail-label">Beschreibung</div>\s+<div class="detail-value">(.+?)</div>',
            "floor": r'<div class="detail-label">Etage</div>\s+<div class="detail-value">(.+?)</div>',
            "rooms": r'<div class="detail-label">Anzahl Zimmer</div>\s+<div class="detail-value">(.+?)</div>',
            "area": r'<div class="detail-label">Fl&auml;che in m²</div>\s+<div class="detail-value">(.+?)</div>',
            "vacant_by": r'<div class="detail-label">Frei ab</div>\s+\s+<div class="detail-value capitalize">(.+?)</div>',
        },
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
        "url": "https://www.ewg-pankow.de/wohnen/",
        "none-str": "Aktuell ist leider kein Wohnungsangebot verfügbar.",
        "success-str": "zum Exposé",
        "expose-url-pattern": r'href="(wohnen/wohnungsangebote/wohnungsdetails/.+?html)',
    },
    {
        "name": "DeGeWo",
        "url": f"https://immosuche.degewo.de/de/search?size=10&page=1&property_type_id=1&categories%5B%5D=1&lat=&lon=&area=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district={degewo_districts}&property_number=&price_switch=true&price_radio=custom&price_from=&price_to={rent_max}&qm_radio=custom&qm_from={area_min}&qm_to={area_max}&rooms_radio=custom&rooms_from={rooms_min}&rooms_to={rooms_max}&wbs_required={'true' if wbs else 'false'}&order=rent_total_without_vat_asc",
        "none-str": "0</span>\n Treffer anzeigen",
        "success-str": "<div class='merken merken__article-list js-merken' data-objectid=",
        "expose-url-pattern": r'href="(/de/properties/W[0-9-]+?)"><div class=\'article-list__image',
        "expose-details": {
            "title": r"<h1 class=\'article__title\'>\s+(.+?)\s+</h1>",
            "location": r"<span class='expose__meta'>(.+?)</span>",
            "price": r"<li class=\'ce-table__list-item\'>Nettokaltmiete: (.+?) €</li>",
            "total_rent": r"<div class=\'expose__price-tag\'>\s*(.+?) €\s*<span",
            "safety": r"<li class=\'ce-table__list-item\'>Kaution: (.+?)</li>",
            "rooms": r"<td class=\'teaser-tileset__table-item\'>Zimmer</td>\s+<td class=\'teaser-tileset__table-item\'>(.+?)</td>",
            "area": r"<td class=\'teaser-tileset__table-item\'>Wohnfläche</td>\s+<td class=\'teaser-tileset__table-item\'>(.+?) m²</td>",
            "vacant_by": r"<td class=\'teaser-tileset__table-item\'>Verfügbar ab</td>\s+<td class=\'teaser-tileset__table-item\'>\s*(.+?)\s*</td>",
            "floor": r"<td class=\'teaser-tileset__table-item\'>\s*Geschoss / Anzahl\s*</td>\s+<td class=\'teaser-tileset__table-item\'>\s*(.+?)\s*</td>",
            "construction_year": r"<td class=\'teaser-tileset__table-item\'>Baujahr</td>\s+<td class=\'teaser-tileset__table-item\'>\s*(.+?)\s*</td>",
        },
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
        "success-str": '<td class="cm_table cm_lastcol">',
        "expose-url-pattern": r'https://public\.od\.cm4allbusiness\.de/\.cm4all/uro/W4BOD0AVBPF3/1_Mietangebote/Expos%C3%A9/.+?\.pdf.+?',
    },
    #     {
    #         "name": "Vaterländischer Bauverein",
    #         "url": "http://www.vbveg.de/aktuelles/freie-wohnungen.html",
    #         "none-str": """\
    # <div class="ce_text block">
    # </div>
    # </div>
    # <!-- indexer::stop -->
    # <p class="back"><a href="javascript:history.go(-1)" title="Zurück">Zurück</a></p>""",
    #     },
     {
         "name": "Berolina",
         "url": "https://berolina.info/wohnungsangebote-wenn-angebote-vorhanden/",
         "none-str": "Momentan sind leider keine Immobilien in unserem Angebot verfügbar.",
     },
    # {
    #     "name": "ebay Kleinanzeigen",
    #     "url": f"https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/berlin/anzeige:angebote/preis::{rent_max}/c203l3331+wohnung_mieten.etage_i:{floor_min},{floor_max}+wohnung_mieten.qm_d:{area_min},+wohnung_mieten.zimmer_d:{rooms_min},{rooms_max}",
    #     "none-str": "Es wurden leider keine Anzeigen gefunden.",
    #     "success-str": '<article class="aditem" data-adid="',
    #     "expose-url-pattern": r'<a class="ellipsis" (?:name="[0-9]+?")?\s+ href="(/s-anzeige/.+?)">',
    #     "expose-details": {
    #         "title": r'<h1 id="viewad-title" class="articleheader--title" itemprop="name">(.+?)</h1>',
    #         "total_rent": r'<dt class="attributelist--key">Warmmiete.+?:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
    #         "price": r'<h2 class="articleheader--price" id="viewad-price">Preis: (.+?)</h2>',
    #         "location": r'(?:<span id="street-address" itemprop="street-address">\s+(.+?)</span>,\s+)?<span id="viewad-locality" itemprop="locality">\s+(.+?)</span>',
    #         "rooms": r'<dt class="attributelist--key">Zimmer:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
    #         "area": r'<dt class="attributelist--key">Wohnfläche.+?:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
    #         "floor": r'<dt class="attributelist--key">Etage:</dt>\s+<dd class="attributelist--value">\s+<span >\s+(.+?)</span>',
    #     },
    # },
    # ...? Send me PRs!
]
