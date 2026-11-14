"""Extract only allowlisted TBI archive metadata from a read-only Chromium history."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlsplit

HOST = 'crimeinsight.tbi.tn.gov'
DOWNLOAD_NAMES = {'Crimes Rates by Jurisdiction.csv', 'Crimes and Clearances by Offense Type.csv',
                  'Crimes and Clearances by Offense Type (1).csv', 'Crimes and Clearances by Offense Type (2).csv',
                  'Use of Force Counts and Percent Change.csv'}
PARAMETERS = {'ReportId', 'DetailedDefinition', 'SelectedMembersDisplayLimit', 'SummaryCubeId',
              'download', 'DownloadFormat', 'CsvDataFormat'}


def utc(value: int) -> str:
    return (dt.datetime(1601,1,1,tzinfo=dt.timezone.utc)+dt.timedelta(microseconds=value)).isoformat()


def safe_url(value: str) -> dict | None:
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or parsed.hostname != HOST:
        return None
    return {'host': HOST, 'path': parsed.path,
            'parameters': {k:v for k,v in parse_qs(parsed.query).items() if k in PARAMETERS}}


def extract(connection: sqlite3.Connection) -> dict:
    downloads=[]
    for row in connection.execute('SELECT id,target_path,tab_url,start_time,end_time,received_bytes,total_bytes,state,interrupt_reason,length(hash) FROM downloads ORDER BY start_time'):
        identifier,path,url,start,end,received,total,state,interrupt,hash_length=row
        # Handle Windows names even when tests run on another operating system.
        name=path.replace('\\','/').rsplit('/',1)[-1]
        page=safe_url(url)
        if name not in DOWNLOAD_NAMES or page is None:
            continue
        chains=[]
        for _, chain_url in connection.execute('SELECT chain_index,url FROM downloads_url_chains WHERE id=? ORDER BY chain_index',(identifier,)):
            safe=safe_url(chain_url)
            if safe is not None:
                chains.append(safe)
        downloads.append({'filename':name,'start_utc':utc(start),'end_utc':utc(end),
                          'received_bytes':received,'total_bytes':total,'state_code':state,
                          'interrupt_reason_code':interrupt,'stored_hash_bytes':hash_length or 0,
                          'page':page,'download_chain':chains})
    definitions=[]
    for url,time in connection.execute("SELECT u.url,v.visit_time FROM urls u JOIN visits v ON v.url=u.id WHERE u.url LIKE '%ReportDefinitionSpawned.aspx%' ORDER BY v.visit_time"):
        safe=safe_url(url)
        if safe is not None:
            definitions.append({'visit_utc':utc(time),**safe})
    return {'scope':'Allowlisted TBI download metadata and report-definition visits only',
            'downloads':downloads,'report_definition_visits':definitions,
            'limits':['No downloaded CSV contents or hashes recovered by this extraction',
                      'URLs do not recover HTTP request bodies or server-side selected members',
                      'A later definition-page visit does not establish an earlier query selection']}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    # Ordinary read-only mode respects database locks; never alter a live profile.
    with sqlite3.connect(args.history.resolve().as_uri()+'?mode=ro',uri=True,timeout=2) as connection:
        result=extract(connection)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'downloads':len(result['downloads']), 'definition_visits':len(result['report_definition_visits']),
                      'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':
    main()
