|Downloads|

ip2geo
======

Get geolocation information from IP address or hostname. Uses: 'ip-api.com',
'freegeoip.net', 'ipinfo.io' or 'coding.tools'. Can also do a local lookup using
`DB-IP.com <https://db-ip.com/>`_ `IP to City Lite <https://db-ip.com/db/download/ip-to-city-lite>`_ MMDB Database.

Simple example::

    $ ip2geo 8.8.8.8
    8.8.8.8 - United States (US), California (CA), Mountain View - Google

Local lookup::

    $ ip2geo 8.8.8.8 -d dbip-city-lite.mmdb
    8.8.8.8 - United States (US), New Jersey, Newark

Please note the following:

- http://ip-api.com/ (default) has a 45 requests per minute restriction

The script by default will sleep 1.5s between each request when doing multiple
lookups using an input file. This is done to comply to the restrictions on
'ip-api.com'. The sleep time can be changed using the '-s' switch.


Notes
=====

- Works on Python 2 and Python 3
- Uses only Python standard library for remote lookup


Install
=======

Install using pip::

    pip install ip2geo

or

Download and set executable permission on the script file::

    chmod +x ip2geo.py

or

Download and run using the python interpreter::

    python ip2geo.py

For local lookup the maxminddb module is needed::

    pip install maxminddb


Usage
=====

::

    Usage: ip2geo.py [ip|hostname] [options]

    get geolocation from IP address or hostname, can use: 'ip-api.com',
    'freegeoip.net', 'ipinfo.io', 'coding.tools' or 'db-ip.com' ip to city lite
    database for local lookup

    Options:
        --version         show program's version number and exit
        -h, --help        show this help message and exit
        -g API            geolocation api to use: 'ipapi', 'freegeoip', 'ipinfo' or
                          'coding'(default: ipapi)
        -s SLEEP          time to sleep between http requests (default: 1.5)
        -t TIMEOUT        timeout in seconds to wait for reply (default: 5)
        -d DATABASE_FILE  local lookup using db-ip.com ip to city lite database
                          mmdb: https://db-ip.com/db/download/ip-to-city-lite, the
                          maxminddb module must be installed:
                          https://github.com/maxmind/MaxMind-DB-Reader-python
        -i INPUT_FILE     use ips/hostnames from input file (one ip/hostname per
                          line)
        -o OUTPUT_FILE    save geolocation information to file


Examples
========

Get geolocation from IP or hostname::

    $ ip2geo google.com

Get geolocation using 'coding.tools' api::

    $ ip2geo google.com -g coding

Uses an input file containing multiple ips/hostnames (one per line)::

    $ ip2geo -i ips.txt

Save output to file::

    $ ip2geo -i ips.txt -o geo_info.txt


.. |Downloads| image:: https://pepy.tech/badge/ip2geo
