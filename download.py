import requests
import filecmp
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

URLs = {
    'BAG_test_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx',
    'BAG_report_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-datengrundlage-lagebericht.xlsx.download.xlsx/200325_Datengrundlage_Grafiken_COVID-19-Bericht.xlsx',
    'BAG_cases_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx',
    'BAG_covid19_website': 'https://www.covid19.admin.ch',
    'BAG_2020_Q1': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/bisherige-lageberichte-q1-2020.zip.download.zip/Lageberichte_Quartal_1_2020_DE.zip',
    'BAG_2020_Q2': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/bisherige-lageberichte-q2-2020.zip.download.zip/Lageberichte_Quartal_2_2020_DE.zip',
    'BAG_2020_Q3': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/bisherige-lageberichte-q3-2020.zip.download.zip/Lageberichte_Quartal_3_2020_DE.zip',
    'BAG_2020_Q4': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/bisherige-lageberichte-q4-2020.zip.download.zip/Lageberichte_Quartal_4_2020_DE.zip'
}

def download(url, target_dir = Path.cwd(), file_name = None, overwrite = False):
    '''
    Downloads a file from an url into target_dir. If no file_name is probided, the file is named
    as defined by the url. In case there is already a file named file_name within target_dir, overwrite=True
    needs to be set to force saving the download.
    '''
    # get the file name from url if fn is None
    if file_name is None:
        file_name = url.split('/')[-1]
    # exit if the file already exists and overwrite = False
    f = target_dir / file_name
    if (f.exists() and not overwrite):
        return
    # download and save the file
    r = requests.get(url, allow_redirects=True)
    open(f, 'wb').write(r.content)
    return f

    
def download_if_new(url, target_dir, suffix = ''):
    '''
    Downloads a file fro url and stores it in target_dir unless there is already a file with
    the same content (byte-by-byte comparison).
    '''
    # get the last modified file
    try:
        time, latest = max((f.stat().st_mtime, f) for f in target_dir.glob('*' + suffix))
    except ValueError as e:
        latest = None
    # download the current file from bag
    f_download = download(url, target_dir, file_name = 'tmp', overwrite = True)
    
    # compare the latest file with the current download
    if (latest is None):
        same = False
    else:
        same = filecmp.cmp(str(latest), str(f_download), shallow = False)
    
    # rename or remove the current download if defferent from the previous file
    if not same:
        prefix = datetime.now().strftime("%Y-%m-%d_%H-%M")
        f_new = target_dir / (prefix + '_' + url.split('/')[-1])
        f_download.replace(f_new)
    else:
        f_download.unlink()
        
def get_link_url(website, link_name, append_to_website = False):  
    page = requests.get(website)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract and store in top_items according to instructions on the left
    links = soup.select('a')
    url = None
    for link in soup.select('a'):
        text = link.text
        text = text.strip() if text is not None else ''
        if (text == link_name):
            url = link.get('href')
            url = url.strip() if url is not None else ''
            break
    
    if (append_to_website):
        url = website + url

    return url


# data directory definitions
daily_reports_dir = Path('downloads/daily_reports')
report_data_dir = Path('downloads/report_data')
test_data_dir = Path('downloads/test_data')
cases_data_dir = Path('downloads/cases_data')
csv_data_dir = Path('downloads/csv_data')
json_data_dir = Path('downloads/json_data')

# create data directories
Path.mkdir(daily_reports_dir, exist_ok = True)
Path.mkdir(report_data_dir, exist_ok = True)
Path.mkdir(test_data_dir, exist_ok = True)
Path.mkdir(cases_data_dir, exist_ok = True)
Path.mkdir(csv_data_dir, exist_ok = True)
Path.mkdir(json_data_dir, exist_ok = True)

# download new data
download_if_new(URLs['BAG_2020_Q1'], daily_reports_dir, suffix = 'Quartal_1_2020_DE.zip')
download_if_new(URLs['BAG_2020_Q2'], daily_reports_dir, suffix = 'Quartal_2_2020_DE.zip')
download_if_new(URLs['BAG_2020_Q3'], daily_reports_dir, suffix = 'Quartal_3_2020_DE.zip')
download_if_new(URLs['BAG_2020_Q4'], daily_reports_dir, suffix = 'Quartal_4_2020_DE.zip')
#
download_if_new(URLs['BAG_report_data'], report_data_dir, suffix = '.xlsx')
download_if_new(URLs['BAG_test_data'], test_data_dir, suffix = '.xlsx')
download_if_new(URLs['BAG_cases_data'], cases_data_dir, suffix = '.xlsx')
#
csv_url = get_link_url(URLs['BAG_covid19_website'], link_name = 'Daten als .csv', append_to_website = True)
download_if_new(csv_url, csv_data_dir, suffix = '.zip')
#
json_url = get_link_url(URLs['BAG_covid19_website'], link_name = 'Daten als .json', append_to_website = True)
download_if_new(json_url, json_data_dir, suffix = '.zip')