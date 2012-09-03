import re, urllib

MY_IP = None

def is_valid_ip(input_str):
  return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_str) is not None

def whatismyip(site='http://ipecho.net/plain'):
  global MY_IP

  if not MY_IP:
    print("Fetching new copy of public IP from " + site + "...")
    MY_IP = urllib.urlopen(site).read()

  # FIXME: better regex is possible
  if is_valid_ip(MY_IP):
    print("Got " + MY_IP)
    return MY_IP
  else:
    print("Error: failed to fetch a valid public-facing IP address")
    return None
