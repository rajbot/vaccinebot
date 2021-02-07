# Install on Ubuntu 18.04 headless
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

pip3 install beautifulsoup4 lxml
```


# Install and run on OS X

Make sure you have the Chrome browser installed first.

```bash
wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
export CHROMEDRIVER_PATH=/path/to/chromedriver

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements_osx.txt

./crawler.py
```


# Run vaccination site crawler on Ubuntu 18.04 headless
```bash
killall chrome #kill any old chrome processes that may have hung

source venv/bin/activate
export CHROMEDRIVER_PATH=/path/to/chromedriver
export HEADLESS=true

nice ./crawler.py
```

# Manually test a single county parser
```bash
# BeautifulSoup-based parser
python3 -m location_parsers.eldorado

# Selenium-based parser
python3 -m location_parsers.mono
```


# Output:
```bash
02/06/2021 09:57:35 INFO Downloading known locations
02/06/2021 09:57:36 INFO loaded 6004 locations
02/06/2021 09:57:36 INFO Parsing San Francisco County
02/06/2021 09:57:42 INFO 	Found 2 locations
02/06/2021 09:57:42 WARNING 	Moscone Center South not found in database! Please add it.
```

Once you add the missing location to the database, you will see this:
```bash
02/06/2021 10:10:36 INFO Downloading known locations
02/06/2021 10:10:37 INFO loaded 6004 locations
02/06/2021 10:10:37 INFO Parsing San Francisco County
02/06/2021 10:10:44 INFO 	Found 2 locations
02/06/2021 10:10:44 INFO 	2 locations already in database
```


# User agent:
This crawler is run by hand, and not through an automated process, using this user-agent:
```
Vaccinebot (+https://bitstream.io/vaccinebot)
```
