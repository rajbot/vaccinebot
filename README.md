# Install on ubuntu 18.04
```bash
sudo apt-get update
sudo apt-get install -y libappindicator1 fonts-liberation
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
sudo apt-get --fix-broken install
sudo dpkg -i google-chrome*.deb

wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip
sudo apt-get install unzip
unzip chromedriver_linux64.zip

python3 -m venv venv
source venv/bin/activate
pip3 install selenium

sudo apt-get install xvfb
pip3 install wheel
pip3 install pyvirtualdisplay
```


# Run vaccination site crawler
```bash
export CHROMEDRIVER_PATH=/path/to/chromedriver
killall chrome #kill any old chrome processes that may have hung
nice ./crawler.py
```


# Output:
```bash
02/06/2021 09:57:35 INFO Downloading known locations
02/06/2021 09:57:36 INFO loaded 6004 locations
02/06/2021 09:57:36 INFO Parsing San Francisco County
02/06/2021 09:57:42 INFO 	Found 2 locations
02/06/2021 09:57:42 WARNING 	Moscone Center South not found in database! Please add it.
```


# User agent:
This crawler is run by hand, and not through an automated process, using this user-agent:
```
Vaccinebot (+https://bitstream.io/vaccinebot)
```
