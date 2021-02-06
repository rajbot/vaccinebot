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
#pip3 install xvfbwrapper
pip3 install pyvirtualdisplay
```

# Run vaccination site crawler
```bash
export CHROMEDRIVER_PATH=/path/to/chromedriver
killall chrome #kill any old chrome processes that may have hung
nice ./crawler.py
```
