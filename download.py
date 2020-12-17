import requests
import filecmp
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

URLs = {
    'BAG_test_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx',
    'BAG_report_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-datengrundlage-lagebericht.xlsx.download.xlsx/200325_Datengrundlage_Grafiken_COVID-19-Bericht.xlsx',
    'BAG_cases_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx',
    'BAG_covid19_website': 'https://www.covid19.admin.ch'
    
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
        
def get_csv_url(website, append_to_website = False):  
    page = requests.get(website)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract and store in top_items according to instructions on the left
    links = soup.select('a')
    url = None
    for link in soup.select('a'):
        text = link.text
        text = text.strip() if text is not None else ''
        if (text == 'Daten als .csv'):
            url = link.get('href')
            url = url.strip() if url is not None else ''
            break
    
    if (append_to_website):
        url = website + url

    return url

# download new data
download_if_new(URLs['BAG_report_data'], Path('downloads/report_data'), suffix = '.xlsx')
download_if_new(URLs['BAG_test_data'], Path('downloads/test_data'), suffix = '.xlsx')
download_if_new(URLs['BAG_cases_data'], Path('downloads/cases_data'), suffix = '.xlsx')

csv_url = get_csv_url(URLs['BAG_covid19_website'], append_to_website = True)
download_if_new(csv_url, Path('downloads/csv_data'), suffix = '.zip')