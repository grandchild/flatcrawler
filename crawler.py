#!/usr/bin/env python3
# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.
"""
Watch a webserver continously to check if it and all pages it is supposed to
serve are online. Send an email and exit when something fails.

This script exits after an error so that the recipients won't be spammed, but
this means it requires a manual restart once things are back to normal.

See the bottom of this file for a fitting systemd service file, to be placed
at /etc/systemd/system/notifywebsitedown.service.
"""
import re
import os
import sys
import time
from collections import defaultdict
from urllib.parse import urlsplit, urlunparse
from hashlib import sha1
from pathlib import Path
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import requests
import sendmail
from sites import sites as site_configs
from config import MailConfig

seconds = 1
minutes = 60 * seconds
hours = 60 * minutes


### Basic settings
RECIPIENTS = [MailConfig.recipient, *MailConfig.bcc_recipients]
CHECK_INTERVAL = 1 * hours
URL_PRINT_LENGTH = 300  # print at maximimum n chars of the url in error messages
KNOWN_FILE = "known.txt"

### Message strings
## German
EMAIL_SUBJECT = "[Wohnung] {} neue Wohnungsangebote"
EMAIL_TEXT = "Hey,\n{}\n{}\n"
EMAIL_SITE_OFFERS_TEXT = "\nes gibt neue Wohnungen bei {}:\n{}\n"
EMAIL_SITE_ERRORS_TEXT = "\nEs sind Fehler aufgetreten bei {}:\n{}\n"

ERR_CONNECTION = (
    "Die Seite {} ( {} ) scheint nicht zu funktionieren. Konnte keine Angebote prüfen."
)
ERR_NOT_FOUND = "Angebotsseite {} konnte nicht gefunden werden. Status war {}.\n{}"
ERR_SUCCESS_NO_MATCHES = (
    "success-str bei {} gefunden, aber keine Matches. expose-url-pattern überprüfen."
)
ERR_EXPOSE_CONNECTION = (
    "Die Seite {} scheint nicht zu funktionieren. Konnte keine Details ermitteln."
)
ERR_EXPOSE_NOT_FOUND = ERR_NOT_FOUND

LOG_CRAWLING = "crawling {}"
LOG_NO_FLATS = "  no flats found at {}"
LOG_NEW_RESULTS = ":: new results found ::"
LOG_EMAIL_SENT = ":: email sent ::"
LOG_NO_NEW_RESULTS = ":: no new results ::"
LOG_WARN = 'WARNING: "{}" - {} ({} Neuversuche verbleiben)'
LOG_ERR = 'ERROR: "{}" - {}'


class Site:
    """
    A website to be searched for new flats. Takes a *config* dict, which should include
    most of the fields specified in `sites.py`.
    """

    def __init__(self, config={}):
        self.config = defaultdict(lambda: None, config)
        self.offers = set()
        self.error = None
        self.name = self.config["name"]
        self.url = self.config["url"]
        self.none_str = self.config["none-str"]
        self.success_str = self.config["success-str"]
        self.expose_pattern = self.config["expose-url-pattern"]
        self.expose_details = self.config["expose-details"]

    def check(self, retries=2, backoff=1, include_known=False):
        """
        Check whether there are any flat exposes on a given site. Returns a tuple
        consisting of a list of offers and error.

        Check retries a certain amount of times (total connection attempts are thus
        retries+1) with slightly exponential backoff wait time between tries.
        """
        base_url_parts = urlsplit(self.url)[:2]

        print(LOG_CRAWLING.format(self.name))
        self.error = None
        try:
            result = requests.get(self.url)
            if not result.ok:
                self.error = ERR_NOT_FOUND.format(
                    self.name, format_code(result.status_code), self.url
                )

            elif self.success_str is None:
                if self.check_and_update_known(
                    self.url, result.text, include_known=include_known
                ):
                    self.offers.add(Offer(self.url, self.expose_details))
            elif self.success_str in result.text:
                debug_dump_site_html(self.name, result.text)
                matches = re.findall(self.expose_pattern, result.text)
                for match in matches:
                    match_url = urlunparse(
                        base_url_parts
                        + (match if isinstance(match, str) else match.group(1),)
                        + ("",) * 3
                    )
                    if self.check_and_update_known(
                        match_url, include_known=include_known
                    ):
                        self.offers.add(Offer(match_url, self.expose_details))
                if not matches:
                    self.error = ERR_SUCCESS_NO_MATCHES.format(self.name)
            elif self.none_str and (self.none_str in result.text):
                print(LOG_NO_FLATS.format(self.name))
            else:
                self.error = ERR_CONNECTION.format(
                    self.name, truncate(self.url, URL_PRINT_LENGTH)
                )
        except requests.exceptions.ConnectionError:
            self.error = ERR_CONNECTION.format(
                self.name, truncate(self.url, URL_PRINT_LENGTH)
            )
        if self.error:
            if retries > 0:
                print(LOG_WARN.format(self.name, self.error, retries))
                time.sleep(backoff)
                return self.check(retries - 1, (backoff + 2) * 1.5)
            else:
                print(LOG_ERR.format(self.name, self.error))

    def check_and_update_known(self, url, text=None, include_known=False):
        """Keep track of individual flat urls that we've already seen."""
        if text is not None:
            url += (
                "|"
                + sha1(
                    BeautifulSoup(text, "html.parser").get_text().encode()
                ).hexdigest()
            )
        try:
            with open(KNOWN_FILE, "r+") as known_file:
                if any([True for known in known_file if url in known]):
                    return include_known
                else:
                    print(url, file=known_file)
                    return True
        except FileNotFoundError:
            pass

    def __str__(self):
        if self.error:
            return EMAIL_SITE_ERRORS_TEXT.format(self.name, indent(self.error, "  ✖ "))
        else:
            return EMAIL_SITE_OFFERS_TEXT.format(
                self.name, "\n".join([str(o) for o in self.offers])
            )

    def __repr__(self):
        return self.error if self.error else repr([o.url for o in self.offers])


class Offer:
    """
    A single offer exposé. Takes a *url*, and if given a *details* dict, will retrieve
    those details from the *url*, if present.
    """

    def __init__(self, url, details=None):
        self.url = url
        self.details = OfferDetails(url, details) if details else None

    def __str__(self):
        if self.details:
            return (
                f"  ✔ {self.details.title}\n"
                + f"    {self.url}\n"
                + indent(str(self.details).splitlines(), " " * 8)
            )
        else:
            return f"  ✔ {self.url}"


class OfferDetails:
    """
    A list of extra details about an offer exposé. Takes a *url*, and a *config* dict,
    much like :py:class:`Site` does, containing keys with regex strings. The *url* is
    retrieved and any details for which the regex patterns match will be collected into
    `self.details`.
    """

    def __init__(self, url, config):
        self.config = config
        self.url = url
        self.details = defaultdict(lambda: None, {})
        self.title = None

        try:
            result = requests.get(self.url)
            if not result.ok:
                self.error = ERR_EXPOSE_NOT_FOUND.format(
                    "", format_code(result.status_code), self.url
                )
            else:
                for key, detail_pattern in self.config.items():
                    match = re.search(detail_pattern, result.text)
                    if match:
                        match_str = (
                            match
                            if isinstance(match, str)
                            else " ".join(match.groups(""))
                        )
                        if key == "title":
                            self.title = match_str.strip()
                        else:
                            self.details[key] = match_str.strip()
        except requests.exceptions.ConnectionError:
            self.error = ERR_CONNECTION.format(truncate(self.url, URL_PRINT_LENGTH))

    def __str__(self):
        return "\n".join(
            [f"{k.replace('_', ' ').title(): <10} {v}" for k, v in self.details.items()]
        )


def main(options):
    """Check all pages, send emails if any offers or errors."""
    results = []

    for site_config in site_configs:
        site = Site(site_config)
        site.check(include_known=options.include_known)
        if any(site.offers) or site.error is not None:
            results.append(site)
    if results:
        print(LOG_NEW_RESULTS)
        mail_subject, mail_text = format_mail(results)
        if not options.no_email:
            print(LOG_EMAIL_SENT)
            send_mail(mail_subject, mail_text)
        else:
            print()
            print(mail_subject)
            print()
            print(mail_text)
        if options.debug:
            print(results)
    else:
        print(LOG_NO_NEW_RESULTS)
    return 0 if all([r.error is None for r in results]) else 1


def format_mail(results):
    """
    Format and the email subject and text containing a list of sites with lists of
    offers.
    """
    offers_strs = []
    errors_strs = []
    offers_count = 0
    for site in results:
        if site.error:
            errors_strs.append(str(site))
        else:
            offers_strs.append(str(site))
            offers_count += len(site.offers)
    text = EMAIL_TEXT.format("\n".join(offers_strs), "\n".join(errors_strs))
    return EMAIL_SUBJECT.format(offers_count), text


def send_mail(subject, text):
    """
    Send an email to the configured recipients containing the given subject and content.
    """
    mail = sendmail.Mail(RECIPIENTS[0], subject, text, bcc=RECIPIENTS[1:])
    mail.send()


def format_code(code):
    """Returns the HTTP status code formatted like '200 ("ok")'."""
    return '{} ("{}")'.format(code, requests.status_codes._codes[code][0])


def indent(text, indent):
    """Indent a text (or list of lines) with the given indent string."""
    if isinstance(text, list) or isinstance(text, set):
        return indent + ("\n" + indent).join(text)
    else:
        return indent + text.replace("\n", "\n" + indent)


def truncate(string, max_len):
    return string[: max_len - 3] + "..." if len(string) > max_len else string


def debug_dump_site_html(name, html):
    with open(f"debug-sites/site-{name}.html", "w") as test_log:
        print(html, file=test_log)


def service_file(user_param=False):
    """
    Create a systemd unit file. If *user_param* is True, output will be an
    @-parameterized service file that runs as the given user.
    """
    return f"""\
[Unit]
Description=Check various websites for new flat exposes{" for %I" if user_param else ""}
After=network-online.target nss-lookup.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u "{os.path.realpath(__file__)}"
WorkingDirectory={os.path.dirname(os.path.realpath(__file__))}
{"User=%i" if user_param else ""}

[Install]
WantedBy=multi-user.target"""


def timer_file():
    """
    Create a systemd timer file, targeting the service file, which runs every
    CHECK_INTERVAL seconds.
    """

    return f"""\
[Unit]
Description=Check multiple websites for new flat exposes

[Timer]
OnUnitActiveSec={CHECK_INTERVAL}s
RandomizedDelaySec={CHECK_INTERVAL//4}s

[Install]
WantedBy=timers.target"""


def install(run=False):
    """
    Install service and timer files to user systemd folder, optionally enable and start
    the timer as well.
    """

    target_path = os.path.join(Path.home(), ".local/share/systemd/user/")
    try:
        os.makedirs(target_path, exist_ok=True)
        with open(os.path.join(target_path, "flatcrawler.service"), "w") as service:
            print(service_file(), file=service)
        with open(os.path.join(target_path, "flatcrawler.timer"), "w") as timer:
            print(timer_file(), file=timer)
    except (PermissionError, FileNotFoundError, IOError) as err:
        print(err, file=sys.stderr)
        return 2
    if run:
        os.system("systemctl --user daemon-reload")
        return os.system("systemctl --user enable --now flatcrawler.timer")


if __name__ == "__main__":
    parser = ArgumentParser(description="Crawl flat offer websites for new flats.")
    parser.add_argument(
        "systemd",
        nargs="?",
        choices=["service", "service@", "timer", "install", "run"],
        default=None,
        help=(
            "Print a systemd unit file of the specified type."
            + " Use 'systemd@' to print a service file that allows a User parameter."
            + " Use 'install' to create the service and timer in"
            + " ~/.local/share/systemd/user/. Use 'run' to install, start and enable"
            + " the timer, all in one command."
        ),
    )
    parser.add_argument(
        "--no-email", action="store_true", help="Don't send an email, only log results"
    )
    parser.add_argument("--debug", action="store_true", help="Dump raw results")
    parser.add_argument(
        "--include-known", action="store_true", help="Include known results"
    )
    args = parser.parse_args()
    if args.systemd == "service":
        print(service_file())
    elif args.systemd == "service@":
        print(service_file(user_param=True))
    elif args.systemd == "timer":
        print(timer_file())
    elif args.systemd == "install":
        sys.exit(install())
    elif args.systemd == "run":
        sys.exit(install(run=True))
    else:
        try:
            sys.exit(main(args))
        except KeyboardInterrupt:
            sys.exit(0)
