#!/usr/bin/python

# ip2geo 0.2
# author: Pedro Buteri Gonring
# email: pedro@bigode.net
# date: 20171223

import urllib2
import json
import sys
import time
import codecs
import optparse
import socket
import random


version = '0.2'


# Parse and validate arguments
def get_parsed_args():
    usage = 'usage: %prog [ip|hostname] [options]'
    # Create the parser
    parser = optparse.OptionParser(
        description="get geolocation from IP address or hostname, can use: "
        "'ip-api.com', 'freegeoip.net' or 'ipinfo.io'",
        usage=usage, version=version
    )
    parser.add_option(
        '-g', dest='api', default='ipapi',
        choices=('ipapi', 'freegeoip', 'ipinfo'),
        help="geolocation api to use: 'ipapi', 'freegeoip' or 'ipinfo'"
        "(default: %default)"
    )
    parser.add_option(
        '-s', dest='sleep', default=0.5, type=float,
        help='time to sleep between requests (default: %default)'
    )
    parser.add_option(
        '-t', dest='timeout', default=5, type=int,
        help='timeout in seconds to wait for reply (default: %default)'
    )
    parser.add_option(
        '-i', dest='input_file',
        help='use ips/hostnames from input file (one ip/hostname per line)'
    )
    parser.add_option(
        '-o', dest='output_file',
        help='save geolocation information to file'
    )

    # Print help if no argument is given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    # Parse the args
    (options, args) = parser.parse_args()

    # Some args validation
    if len(args) == 0 and not options.input_file:
        parser.error('ip or file not informed')
    if len(args) == 1 and options.input_file:
        parser.error('ip and file provided, only one needed')
    if len(args) > 1:
        parser.error('incorrect number of arguments')
    if options.sleep <= 0:
        parser.error('sleep time must be a positive number')
    if options.timeout < 1:
        parser.error('timeout must be a positive number')
    return options, args


# Return a random user agent
def get_random_user_agent():
    chrome = ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
    firefox = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) '
               'Gecko/20100101 Firefox/54.0',
               'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) '
               'Gecko/20150101 Firefox/47.0 (Chrome)')
    safari = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
              'AppleWebKit/601.7.7 (KHTML, like Gecko) '
              'Version/9.1.2 Safari/601.7.7',)
    user_agents = chrome + firefox + safari
    user_agent = random.choice(user_agents)
    return user_agent


# Return the http response
def get_http_response(url, ip):
    user_agent = get_random_user_agent()
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url, headers=headers)
    try:
        resp = urllib2.urlopen(req).read()
    except urllib2.URLError as ex:
        if hasattr(ex, 'reason'):
            print "%s - %s" % (ip, ex.reason)
            return None
        elif hasattr(ex, 'code'):
            print "%s - %s" % (ip, ex)
            return None
    return resp


# Get geolocation from "ip-api.com"
def get_geo_ipapi(ip):
    query_url = 'http://ip-api.com/json/' + ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp)
    except (TypeError, ValueError):
        return None
    # Uses dict.get to set a default empty value if a key doesnt exists and to
    # avoid 'KeyError' exceptions
    location = {'country': geo.get('country', ''),
                'country_code': geo.get('countryCode', ''),
                'region': geo.get('regionName', ''),
                'region_code': geo.get('region', ''),
                'city': geo.get('city', ''),
                'org': geo.get('org', '')
                }
    return location


# Get geolocation from "freegeoip.net"
def get_geo_freegeoip(ip):
    query_url = 'http://freegeoip.net/json/' + ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp)
    except (TypeError, ValueError):
        return None
    location = {'country': geo.get('country_name', ''),
                'country_code': geo.get('country_code', ''),
                'region': geo.get('region_name', ''),
                'region_code': geo.get('region_code', ''),
                'city': geo.get('city', '')
                }
    return location


# Get geolocation from "ipinfo.io"
def get_geo_ipinfo(ip):
    query_url = 'http://ipinfo.io/%s/json' % ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp)
    except (TypeError, ValueError):
        return None
    location = {'country': geo.get('country', ''),
                'region': geo.get('region', ''),
                'city': geo.get('city', '')
                }
    return location


# Generate line to be printed based on existing information
def get_print_ipapi(location, ip):
    country, country_code, region, region_code, city, org = (
        location['country'], location['country_code'], location['region'],
        location['region_code'], location['city'], location['org'])
    if org:
        if not country.strip():
            print_info = "%s - Unknown (Maybe reserved range?)" % ip
        elif not region.strip():
            print_info = "%s - %s (%s) - %s" % (ip, country, country_code, org)
        elif not city.strip():
            print_info = "%s - %s (%s), %s (%s) - %s" % (
                ip, country, country_code, region, region_code, org)
        else:
            print_info = "%s - %s (%s), %s (%s), %s - %s" % (
                ip, country, country_code, region, region_code, city, org)
    else:
        if not country.strip():
            print_info = "%s - Unknown (Maybe reserved range?)" % ip
        elif not region.strip():
            print_info = "%s - %s (%s)" % (ip, country, country_code)
        elif not city.strip():
            print_info = "%s - %s (%s), %s (%s)" % (
                ip, country, country_code, region, region_code)
        else:
            print_info = "%s - %s (%s), %s (%s), %s" % (
                ip, country, country_code, region, region_code, city)
    return print_info


# Generate line to be printed based on existing information
def get_print_freegeoip(location, ip):
    country, country_code, region, region_code, city = (
        location['country'], location['country_code'], location['region'],
        location['region_code'], location['city'])
    if not country.strip():
        print_info = "%s - Unknown (Maybe reserved range?)" % ip
    elif not region.strip():
        print_info = "%s - %s (%s)" % (ip, country, country_code)
    elif not city.strip():
        print_info = "%s - %s (%s), %s (%s)" % (
            ip, country, country_code, region, region_code)
    else:
        print_info = "%s - %s (%s), %s (%s), %s" % (
            ip, country, country_code, region, region_code, city)
    return print_info


# Generate line to be printed based on existing information
def get_print_ipinfo(location, ip):
    country, region, city = (
        location['country'], location['region'], location['city'])
    if not country.strip():
        print_info = "%s - Unknown (Maybe reserved range?)" % ip
    elif not region.strip():
        print_info = "%s - %s" % (ip, country)
    elif not city.strip():
        print_info = "%s - %s, %s" % (ip, country, region)
    else:
        print_info = "%s - %s, %s, %s" % (ip, country, region, city)
    return print_info


# Return the one line formatted information
def get_print_info(api, ip):
    if api == 'ipapi':
        location = get_geo_ipapi(ip)
        if location:
            print_info = get_print_ipapi(location, ip)
            return print_info
    elif api == 'freegeoip':
        location = get_geo_freegeoip(ip)
        if location:
            print_info = get_print_freegeoip(location, ip)
            return print_info
    elif api == 'ipinfo':
        location = get_geo_ipinfo(ip)
        if location:
            print_info = get_print_ipinfo(location, ip)
            return print_info
    return None


# Write output to file, open with codecs 'utf-8' to write non ascii text
def write_to_file(output_file, print_info):
    with codecs.open(output_file, 'a', encoding='utf-8') as f:
        f.write('%s\n' % print_info)


# Get the host IPv4, also works as a simple IPv4 validator
def get_ip(host):
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        return None
    return remote_ip


# Main CLI
def cli():
    (options, args) = get_parsed_args()
    socket.setdefaulttimeout(options.timeout)

    try:
        if not options.input_file:
            ip = get_ip(args[0])
            if not ip:
                print "Invalid IP or hostname: %s" % args[0]
                sys.exit(1)
            print_info = get_print_info(options.api, ip)
            if print_info:
                # Set encoding fix pipe '|' redirects for non ascii text
                print print_info.encode('utf-8')
                if options.output_file:
                    write_to_file(options.output_file, print_info)

        else:
            with open(options.input_file, 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                ip = get_ip(line)
                if not ip:
                    print "Invalid IP or hostname: %s" % line
                    continue
                print_info = get_print_info(options.api, ip)
                if print_info:
                    # Uses sys.stdout and flush to print to terminal asap
                    sys.stdout.write(print_info.encode('utf-8') + '\n')
                    sys.stdout.flush()
                    if options.output_file:
                        write_to_file(options.output_file, print_info)
                time.sleep(options.sleep)
    except KeyboardInterrupt:
        print 'Aborting.'
        sys.exit(1)


# Run cli function if invoked from shell
if __name__ == '__main__':
    cli()
