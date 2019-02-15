
# Flatcrawler

A little script to crawl certain housing association websites for new flats.

## How it works

The configuration takes a list of website URLs which are searched for certain
strings, that indicate whether any appartments are available or not. If there
are, all URLs pointing to exposes are extracted via a pattern, and sent out in
an email.

## Usage

Copy `config-default.py` to a new `config.py` and edit the `MailConfig` class at
the bottom to include your email address and your login password.

You can also add new webpages along the lines of the existing ones... Let me
know (PR maybe) if there are any more one should add.

## Python

Uses f-strings 🤩 and thus needs python 3.6 or higher.

## systemd

You can create systemd service and timer files from the script itself by calling
it with the parameter `service` and `timer` respectively:

```bash
./crawler.py service > ~/.local/share/systemd/user/flatcrawler.service
./crawler.py timer > ~/.local/share/systemd/user/flatcrawler.timer
systemctl --user daemon-reload
systemctl enable --now flatcrawler.timer
```

The timer defaults to a one hour interval (delayed randomly by up to 15min).

Check that the service and timer are running with:

```bash
systemctl --user status flatcrawler flatcrawler.timer
```
