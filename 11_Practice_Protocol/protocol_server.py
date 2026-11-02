#!/usr/bin/env python3
"""Loopback-only HTTP facade for the ArcaneXus Practice Protocol. Does not execute actions."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import protocol

MAX_BODY=32768

class Handler(BaseHTTPRequestHandler):
    server_version="ArcaneXusPractice/1.0"
    def log_message(self,fmt,*args): pass
    def send_json(self,code,obj):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers(); self.wfile.write(raw)
    def read_body(self):
        n=int(self.headers.get("Content-Length","0"))
        if n<1 or n>MAX_BODY: raise ValueError("invalid request body size")
        value=json.loads(self.rfile.read(n))
        if not isinstance(value,dict): raise ValueError("JSON object required")
        return value
    def do_GET(self):
        path=urlparse(self.path).path
        try:
            if path=="/" or path=="/console":
                raw=(protocol.ROOT/"console.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(raw)))
                self.send_header("Cache-Control","no-store")
                self.end_headers(); self.wfile.write(raw); return
            if path=="/api/v1/practice/health":
                return self.send_json(200,{"status":"OK","service":"ArcaneXus Practice Protocol","version":"1.0","execution":"disabled"})
            if path=="/api/v1/practice/operations":
                return self.send_json(200,protocol.status_report())
            prefix="/api/v1/practice/operations/"
            if path.startswith(prefix):
                oid=path[len(prefix):]
                return self.send_json(200,protocol.status_report(oid))
            return self.send_json(404,{"error":"not found"})
        except Exception as e: return self.send_json(400,{"error":str(e)})
    def do_POST(self):
        try:
            path=urlparse(self.path).path
            body=self.read_body()
            if path=="/api/v1/practice/operations":
                oid,row=protocol.define(body.get("system_id"),body.get("intent"),
                    body.get("success_condition"),body.get("failure_condition"),
                    body.get("actor"),body.get("parent_operation_id"))
                return self.send_json(201,{"operation_id":oid,"stage":"DEFINE","event_hash":row["event_hash"]})
            prefix="/api/v1/practice/operations/"
            if path.startswith(prefix):
                parts=path[len(prefix):].split("/")
                if len(parts)!=2: return self.send_json(404,{"error":"expected operation_id/stage"})
                oid,stage=parts
                row=protocol.advance(oid,stage.upper(),body.get("actor"),body.get("data",{}))
                return self.send_json(200,{"operation_id":oid,"stage":row["event_type"],"event_hash":row["event_hash"]})
            return self.send_json(404,{"error":"not found"})
        except PermissionError as e: return self.send_json(403,{"error":str(e)})
        except (ValueError,KeyError,TypeError) as e: return self.send_json(400,{"error":str(e)})
        except Exception as e: return self.send_json(500,{"error":str(e)})

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=1131)
    a=ap.parse_args()
    if a.host not in ("127.0.0.1","::1","localhost"):
        raise SystemExit("Refusing non-loopback bind: this facade has no remote authentication")
    server=ThreadingHTTPServer((a.host,a.port),Handler)
    print(f"ArcaneXus Practice Protocol API listening on http://{a.host}:{a.port}",flush=True)
    server.serve_forever()

if __name__=="__main__": main()
