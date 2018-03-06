## Setup

1. Clone project to your local folder:
```git clone git@gitlab.newmatik.com:gunslinger/scrapy.git```

2. Install Python Scrapy:
```pip install scrapy```

3. Install dependency Incapsula cracker module:
```pip install incapsula_cracker```

## How to use
Make sure you are in the Scrapy project directory before executing scrapy commands.

### List all scrapy spiders
```scrapy list```

Currently supported spiders are:

__Arrow__
- Name: arrow
- Incapsula: yes
- Return Qty: yes
- Return Price: not implemented yet

__Digi-key__
- Name: digikey
- Incapsula: no
- Return Qty: yes
- Return Price: not implemented yet

__Farnell__
 - Name: farnell
 - Incapsula: no
 - Return Qty: yes
 - Return Price: not implemented yet
 
__Future Electronics__
 - Name: futureelectronics
 - Incapsula: yes (aggressive)
 - Return Qty: not implemented yet
 - Return Price: not implemented yet
 
__Mouser__
 - Name: mouser
 - Incapsula: no
 - Return Qty: yes
 - Return Price: not implemented yet
 
__RS Components__
 - Name: rscomponents 
 - Incapsula: no
 - Return Qty: not implemented yet (Not returning QTY due to javascript)
 - Return Price: not implemented yet
 
__Rutronik__
 - Name: rutronik
 - Incapsula: no
 - Return Qty: ???
 - Return Price: not implemented yet
 
__TME__
 - Name: tme
 - Incapsula: no
 - Return Qty: ???
 - Return Price: not implemented yet
 
__TTI Europe__
 - Name: ttieurope
 - Incapsula: yes
 - Return Qty: ???
 - Return Price: not available

### Run single spider example

Run a single crawler for "digikey" with the search term "LR2010" and store it to file "data/sampledata.json" in JSON format.

```scrapy crawl digikey -a query="LR2010" -o temp/sampledata.json -t json```

### Run all spiders

Run all registered spiders with the search term "LR2010".

```python main.py -k "LR2010"```

JSON output will be written to file "data.json".

Logfile will be written to "data/log.txt".

### Notes : 
* Code is commented for readibility and documented for future development in every file.
* Electronic scrapy crawler can handle category page, multiple page result, pagination, and single page automatically.
* Not all crawlers return quantity data. Due some quantity not displayed directly but called by ajax http request, or due to javascript, which scrapy cant handle.
* Scrapy timeout can be configured.
* Incapsula-cracker library added for bypassing incapsula web firewall and added as middleware where needed.
* Read settings.py for scrapy settings values.
* Customfunction.py holds global function that will be used by every crawler.
* Scrapy using xpath and css selector for parsing of data.

### About Documentation:

Using basic Google Style Docstrings:

```
# -*- coding: utf-8 -*-
""" Short description of the function.

More detailed description of what does this do? Please explain here in more detail.

Args:
    param1: This is the first param.
    param2: This is a second param.

Returns:
    This is a description of what is returned.

Raises:
    KeyError: Raises an exception.

TODO:
     Incapsula: unblock spider IP from incapsula on distributor firewall to remove necessity of incapsula hack
"""
```