
# Flatcrawler

A little script to crawl certain housing association websites for new flats.

## How it works

The configuration takes a list of website URLs which are searched for certain strings,
that indicate whether any appartments are available or not. If there are, all URLs
pointing to exposes are extracted via a pattern, and sent out in an email.

## Usage

Copy `config-default.py` to a new `config.py` and edit the `MailConfig` class at the
bottom to include your email address and your login password.

You can also add new webpages in `sites.py` along the lines of the existing ones... Let
me know (create an issue, or a pull request maybe) if there are any more one should add.

Then either run the `crawler.py` script directly, or use the _systemd_ services as
[described below](#systemd). To debug or test the script, run
```
crawler.py --no-email --include-known
```
to skip email sending and print all items that would be sent in a new run.

## Dependencies

* Python >= 3.6
* [requests](http://docs.python-requests.org/en/master/user/install/#install)
* [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)

## systemd

You can create systemd service and timer files from the script itself by calling it with
the parameter `service` and `timer` respectively:

```bash
./crawler.py service > ~/.local/share/systemd/user/flatcrawler.service
./crawler.py timer > ~/.local/share/systemd/user/flatcrawler.timer
systemctl --user daemon-reload
systemctl --user enable --now flatcrawler.timer
```

The timer defaults to a one hour interval (delayed randomly by up to 15min).


If you don't want to run all the above on your own, you can use the `install` command to
just install the service files or the `run` command to install the service files and
start the timer right away.


Check that the timer is running with:

```bash
systemctl --user status flatcrawler.timer
```

## Contributing

Please follow these guidelines when contributing code to the project:

Use [**black**](https://black.readthedocs.io/en/stable/) to format all Python source
code! (All _black_ options on default values.)

Commit messages should look like this:

```shell
Add brief summary line of 50 characters or less
  ## empty line ##
In the message body write mainly _why_ you you did the change, not
just _what_ changed. Keep the message body text line-length to 70
characters or less.

Use _active_ and _present_ tense. Ideally, the summary and message
should describe what the commit changes when applied.
```

Read the license note below about CC0 and attribution. Understand that attribution is
usually given gladly and where due, but is strictly optional. This includes everyone.

Thank you!

## License

This software has a [CC0](https://creativecommons.org/publicdomain/zero/1.0/) license.

You may use this code without attribution, that is without mentioning where it's from or
who wrote it. I would actually prefer if you didn't mention me. You may even claim it's
your own.
