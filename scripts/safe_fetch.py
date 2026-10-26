"""Bounded, address-pinned public HTTP(S) retrieval. No proxy or cookie support."""
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit

MAX_BYTES = 3_000_000
HEADERS = {'User-Agent': 'IbrahimBlogResearch/1.0', 'Accept': 'text/html,application/rss+xml,application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.1', 'Accept-Encoding':'identity'}

class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self.address = address
    def connect(self):
        sock = socket.create_connection((self.address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)

class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self.address = address
    def connect(self): self.sock = socket.create_connection((self.address, self.port), self.timeout)

def resolve_public(host, port):
    if host.lower() == 'localhost' or host.lower().endswith(('.local','.internal')): raise ValueError('local host denied')
    addresses = list(dict.fromkeys(x[4][0] for x in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)))
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses): raise ValueError('non-public DNS answer denied')
    return addresses

def fetch(url, *, timeout=25, limit=MAX_BYTES, redirects=5):
    for _ in range(redirects + 1):
        u=urlsplit(url)
        if u.scheme not in ('http','https') or not u.hostname or u.username is not None or u.password is not None: raise ValueError('invalid public URL')
        port=u.port or (443 if u.scheme == 'https' else 80)
        if port not in (80,443): raise ValueError('nonstandard port denied')
        host=u.hostname
        addresses=resolve_public(host,port)
        path=u.path or '/'
        if u.query: path += '?' + u.query
        last=None
        for address in addresses:
            conn=(PinnedHTTPS if u.scheme == 'https' else PinnedHTTP)(host,port,address,timeout)
            try:
                conn.request('GET',path,headers=HEADERS)
                resp=conn.getresponse()
                if resp.status in (301,302,303,307,308):
                    location=resp.getheader('Location'); resp.read(1024)
                    if not location: raise ValueError('redirect without location')
                    url=urljoin(url,location); break
                if resp.status < 200 or resp.status >= 300: raise ValueError('HTTP '+str(resp.status))
                length=resp.getheader('Content-Length')
                if length and int(length)>limit: raise ValueError('response too large')
                body=resp.read(limit+1)
                if len(body)>limit: raise ValueError('response too large')
                return body,url,resp.getheader('Content-Type','')
            except (OSError,http.client.HTTPException) as exc: last=exc
            finally: conn.close()
        else:
            raise ValueError(f'connection failed: {last}')
    raise ValueError('too many redirects')
