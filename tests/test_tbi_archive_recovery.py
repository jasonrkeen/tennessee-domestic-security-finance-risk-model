"""Synthetic tests: only relevant archive metadata may leave the history database."""
import json
import sqlite3
from research.tbi_archive_recovery.extract_history import extract, safe_url, utc


def fixture():
    db=sqlite3.connect(':memory:')
    db.executescript('''CREATE TABLE downloads(id INTEGER,target_path TEXT,tab_url TEXT,start_time INTEGER,end_time INTEGER,received_bytes INTEGER,total_bytes INTEGER,state INTEGER,interrupt_reason INTEGER,hash BLOB);
    CREATE TABLE downloads_url_chains(id INTEGER,chain_index INTEGER,url TEXT);
    CREATE TABLE urls(id INTEGER,url TEXT); CREATE TABLE visits(url INTEGER,visit_time INTEGER);''')
    return db


def test_url_allowlist_drops_identity_tokens_and_unrelated_hosts():
    result=safe_url('https://crimeinsight.tbi.tn.gov/public/View/dispview.aspx?ReportId=52&userId=PRIVATE&token=SECRET#fragment')
    assert result['parameters']=={'ReportId':['52']}
    assert 'PRIVATE' not in json.dumps(result) and 'SECRET' not in json.dumps(result)
    assert safe_url('https://crimeinsight.tbi.tn.gov.example.org/?ReportId=52') is None
    assert safe_url('https://example.org/?ReportId=52') is None


def test_chromium_time_conversion_is_explicit_utc():
    assert utc(0)=='1601-01-01T00:00:00+00:00'
    assert utc(13424433798925940)=='2026-05-28T09:23:18.925940+00:00'


def test_extract_keeps_download_metadata_without_paths_or_private_rows():
    db=fixture()
    db.executemany('INSERT INTO downloads VALUES(?,?,?,?,?,?,?,?,?,?)',[
        (1,r'C:\Private\Downloads\Crimes Rates by Jurisdiction.csv','https://crimeinsight.tbi.tn.gov/public/View/dispview.aspx',1,2,9798,9798,1,0,b''),
        (2,r'C:\Private\personal.csv','https://example.org',1,2,9,9,1,0,b''),
        (3,r'C:\Private\Crimes Rates by Jurisdiction.csv','https://example.org',1,2,9,9,1,0,b'')])
    db.execute('INSERT INTO downloads_url_chains VALUES(1,0,?)',('https://crimeinsight.tbi.tn.gov/public/View/dispview.aspx?DownloadFormat=CSV&token=SECRET',))
    result=extract(db);db.close()
    assert len(result['downloads'])==1
    record=result['downloads'][0]
    assert record['filename']=='Crimes Rates by Jurisdiction.csv'
    assert record['stored_hash_bytes']==0
    assert record['received_bytes']==9798
    assert all(t not in json.dumps(result) for t in ['Private','personal.csv','SECRET'])


def test_definition_visit_is_metadata_only_and_preserves_its_date():
    db=fixture()
    db.execute('INSERT INTO urls VALUES(1,?)',('https://crimeinsight.tbi.tn.gov/public/View/ReportDefinitionSpawned.aspx?ReportId=52&userId=PRIVATE&SelectedMembersDisplayLimit=10',))
    db.execute('INSERT INTO visits VALUES(1,1)')
    result=extract(db);db.close()
    assert result['downloads']==[]
    row=result['report_definition_visits'][0]
    assert row['parameters']=={'ReportId':['52'],'SelectedMembersDisplayLimit':['10']}
    assert 'selected_members' not in row


def test_empty_history_does_not_invent_recovery():
    db=fixture();result=extract(db);db.close()
    assert result['downloads']==[] and result['report_definition_visits']==[]
