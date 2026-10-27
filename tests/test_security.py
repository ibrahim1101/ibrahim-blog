import sys, unittest, socket
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import safe_fetch
class SecurityTests(unittest.TestCase):
    def test_public_address(self):
        with patch('safe_fetch.socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443))]): self.assertEqual(safe_fetch.resolve_public('example.com',443),['8.8.8.8'])
    def test_private_dns_and_mixed_answers_denied(self):
        for ips in [('127.0.0.1',),('8.8.8.8','10.0.0.1'),('169.254.169.254',),('::1',)]:
            with self.subTest(ips=ips),patch('safe_fetch.socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,443)) for ip in ips]):
                with self.assertRaises(ValueError): safe_fetch.resolve_public('example.com',443)
    def test_unsafe_urls(self):
        for url in ['file:///etc/passwd','http://user:pass@example.com','https://localhost/x','https://example.com:9000/']:
            with self.subTest(url=url):
                with self.assertRaises(ValueError): safe_fetch.fetch(url)
    def test_redirect_is_revalidated(self):
        class Response:
            status=302
            def getheader(self,*args): return 'http://127.0.0.1/'
            def read(self,*args): return b''
        class Connection:
            def __init__(self,*a): pass
            def request(self,*a,**kw): pass
            def getresponse(self): return Response()
            def close(self): pass
        def dns(host,port):
            if host=='127.0.0.1': raise ValueError('private')
            return ['8.8.8.8']
        with patch('safe_fetch.resolve_public',side_effect=dns),patch('safe_fetch.PinnedHTTPS',Connection):
            with self.assertRaises(ValueError): safe_fetch.fetch('https://example.com/start')
    def test_redirect_checks_each_url_before_connecting(self):
        class Response:
            def __init__(self,redirect): self.status=302 if redirect else 200;self.redirect=redirect
            def getheader(self,name,default=None): return 'https://other.example/article' if name=='Location' else 'text/html' if name=='Content-Type' else default
            def read(self,*args): return b'body'
        class Connection:
            count=0
            def __init__(self,*a): pass
            def request(self,*a,**kw): pass
            def getresponse(self): Connection.count+=1;return Response(Connection.count==1)
            def close(self): pass
        visited=[]
        with patch('safe_fetch.resolve_public',return_value=['8.8.8.8']),patch('safe_fetch.PinnedHTTPS',Connection):
            safe_fetch.fetch('https://example.com/start',before_request=visited.append)
        self.assertEqual(visited,['https://example.com/start','https://other.example/article'])
if __name__=='__main__': unittest.main()
