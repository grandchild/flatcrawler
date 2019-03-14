# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.

"""Configure your type of flat. Is not used for all sites."""
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
degewo_districts = "%2C+".join(["28"])

### Gewobag districts, comment out the ones you'd not like to search in.
gewobag_districts = "X1".join(
    [
        # "Adlershof",
        # "Alt-Hohenschoenhausen",
        "Alt-Treptow",
        # "Falkenberg",
        # "Falkenhagener_Feld",
        # "Fennpfuhl",
        "Lichtenberg",
        # "Mariendorf",
        "Prenzlauer_Berg",
        "Schoeneberg",
        # "Staaken",
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
