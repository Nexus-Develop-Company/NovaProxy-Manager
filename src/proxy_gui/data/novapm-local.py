#!/usr/bin/env python3
"""Local proxy that adds Basic auth to upstream corporate proxy."""
import socket, select, base64, sys, os

CONFIG_FILE = os.path.expanduser("~/.config/proxy/proxy.conf")

def load_config():
    cfg = {}
    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg

def tunnel(client, upstream):
    sockets = [client, upstream]
    while sockets:
        r, _, _ = select.select(sockets, [], [], 60)
        if not r:
            break
        for s in r:
            try:
                data = s.recv(4096)
                if not data:
                    sockets.remove(s)
                    s.close()
                    continue
                if s is client:
                    upstream.sendall(data)
                else:
                    client.sendall(data)
            except:
                sockets.remove(s)
                try: s.close()
                except: pass

def handle(client):
    try:
        cfg = load_config()
        upstream_host = cfg.get("UPSTREAM_HOST", "10.12.0.205")
        upstream_port = int(cfg.get("UPSTREAM_PORT", "3128"))
        user = cfg.get("UPSTREAM_USER", "")
        passwd = cfg.get("UPSTREAM_PASS", "")
        auth = base64.b64encode(f"{user}:{passwd}".encode()).decode()

        req = client.recv(4096)
        if not req:
            return

        upstream = socket.create_connection((upstream_host, upstream_port), timeout=10)

        if req.startswith(b"CONNECT "):
            host_port = req.split(b" ")[1].decode()
            msg = f"CONNECT {host_port} HTTP/1.1\r\nProxy-Authorization: Basic {auth}\r\n\r\n"
            upstream.sendall(msg.encode())
            resp = upstream.recv(4096)
            if b"200" not in resp:
                client.sendall(resp)
                return
            client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            tunnel(client, upstream)
        else:
            first_line, rest = req.split(b"\r\n", 1)
            auth_header = f"Proxy-Authorization: Basic {auth}\r\n".encode()
            upstream.sendall(first_line + b"\r\n" + auth_header + rest)
            tunnel(upstream, client)
    except Exception as e:
        print(f"proxy-local: {e}", file=sys.stderr)
    finally:
        for s in (client, upstream):
            try: s.close()
            except: pass

def main():
    cfg = load_config()
    host = cfg.get("PROXY_HOST", "127.0.0.1")
    port = int(cfg.get("PROXY_PORT", "3128"))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)
    print(f"proxy-local: listening on {host}:{port}")
    sys.stdout.flush()
    while True:
        client, _ = server.accept()
        t = threading.Thread(target=handle, args=(client,))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    import threading
    main()
