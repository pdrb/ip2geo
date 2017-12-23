ip2geo
======

Get geolocation information from IP address or hostname. Uses: 'ip-api.com',
'freegeoip.net' or 'ipinfo.io'.

Simple example:

::

    $ ip2geo 8.8.8.8
    8.8.8.8 - United States (US), California (CA), Mountain View - Google

Please note the following:

- http://ip-api.com/ (default) has a 150 requests per minute restriction
- http://freegeoip.net/ has a 15,000 requests per hour restriction
- https://ipinfo.io/ has a 1,000 requests per day restriction

The script by default will pause 0.5s between each request when doing multiple
lookups using an input file. This is done to comply to the restrictions on
'ip-api.com' and 'freegeoip.net'. Just be careful when using 'ipinfo.io'.


Install
-------

Install using pip:

::

    pip install ip2geo

or

Download and set executable permission on the script file:

::

    chmod +x ip2geo.py

or

Download and run using the python interpreter:

::

    python ip2geo.py


Usage
-----

::

    Usage: ip2geo [ip|hostname] [options]

    get geolocation from IP address or hostname, can use: 'ip-api.com',
    'freegeoip.net' or 'ipinfo.io'

    Options:
    --version       show program's version number and exit
    -h, --help      show this help message and exit
    -g API          geolocation api to use: 'ipapi', 'freegeoip' or
                    'ipinfo'(default: ipapi)
    -s SLEEP        time to sleep between requests (default: 0.5)
    -t TIMEOUT      timeout in seconds to wait for reply (default: 5)
    -i INPUT_FILE   use ips/hostnames from input file (one ip/hostname per line)
    -o OUTPUT_FILE  save geolocation information to file


Examples
--------

Get geolocation from IP or hostname:

::

    $ ip2geo google.com

Get geolocation using 'freegeoip.net' api:

::

    $ ip2geo google.com -g freegeoip

Uses an input file containing multiple ips/hostnames (one per line):

::

    $ ip2geo -i ips.txt

Save output to file:

::

    $ ip2geo -i ips.txt -o geo_info.txt


Notes
-----

- Works on Python 2
- Tested on Linux and Windows, but should work on all platforms
- Uses only Python standard library for maximum compatibility
