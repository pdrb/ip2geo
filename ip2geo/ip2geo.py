#!/usr/bin/env python

# ip2geo 0.4
# author: Pedro Buteri Gonring
# email: pedro@bigode.net
# date: 20200423

import json
import sys
import time
import codecs
import optparse
import socket
import random

if sys.version_info[0:2] <= (2, 7):
    import urllib2
    from urllib import urlencode
else:
    import urllib.request as urllib2
    from urllib.parse import urlencode


_version = "0.4"


# Parse and validate arguments
def get_parsed_args():
    usage = "usage: %prog [ip|hostname] [options]"
    # Create the parser
    parser = optparse.OptionParser(
        description="get geolocation from IP address or hostname, can use: "
        "'ip-api.com', 'freegeoip.net', 'ipinfo.io', 'coding.tools' or 'db-ip.com' "
        "ip to city lite database for local lookup",
        usage=usage,
        version=_version,
    )
    parser.add_option(
        "-g",
        dest="api",
        default="ipapi",
        choices=("ipapi", "freegeoip", "ipinfo", "coding"),
        help="geolocation api to use: 'ipapi', 'freegeoip', 'ipinfo' or 'coding'"
        "(default: %default)",
    )
    parser.add_option(
        "-s",
        dest="sleep",
        default=1.5,
        type=float,
        help="time to sleep between http requests (default: %default)",
    )
    parser.add_option(
        "-t",
        dest="timeout",
        default=5,
        type=int,
        help="timeout in seconds to wait for reply (default: %default)",
    )
    parser.add_option(
        "-d",
        dest="database_file",
        help="local lookup using db-ip.com ip to city lite database mmdb: "
        "https://db-ip.com/db/download/ip-to-city-lite, the "
        "maxminddb module must be installed: "
        "https://github.com/maxmind/MaxMind-DB-Reader-python",
    )
    parser.add_option(
        "-i",
        dest="input_file",
        help="use ips/hostnames from input file (one ip/hostname per line)",
    )
    parser.add_option(
        "-o", dest="output_file", help="save geolocation information to file",
    )

    # Print help if no argument is given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    # Parse the args
    (options, args) = parser.parse_args()

    # Some args validation
    if len(args) == 0 and not options.input_file:
        parser.error("missing ip/hostname or input file")
    if len(args) == 1 and options.input_file:
        parser.error("ip and file provided, only one needed")
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    if options.sleep < 0:
        parser.error("sleep time cannot be a negative number")
    if options.timeout < 1:
        parser.error("timeout must be a positive number")
    return options, args


# Return the http response
def get_http_response(url, ip, values=None):
    user_agent = "ip2geo/" + _version
    headers = {"User-Agent": user_agent}
    if values:
        data = urlencode(values)
        req = urllib2.Request(url, data=data.encode("utf-8"), headers=headers)
    else:
        req = urllib2.Request(url, headers=headers)
    try:
        resp = urllib2.urlopen(req).read()
    except urllib2.URLError as ex:
        if hasattr(ex, "reason"):
            print("%s - %s" % (ip, ex.reason))
            return None
        elif hasattr(ex, "code"):
            print("%s - %s" % (ip, ex))
            return None
    return resp


# Get geolocation from "ip-api.com"
def get_geo_ipapi(ip):
    query_url = "http://ip-api.com/json/" + ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp.decode("utf-8"))
    except (TypeError, ValueError):
        return None
    # Uses dict.get to set a default empty value if a key doesnt exists and to
    # avoid 'KeyError' exceptions
    location = {
        "country": geo.get("country", ""),
        "country_code": geo.get("countryCode", ""),
        "region": geo.get("regionName", ""),
        "region_code": geo.get("region", ""),
        "city": geo.get("city", ""),
        "org": geo.get("org", ""),
    }
    return location


# Get geolocation from "freegeoip.net"
def get_geo_freegeoip(ip):
    query_url = "https://freegeoip.app/json/" + ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp.decode("utf-8"))
    except (TypeError, ValueError):
        return None
    location = {
        "country": geo.get("country_name", ""),
        "country_code": geo.get("country_code", ""),
        "region": geo.get("region_name", ""),
        "region_code": geo.get("region_code", ""),
        "city": geo.get("city", ""),
    }
    return location


# Get geolocation from "ipinfo.io"
def get_geo_ipinfo(ip):
    query_url = "http://ipinfo.io/%s/json" % ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp.decode("utf-8"))
    except (TypeError, ValueError):
        return None
    location = {
        "country": geo.get("country", ""),
        "region": geo.get("region", ""),
        "city": geo.get("city", ""),
    }
    return location


# Get geolocation from "coding.tools"
def get_geo_coding(ip):
    query_url = "https://coding.tools/my-ip-address"
    values = {"queryIp": ip}
    resp = get_http_response(query_url, ip, values)
    if not resp:
        return None
    try:
        geo = json.loads(resp.decode("utf-8"))
    except (TypeError, ValueError):
        return None
    location = {
        "country": geo.get("country_name", ""),
        "country_code": geo.get("country_code", ""),
        "region": geo.get("region_name", ""),
        "city": geo.get("city_name", ""),
    }
    return location


# Generate line to be printed for "ip-api.com"
def get_print_ipapi(location, ip):
    if not location["country"].strip():
        return "%s - Unknown (Maybe reserved range?)" % ip

    print_info = "%s - %s (%s)" % (ip, location["country"], location["country_code"])
    if location["city"].strip():
        print_info = "%s, %s (%s), %s" % (
            print_info,
            location["region"],
            location["region_code"],
            location["city"],
        )
    elif location["region"].strip():
        print_info = "%s, %s (%s)" % (
            print_info,
            location["region"],
            location["region_code"],
        )
    if location["org"]:
        print_info = print_info + " - " + location["org"]
    return print_info


# Generate line to be printed for "freegeoip.net"
def get_print_freegeoip(location, ip):
    if not location["country"].strip():
        return "%s - Unknown (Maybe reserved range?)" % ip

    print_info = "%s - %s (%s)" % (ip, location["country"], location["country_code"])
    if location["city"].strip():
        print_info = "%s, %s (%s), %s" % (
            print_info,
            location["region"],
            location["region_code"],
            location["city"],
        )
    elif location["region"].strip():
        print_info = "%s, %s (%s)" % (
            print_info,
            location["region"],
            location["region_code"],
        )
    return print_info


# Generate line to be printed for "ipinfo.io"
def get_print_ipinfo(location, ip):
    if not location["country"].strip():
        return "%s - Unknown (Maybe reserved range?)" % ip

    print_info = "%s - %s" % (ip, location["country"])
    if location["city"].strip():
        print_info = "%s, %s, %s" % (print_info, location["region"], location["city"])
    elif location["region"].strip():
        print_info = "%s, %s" % (print_info, location["region"])
    return print_info


# Generate line to be printed for "coding.tools"
def get_print_coding(location, ip):
    if location["country"] == "-":
        return "%s - Unknown (Maybe reserved range?)" % ip

    print_info = "%s - %s (%s), %s, %s" % (
        ip,
        location["country"],
        location["country_code"],
        location["region"],
        location["city"],
    )
    return print_info


# Return the one line formatted information
def get_print_info(api, ip):
    if api == "ipapi":
        location = get_geo_ipapi(ip)
        if location:
            print_info = get_print_ipapi(location, ip)
            return print_info
    elif api == "freegeoip":
        location = get_geo_freegeoip(ip)
        if location:
            print_info = get_print_freegeoip(location, ip)
            return print_info
    elif api == "ipinfo":
        location = get_geo_ipinfo(ip)
        if location:
            print_info = get_print_ipinfo(location, ip)
            return print_info
    elif api == "coding":
        location = get_geo_coding(ip)
        if location:
            print_info = get_print_coding(location, ip)
            return print_info
    return None


# Local lookup
def local_lookup(ip, reader):
    info = reader.get(ip)
    if info is not None:
        country_code = info["country"]["iso_code"]
        country_name = info["country"]["names"]["en"]
        try:
            region = info["subdivisions"][0]["names"]["en"]
        except KeyError:
            region = None
        city = info["city"]["names"]["en"]
        print_info = "%s - %s (%s)" % (ip, country_name, country_code)
        if region:
            print_info = "%s, %s, %s" % (print_info, region, city)
        else:
            print_info = "%s, %s" % (print_info, city)
    else:
        print_info = "%s - Unknown (Maybe reserved range?)" % ip
    return print_info


# Write output to file, open with codecs 'utf-8' to write non ascii text
def write_to_file(output_file, print_info):
    with codecs.open(output_file, "a", encoding="utf-8") as f:
        f.write("%s\n" % print_info)


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

    if options.database_file:
        import maxminddb

        reader = maxminddb.open_database(options.database_file)

    try:
        if not options.input_file:
            ip = get_ip(args[0])
            if not ip:
                print("Invalid IP or hostname: %s" % args[0])
                sys.exit(1)
            if not options.database_file:
                print_info = get_print_info(options.api, ip)
            else:
                print_info = local_lookup(ip, reader)
            if print_info:
                if sys.version_info[0:2] <= (2, 7):
                    # Set encoding fix pipe '|' redirects for non ascii text
                    print(print_info.encode("utf-8"))
                else:
                    print(print_info)
            if options.output_file:
                write_to_file(options.output_file, print_info)
        # Get ips/hostnames from file
        else:
            with open(options.input_file, "r") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                ip = get_ip(line)
                if not ip:
                    print("Invalid IP or hostname: %s" % line)
                    continue
                if not options.database_file:
                    print_info = get_print_info(options.api, ip)
                else:
                    print_info = local_lookup(ip, reader)
                if print_info:
                    if sys.version_info[0:2] <= (2, 7):
                        # Uses sys.stdout and flush to print to terminal asap
                        sys.stdout.write(print_info.encode("utf-8") + "\n")
                    else:
                        sys.stdout.write(print_info + "\n")
                    sys.stdout.flush()
                    if options.output_file:
                        write_to_file(options.output_file, print_info)
                if not options.database_file:
                    time.sleep(options.sleep)
    except KeyboardInterrupt:
        print("Aborting.")
        sys.exit(1)


# Run cli function if invoked from shell
if __name__ == "__main__":
    cli()
