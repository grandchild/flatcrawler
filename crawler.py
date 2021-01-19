#!/usr/bin/env python3
# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.
"""
flatcrawler -- Crawl flat offer websites for new flats.

If run periodically, this script will notify you of new offers quickly as they appear
online.

For each site configured in sites.py, retrieve the website HTML and scan it for the
presence of certain strings and links. Create `Offer` objects for each expose link
found. Will optionally retrieve the offer links as well scan them for additional details
on the offer.

Previously seen offers will not be considered and to that end all offer links will be
saved to a `known.txt` file.

If there are any new offers, format the collected offer list as a plaintext email with
links. When run with the flag `--no-email`, skip email sending and print the text on
stdout. Use this flag to send via other means, such as messenger bots.
"""
import re
import os
import sys
import time
from collections import defaultdict
from urllib.parse import urlparse, urlsplit, urlunparse
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

### HTTP request settings
HEADERS = {
    # set a user agent to prevent "403: forbidden" errors on some sites
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0"
}

### Message strings
## German
EMAIL_SUBJECT = "[Wohnung] {} neue Wohnungsangebote"
EMAIL_TEXT = "Hey,\n{}\n{}\n"
EMAIL_SITE_OFFERS_TEXT = "\nes gibt neue Wohnungen bei {}:\n{}\n"
EMAIL_SITE_ERRORS_TEXT = "\nEs sind Fehler aufgetreten bei {}:\n{}\n"
EMAIL_SITE_NO_LIST_TEXT = "Es gibt Resultate, aber auflisten ist nicht möglich.\n{}"

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

VERBOSITY = 0
QUIET = False


class Site:
    """
    A website to be searched for new flats. Takes a *config* dict, which should include
    most of the fields specified in `sites.py`.
    """

    def __init__(self, config):
        self.config = defaultdict(lambda: None, config)
        self.offers = set()
        self.error = None
        self.name = self.config["name"]
        self.url = self.config["url"]
        self.none_str = self.config["none-str"]
        self.success_str = self.config["success-str"]
        self.expose_url_pattern = self.config["expose-url-pattern"]
        self.expose_details = self.config["expose-details"]

    def check(self, retries=2, backoff=1, include_known=False):
        """
        Check whether there are any flat exposes on a given site. Returns a tuple
        consisting of a list of offers and error.

        Check retries a certain amount of times (total connection attempts are thus
        retries+1) with slightly exponential backoff wait time between tries.
        """
        base_url_parts = urlsplit(self.url)[:2]

        v(LOG_CRAWLING.format(self.name))
        self.error = None
        try:
            result = requests.get(self.url, headers=HEADERS)
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
                if self.expose_url_pattern is not None:
                    matches = re.findall(self.expose_url_pattern, result.text)
                else:
                    self.offers.add(Offer(EMAIL_SITE_NO_LIST_TEXT.format(self.url)))
                    return
                for match in matches:
                    match_url = match if isinstance(match, str) else match.group(1)
                    if not urlparse(match_url).scheme:
                        match_url = urlunparse(base_url_parts + (match_url, "", "", ""))
                    if self.check_and_update_known(
                        match_url, include_known=include_known
                    ):
                        self.offers.add(Offer(match_url, self.expose_details))
                if not matches:
                    self.error = ERR_SUCCESS_NO_MATCHES.format(self.name)
            elif self.none_str and (self.none_str in result.text):
                v(LOG_NO_FLATS.format(self.name))
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
                err(LOG_WARN.format(self.name, self.error, retries))
                time.sleep(backoff)
                return self.check(retries - 1, (backoff + 2) * 1.5)
            else:
                err(LOG_ERR.format(self.name, self.error))

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
            known_file_path = Path(KNOWN_FILE)
            known_file_path.touch()
            with known_file_path.open("r+") as known_file:
                if any(True for known in known_file if url in known):
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
        return (
            self.error
            if self.error
            else repr(
                [(o.url, o.details.details if o.details else None) for o in self.offers]
            )
        )


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
            result = requests.get(self.url, headers=HEADERS)
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
        v(LOG_NEW_RESULTS)
        mail_subject, mail_text = format_mail(results)
        if options.no_email:
            print(f"{mail_subject}\n\n{mail_text}")
        else:
            send_mail(mail_subject, mail_text)
            v(LOG_EMAIL_SENT)
        vv(results)
    else:
        v(LOG_NO_NEW_RESULTS)
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
    dump_sites_path = Path("debug-sites")
    dump_sites_path.mkdir(parents=True, exist_ok=True)
    site_debug_path = dump_sites_path / f"sites-{name}.html"
    with site_debug_path.open("w") as site_dump:
        print(html, file=site_dump)


def v(*msg):
    if VERBOSITY > 0 and not QUIET:
        print(*msg)


def vv(*msg):
    if VERBOSITY > 1 and not QUIET:
        print(*msg)


def err(*msg):
    if not QUIET:
        print(*msg, file=sys.stderr)


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
            " Use 'service@' to print a service file that allows a User parameter."
            " Use 'install' to create the service and timer in"
            " ~/.local/share/systemd/user/. Use 'run' to install, start and enable"
            " the timer, all in one command."
        ),
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Don't send email, print email text to stdout",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Increase verbosity (1 shows progress, 2 dumps raw results at the end)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Print no messages, not even errors"
    )
    parser.add_argument(
        "--include-known", action="store_true", help="Include known results"
    )
    args = parser.parse_args()
    VERBOSITY = args.verbose or 0
    QUIET = args.quiet or False
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
