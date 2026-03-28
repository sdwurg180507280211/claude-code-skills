#!/usr/bin/env python3
import socket
import json
import sys

def check_proxy(host, port):
    """Check if proxy is available on given port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def find_proxy():
    """Find available proxy from common ports"""
    ports = [7890, 7891, 1087, 8080]
    host = "127.0.0.1"

    for port in ports:
        if check_proxy(host, port):
            return {"proxy": f"http://{host}:{port}", "available": True, "port": port}

    return {"available": False}

if __name__ == "__main__":
    result = find_proxy()
    print(json.dumps(result))
    sys.exit(0 if result["available"] else 1)
