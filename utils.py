import re, urllib

def is_valid_ip(input_str):
  return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_str) is not None

def whatismyip():
  try:
    fip = open('ip.txt', 'r')
    ip = fip.readline()
    fip.close()
  except:
    print("No local storage of ip found. Grabbing a fresh copy...")
    ip = urllib.urlopen('http://ipecho.net/plain').read()
    fip = open('ip.txt', 'w')
    fip.write(ip)
    fip.close()

  # FIXME: better regex is possible
  if is_valid_ip(ip):
    return ip
  else:
    print("Error: failed to fetch a valid public-facing IP address")
    return None
