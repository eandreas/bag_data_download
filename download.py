import requests
import os.path
from datetime import datetime
import filecmp

URLs = {
    'BAG_test_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx',
    'BAG_report_data': 'https://www.bag.admin.ch/dam/bag/de/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-datengrundlage-lagebericht.xlsx.download.xlsx/200325_Datengrundlage_Grafiken_COVID-19-Bericht.xlsx'
}

def download_file(url, path = '.', fn = None, overwrite = False):
    # get the file name from url if not specified by fn argument
    if fn == None:
        fn = url.split('/')[-1]
    # exit if file already exists and overwrite = False
    if ((overwrite == False) and (os.path.isfile(path + '/' + fn))):
        return
    # download and save the file
    r = requests.get(url, allow_redirects=True)
    open(path + '/' + fn, 'wb').write(r.content)

url = URLs['BAG_report_data']
target_dir = 'downloads/report_data/'

# list of all files within target_dir
ls = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]

# download the current file from bag
fn = target_dir + 'xxx_' + url.split('/')[-1]
download_file(URLs['BAG_report_data'], fn = fn, overwrite = True)

# remembers if the downloaded file should be kept, initially keep = False
keep = False

if (len(ls) < 1):
    # keep the downloaded file if it is the only one
    keep = True
else:
    # compare the downloaded file to the previous one and keep if not identical
    latest = target_dir + sorted(ls)[-1]
    print(f'comparing {latest} and {fn}')
    if not filecmp.cmp(latest, fn, shallow = False):
        keep = True
        
if keep:
    # rename and keep the downloaded file
    date_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    fn_new = target_dir + '/' + date_time + '_' + url.split('/')[-1]
    os.rename(fn, fn_new)
else:
    # delete the downloaded file
    os.remove(fn)
