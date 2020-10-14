# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.

"""Configure your flat criteria. Not all fields are used by all sites."""
rooms_min = 2
rooms_max = rooms_min
area_min = 40
area_max = 200
rent_max = 1000
floor_min = 1
floor_max = 1000
wbs = False  # Wohnberechtigungsschein (If you don't know what this is leave it False)

### DeGeWo district IDs, select the ones you'd like to include below (as strings!).
degewo_districts = "%2C+".join([
    "46",     # Friedrichshain-Kreuzberg
    "29",     # Neukölln
    "71",     # Pankow
    "28",     # Mitte
    "7",      # Treptow-Köpenick
    "60",     # Tempelhof-Schöneberg
    "3",      # Lichtenberg
    "33",     # Charlottenburg-Wilmersdorf
    "64",     # Reinickendorf
    "2",      # Marzahn-Hellersdorf
    "4-8",    # Spandau
    "58",     # Steglitz-Zehlendorf
    "40-67",  # Umland
])

### Gewobag districts, comment out the ones you'd not like to search in.
gewobag_districts = "&bezirke%5B%5D=".join(
    [
        "charlottenburg-wilmersdorf",
        "charlottenburg-wilmersdorf-grunewald",
        "friedrichshain-kreuzberg",
        "friedrichshain-kreuzberg-friedrichshain",
        "friedrichshain-kreuzberg-kreuzberg",
        "lichtenberg",
        "lichtenberg-alt-hohenschoenhausen",
        "lichtenberg-falkenberg",
        "lichtenberg-fennpfuhl",
        "neukoelln",
        "neukoelln-britz",
        "neukoelln-buckow",
        "neukoelln-rudow",
        "pankow",
        "pankow-prenzlauer-berg",
        "reinickendorf",
        "reinickendorf-tegel",
        "reinickendorf-waidmannslust",
        "spandau",
        "spandau-haselhorst",
        "spandau-staaken",
        "steglitz-zehlendorf",
        "steglitz-zehlendorf-lichterfelde",
        "tempelhof-schoeneberg",
        "tempelhof-schoeneberg-mariendorf",
        "treptow-koepenick",
        "treptow-koepenick-adlershof",
        "treptow-koepenick-alt-treptow",
    ]
)


class MailConfig:
    """
    Enter your email login here, emails will be sent from the *user* address to
    the *recipient* address.
    """

    server = ""  ## FILL ME
    user = ""  ## FILL ME
    password = ""  ## FILL ME
    from_ = "NAME <" + user + ">"
    reply_to = "NAME <" + user + ">"
    recipient = user
    bcc_recipients = []
