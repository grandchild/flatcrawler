
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

You can create a systemd service file from the script itself by calling it with
the parameter `systemd`:

```bash
./crawler.py systemd > ~/.local/share/systemd/user/flatcrawler.service
systemctl --user daemon-reload
systemctl enable --now flatcrawler
```

Check that it's running with:
```bash
systemctl --user status flatcrawler
```
