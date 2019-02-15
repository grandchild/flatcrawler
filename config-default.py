# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.

'''Configure your type of flat. Is not used for all sites.'''
rooms_min = 2
rooms_max = rooms_min
area_min = 40
area_max = 200
rent_max = 1000

### DeGeWo district IDs, select the ones you'd like to include below (as strings!).
# Friedrichshain-Kreuzberg:     46
# Neukölln:                     29
# Pankow:                       71
# Mitte:                        28
# Treptow-Köpenick:              7
# Tempelhof-Schöneberg:         60
# Lichtenberg:                   3
# Charlottenburg-Wilmersdorf:   33
# Reinickendorf:                64
# Marzahn-Hellersdorf:           2
# Spandau:                    4-65
# Steglitz-Zehlendorf:          58
# Umland:                    40-67
_degewo_districts='%2C+'.join(['28',])

### Gewobag districts, comment out the ones you'd not like to search in.
_gewobag_districts='X1'.join([
    # 'Adlershof',
    # 'Alt-Hohenschoenhausen',
    'Alt-Treptow',
    # 'Falkenberg',
    # 'Falkenhagener_Feld',
    # 'Fennpfuhl',
    'Lichtenberg',
    # 'Mariendorf',
    'Prenzlauer_Berg',
    'Schoeneberg',
    # 'Staaken',
])


'''
name: name of site (must be unique)
url: website url where offers should appear
none-str: a string that appears in the website html in case nothing has been found
success-str: a string that appears in the website html in case something has been found.
expose-url-pattern: regex for links that point to offer exposes and should be sent out via email
notes: general notes on the site (currently not used)
'''
sites = [
    {
        'name': 'Gewobag',
        'url': f'https://www.gewobag.de/mieten-7.html?zimmer_von={rooms_min}&zimmer_bis={rooms_max}&wohnung=1&ortsteil={_gewobag_districts}&start=0&do=AKTUALISIEREN',
        'none-str': 'Zur Zeit sind leider keine passenden Angebote verfügbar',
        'success-str': 'Seite 1 von',
        'expose-url-pattern': r'href="(expose_.+?html)',
        'notes': 'nur prenzlberg',
    },
    {
        'name': 'Habitat e.G.',
        'url': 'http://www.habitat-eg.de/index/110/',
        'none-str': 'Derzeit können wir Ihnen leider&nbsp;keine freien Wohnungen anbieten.',
    },
    {
        'name': 'Gesobau',
        'url': f'https://www.gesobau.de/mieten/wohnungssuche.html?list%5BzimmerMin%5D={rooms_min}&list%5BflaecheMin%5D={area_min}&list%5BmieteMax%5D={rent_max}',
        'none-str': 'Zu Ihrer Suche konnten keine passenden Angebote gefunden werden.',
        'success-str': '<span>1</span> von',
        'expose-url-pattern': r'href="(/wohnung/.+?html)',
    },
    {
        'name': 'EWG Pankow',
        'url': 'https://www.ewg-pankow.de/wohnen/wohnungsangebote.html',
        'none-str': None,
        'success-str': 'zum Exposé',
        'expose-url-pattern': r'href="(wohnen/wohnungsangebote/wohnungsdetails/.+?html)',
    },
    {
        'name': 'DeGeWo',
        'url': f'https://immosuche.degewo.de/de/search?size=10&page=1&property_type_id=1&categories%5B%5D=1&lat=&lon=&area=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&district={_degewo_districts}&property_number=&price_switch=true&price_radio=custom&price_from=0&price_to={rent_max}&qm_radio=custom&qm_from={area_min}&qm_to={area_max}&rooms_radio=custom&rooms_from={rooms_min}&rooms_to={rooms_max}&order=rent_total_without_vat_asc',
        'none-str': '0</span>\n Treffer anzeigen',
        'success-str': '<div class=\'merken merken__article-list js-merken\' data-objectid=',
        'expose-url-pattern': r'href="(/de/properties/.+?)"><div class=\'article-list__image',
    },
    ### uses XHR dynamic reloading, but has own email subscription
    # {
    #     'name': 'HoWoGe',
    #     'url': f'https://www.howoge.de/mieten/wohnungssuche.html',
    #     'none-str': '',
    #     'success-str': '',
    #     'expose-url-pattern': r'href="(.+?html)',
    # },
    {
        'name': 'Gemeinnützige Baugenossenschaft Steglitz e.G.',
        'url': f'https://www.gbst-berlin.de/Mietangebote/Freie-Wohnungen',
        'none-str': None,
        'success-str': '<tbody class="cm_table"><tr class="cm_table cm_firstrow"><td class="cm_table cm_firstcol"',
        'expose-url-pattern': r'href="(https://public\.od\.cm4allbusiness\.de/\.cm4all/uro/W4BOD0AVBPF3/aktuelle%20Mietangebote%20PDF/.+?&amp;cdp=a)"',
    },
    {
        'name': 'Vaterländischer Bauverein',
        'url': 'http://www.vbveg.de/aktuelles/freie-wohnungen.html',
        'none-str': '''\
<div class="ce_text block">
</div>
</div>
<!-- indexer::stop -->
<p class="back"><a href="javascript:history.go(-1)" title="Zurück">Zurück</a></p>''',
    },
    {
        'name': 'Berolina',
        'url': 'https://berolina.info/wohnungssuche/',
        'none-str': 'Es tut uns leid, zur Zeit sind alle unsere Wohnungen vermietet und wir können Ihnen leider keine freien Wohnungen anbieten.',
    },
    # ...? Send me PRs!
]


class MailConfig:
    '''
    Enter your email login here, emails will be sent from the *user* address to
    the *recipient* address.
    '''
    server = '' ## FILL ME
    user = '' ## FILL ME
    password = '' ## FILL ME
    from_ = 'NAME <'+user+'>'
    reply_to = 'NAME <'+user+'>'
    recipient = user
    bcc_recipients = []
