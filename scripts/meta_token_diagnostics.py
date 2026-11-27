#!/usr/bin/env python3
"""Read-only Meta token diagnostics; never display access tokens or secret values."""
import json,os,urllib.error,urllib.parse,urllib.request
BASE="https://graph.facebook.com/v27.0"
PAGE="100499538904729"
IG="17841458273487103"
token=os.getenv("META_PAGE_ACCESS_TOKEN","")
if not token:raise SystemExit("Meta secret absent")
def probe(path,fields):
    url=BASE+"/"+path+"?"+urllib.parse.urlencode({"fields":fields,"access_token":token})
    try:
        with urllib.request.urlopen(url,timeout=20) as resp:
            data=json.load(resp)
            return {"success":True,"id_matches_page":data.get("id")==PAGE if path==PAGE else None,
                    "has_derived_page_token":bool(data.get("access_token")) if "access_token" in fields else None}
    except urllib.error.HTTPError as exc:
        try:body=json.loads(exc.read(3000));code=body.get("error",{}).get("code")
        except Exception:code=None
        return {"success":False,"http_status":exc.code,"graph_error_code":code}
for label,path,fields in [
 ("token_owner","me","id,name"),
 ("page_visibility",PAGE,"id,name"),
 ("page_token_derivable",PAGE,"id,access_token"),
 ("instagram_visibility",IG,"id,username")]:
 print(label,json.dumps(probe(path,fields)))
