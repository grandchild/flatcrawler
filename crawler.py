#!/usr/bin/env python3
# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.
'''
Watch a webserver continously to check if it and all pages it is supposed to
serve are online. Send an email and exit when something fails.

This script exits after an error so that the recipients won't be spammed, but
this means it requires a manual restart once things are back to normal.

See the bottom of this file for a fitting systemd service file, to be placed
at /etc/systemd/system/notifywebsitedown.service.
'''
import re
import os
import sys
import time
from collections import defaultdict
from urllib.parse import urlsplit, urlunparse
import requests
import sendmail
from config import sites, MailConfig

seconds = 1
minutes = 60*seconds
hours = 60*minutes


### Basic settings
RECIPIENTS = [
    MailConfig.recipient,
    *MailConfig.bcc_recipients
]
CHECK_INTERVAL = 1*hours
URL_PRINT_LENGTH = 100 # print at maximimum n chars of the url in error messages
KNOWN_FILE = 'known.txt'

### Message strings
## German
EMAIL_SUBJECT = 'Neue Wohnungsangebote'
EMAIL_TEXT = 'Hey,\n{}\n{}\n'
EMAIL_SITE_OFFERS_TEXT = '\nes gibt neue Wohnungen bei {}:\n{}\n'
EMAIL_SITE_ERRORS_TEXT = '\nEs sind Fehler aufgetreten bei {}:\n{}\n'

ERR_CONNECTION = 'Die Seite {} ({}) scheint nicht zu funktionieren. Konnte keine Angebote prüfen.'
ERR_NOT_FOUND = 'Angebotsseite {} konnte nicht gefunden werden. Status war {}.'
ERR_SUCCESS_NO_MATCHES = 'success-str bei {} gefunden, aber keine Matches. expose-url-pattern überprüfen.'

LOG_CRAWLING = 'crawling {}'
LOG_NO_FLATS = '  no flats found at {}'
LOG_NEW_RESULTS = ':: new results found, email sent ::'
LOG_NO_NEW_RESULTS = ':: no new results ::'
LOG_WARN = 'WARNING: "{}" - {} ({} Neuversuche verbleiben)'
LOG_ERR = 'ERROR: "{}" - {}'


def main():
    '''Check all pages, send emails if any offers or errors.'''
    results = {}
    for site in sites:
        offers, errors = check(site)
        if any(offers) or errors is not None:
            results[site['name']] = (offers, errors)
    if results:
        send_mail(results)
        print(LOG_NEW_RESULTS)
        print(results)
    else:
        print(LOG_NO_NEW_RESULTS)
    return 0


def check(site, retries=2, backoff=1):
    '''
    Check whether there are any flat exposes on a given site. Returns a tuple
    consisting of a list of offers and error.
    
    Check retries a certain amount of times (total connection attempts are
    thus retries+1) with slightly exponential backoff wait time between tries.
    '''
    site = defaultdict(lambda:None, site)
    name = site['name']
    url = site['url']
    none_str = site['none-str']
    success_str = site['success-str']
    expose_pattern = site['expose-url-pattern']
    base_url_parts = urlsplit(url)[:2]
    
    print(LOG_CRAWLING.format(name))
    offers = set()
    err = None
    try:
        result = requests.get(url)
        if not result.ok:
            err = ERR_NOT_FOUND.format(name, format_code(result.status_code))
        elif none_str and (none_str in result.text):
            print(LOG_NO_FLATS.format(name))
        elif success_str is None:
            offers.add(url)
        elif success_str in result.text:
            debug_dump_site_html(name, result.text)
            matches = re.findall(expose_pattern, result.text)
            for match in matches:
                match_url = urlunparse(base_url_parts \
                    + (match if isinstance(match, str) else match.group(1),) \
                    + ('',)*3)
                if check_and_update_known(match_url):
                    offers.add(match_url)
            if not matches:
                err = ERR_SUCCESS_NO_MATCHES.format(name)
        else:
            err = ERR_CONNECTION.format(name, truncate(url, URL_PRINT_LENGTH))
    except requests.exceptions.ConnectionError:
        err = ERR_CONNECTION.format(name, truncate(url, URL_PRINT_LENGTH))
    if err:
        if retries > 0:
            print(LOG_WARN.format(name, err, retries))
            time.sleep(backoff)
            return check(name, result, retries-1, (backoff+2)*1.5)
        else:
            print(LOG_ERR.format(name, err))
    return offers, err


def check_and_update_known(url):
    '''Keep track of individual flat urls that we've already seen.'''
    try:
        with open(KNOWN_FILE, 'r+') as known_file:
            if any([True for known in known_file if url in known]):
                return False
            else:
                print(url, file=known_file)
                return True
    except FileNotFoundError:
        pass


def send_mail(results):
    '''
    Format and send an email containing a list of sites with lists of offers.
    '''
    offers_strs = []
    errors_strs = []
    for site, (offer_list, error) in results.items():
        offers_strs.append(EMAIL_SITE_OFFERS_TEXT.format(site, indent(offer_list, '  ✔ ')))
        if error:
            errors_strs.append(EMAIL_SITE_ERRORS_TEXT.format(site, indent(error_list, '  ✖ ')))
    text = EMAIL_TEXT.format('\n'.join(offers_strs), '\n'.join(errors_strs))
    mail = sendmail.Mail(RECIPIENTS[0], EMAIL_SUBJECT, text, bcc=RECIPIENTS[1:])
    mail.send()


def format_code(code):
    '''Returns the HTTP status code formatted like '200 ("ok")'.'''
    return '{} ("{}")'.format(code, requests.status_codes._codes[code][0])


def indent(text, indent):
    '''Indent a text (or list of lines) with the given indent string.'''
    if isinstance(text, list) or isinstance(text, set):
        return indent + ('\n'+indent).join(text)
    else:
        return indent + text.replace('\n', '\n'+indent)


def truncate(string, max_len):
    return string[:max_len-3] + '...' if len(string) > max_len else string


def debug_dump_site_html(name, html):
    with open(f'site-{name}.html', 'w') as test_log:
        print(html, file=test_log)


def print_unit_file():
    '''Print a systemd unit file to stdout'''
    service_file = f'''\
[Unit]
Description=Watch multiple websites for new flat exposes
After=network-online.target nss-lookup.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {os.path.realpath(__file__)}

[Install]
WantedBy=multi-user.target
'''
    print(service_file)


'''Check in a loop until SIGTERM.'''
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'systemd':
        print_unit_file()
        sys.exit(0)
    try:
        while main() == 0:
            time.sleep(CHECK_INTERVAL)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
