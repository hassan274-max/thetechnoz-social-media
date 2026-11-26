#!/usr/bin/env python3
"""One-time local OAuth setup for TheTechnoz personal LinkedIn publisher.

Run on YOUR computer, not in GitHub Actions or ChatGPT.
Uses LinkedIn 3-legged OAuth (confidential client), localhost callback,
OpenID profile identity (optional Sign In product), and optional GitHub CLI
secrets upload. Never writes token/client secret to disk or prints them.
"""
import getpass
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

REDIRECT="http://localhost:8765/linkedin-callback"
REPO="hassan274-max/thetechnoz-social-media"
AUTH="https://www.linkedin.com/oauth/v2/authorization"
EXCHANGE="https://www.linkedin.com/oauth/v2/accessToken"
USERINFO="https://api.linkedin.com/v2/userinfo"

def request_json(url, data=None, headers=None):
    req=urllib.request.Request(url,data=data,headers=headers or {},method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"LinkedIn request rejected with HTTP {exc.code}. Check the app's products, redirect URL and OAuth scopes.") from None

def save_secret(name,value):
    p=subprocess.run(["gh","secret","set",name,"--repo",REPO],
        input=value,text=True,capture_output=True,check=False)
    if p.returncode:
        raise RuntimeError(f"GitHub CLI rejected secret {name}. Run gh auth login, check repository access, and retry locally.")
    print(f"GitHub Actions secret {name} was saved securely.")

def main():
    print("TheTechnoz — personal LinkedIn OAuth setup")
    print("In LinkedIn Developer App > Auth > Authorized redirect URLs, add EXACTLY:")
    print(" ",REDIRECT)
    print("Add 'Sign In with LinkedIn using OpenID Connect' product so the script can verify the member ID.")
    print("Only use this on your own computer; NEVER share access tokens or client secrets in chat.")
    input("Press Enter after saving that redirect URL and enabling OpenID Connect...")
    cid=input("LinkedIn App Client ID: ").strip()
    csecret=getpass.getpass("LinkedIn App Client Secret (hidden): ").strip()
    if not cid or not csecret:
        raise RuntimeError("Client ID and Client Secret are required")
    state=secrets.token_urlsafe(30)
    # LinkedIn will reject unprovisioned scope requests. If it does,
    # enable Sign In with LinkedIn using OpenID Connect first.
    scopes="openid profile w_member_social"
    uri=AUTH+"?"+urllib.parse.urlencode({
        "response_type":"code","client_id":cid,"redirect_uri":REDIRECT,
        "state":state,"scope":scopes,
    })
    received={}
    class OAuthHandler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_GET(self):
            parsed=urllib.parse.urlparse(self.path)
            query=urllib.parse.parse_qs(parsed.query)
            valid=(parsed.path=="/linkedin-callback" and query.get("state",[""])[0]==state)
            if valid:
                received["code"]=query.get("code",[""])[0]
                received["error"]=query.get("error",[""])[0]
            self.send_response(200 if valid else 400)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(("<h2>LinkedIn authorization received. Return to the terminal.</h2>"
                if valid else "<h2>Invalid callback; authorization not accepted.</h2>").encode())
    server=HTTPServer(("127.0.0.1",8765),OAuthHandler)
    server.timeout=180
    print("Opening LinkedIn consent in your browser...")
    webbrowser.open(uri)
    server.handle_request()
    server.server_close()
    code=received.get("code")
    if not code or received.get("error"):
        raise RuntimeError("Authorization was not completed. Verify redirect and both LinkedIn products.")
    token_doc=request_json(EXCHANGE,urllib.parse.urlencode({
        "grant_type":"authorization_code","code":code,"redirect_uri":REDIRECT,
        "client_id":cid,"client_secret":csecret,
    }).encode(),{"Content-Type":"application/x-www-form-urlencoded"})
    access=token_doc.get("access_token","")
    if not access:
        raise RuntimeError("Token exchange returned no access token")
    granted=set(token_doc.get("scope","").split()) if token_doc.get("scope") else set(scopes.split())
    if "w_member_social" not in granted:
        raise RuntimeError("Personal publishing scope not granted")
    identity=request_json(USERINFO,headers={"Authorization":"Bearer "+access})
    sub=identity.get("sub","")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+",sub):
        raise RuntimeError("LinkedIn userinfo did not provide a valid member ID. Verify OpenID Connect approval.")
    urn="urn:li:person:"+sub
    print("LinkedIn identity verified:",identity.get("name") or "LinkedIn member")
    print("Member author URN:",urn)
    print("w_member_social permission requested and authorized.")
    if not shutil.which("gh"):
        print("Install GitHub CLI and run 'gh auth login' to securely save credentials. No secrets were saved.")
        return
    if input("Save the access token and member URN directly in GitHub Actions secrets? [y/N] ").strip().lower()!="y":
        print("Nothing saved to GitHub. Re-run to authorize later.")
        return
    save_secret("LINKEDIN_ACCESS_TOKEN",access)
    save_secret("LINKEDIN_PERSON_URN",urn)
    print("Credentials saved. Do NOT enable LINKEDIN_DIRECT_ENABLED until the connection preflight passes.")
    print("GitHub workflow: https://github.com/"+REPO+"/actions/workflows/linkedin-direct-daily.yml")
    print("LinkedIn access tokens expire. Re-run this setup when authorization expires.")

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("Setup stopped:",str(exc),file=sys.stderr)
        sys.exit(1)
