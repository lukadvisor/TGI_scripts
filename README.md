# TGI_scripts

## Pre-requisite:
The entire package **must be run in python 3.8.10** (any other version other than that may cause errors). In order not to modify your current environment, it is recommended to create a virtual environment with python 3.8.10 and install the package there.

To do so, I recommend install Anaconda, which allows to manage virtual environments very easily:
https://docs.continuum.io/anaconda/install/linux/

After installing anaconda, a new virtual environment with python 3.8.10 can be created as follows:
```shell script
conda create --name TGI python=3.8.10
```
And then remember to activate the environment **every time** you work with this package:
```shell script
conda activate TGI
```

## Installation

To install the package:
```shell script
git clone https://github.com/lukadvisor/TGI_scripts
cd TGI_scripts
pip install scrapy
pip install bs4
pip install -U deep_translator
pip install adal
```

**Note**
If you see the following errors during installation, just ignore:
```shell script
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
requests-oauthlib 1.3.0 requires oauthlib>=3.0.0, which is not installed.
httpx 0.13.3 requires chardet==3.*, which is not installed.
django-oauth-toolkit 1.5.0 requires oauthlib>=3.1.0, which is not installed.
rotating-free-proxies 0.1.2 requires beautifulsoup4==4.8.2, but you have beautifulsoup4 4.10.0 which is incompatible.
httpx 0.13.3 requires idna==2.*, but you have idna 3.3 which is incompatible. 
```

## Compile libraries

Libraries must be compiled before use - to compile just one module (e.g. aldisued):
```shell script
make aldisued
```
Or if you want to compile all module at once:
```shell script
make all
```

## Run scripts
To crawl one source (e.g. aldisued) and create the .csv file containing the data, run the following command:
```shell script
python run_crawler.py aldisued
```
Now you are ready to write data from .csv into database.

### Note: pre-requisite before writing into database

Before writing into the database, **you have to create a file named .env** containing CLIENT_ID, CLIENT_SECRET etc. (see .env_example in this package for reference). The value of these variables must remain secret, so the .env SHOULD NEVER be committed.

After that, to write data from .csv file into database simply run the command:
```shell script
python write_to_db_v1.py aldisued
```

Alternatively, to run both crawler and script to write into database in one go you can use:
```shell script
python crawl_and_write_to_db.py aldisued
```

## Job scheduling

You can schedule jobs to be executed at a certain time (and specific frequency) by using crontab.
If not install, install it with:
```shell script
sudo apt-get update
sudo apt-get install cron
```

Then create crontab with:
```shell script
crontab -e
```

And add one line for each job to schedule. Remember to include the complete path to the script's directory (check with 'pwd' command in shell to see current directory), e.g if your directory is /home/myname/TGI_scripts, then the job should be scheduled as follows:
```shell script
45 23 * * 6 python /home/myname/TGI_scripts/crawl_and_write_to_db.py aldisued > /home/myname/TGI_scripts/aldisued.log
```
This command will run the script on aldisued every Saturday (6) at 23.45 (with output printed on a log file 'aldisued.log'). Please check cron wiki page for more explanations about the syntax:
https://en.wikipedia.org/wiki/Cron#Overview


## A few final notes about the crawlers

Web scraping is not 'an exact science' - websites keep adding new protections to prevent their data from being scraped.
One of the methods used is block a certain IP address if too many requests are sent from that address.
Currently, it seems that two of the sources (carrefour and walmart) use this method - therefore, the scripts for these two sources may stop running after a certain amount of data has been crawled. In order to avoid that, please consider using a VPN (temporary solution, as it allows to use 1 IP only) or a rotational proxy (better, as it allows to rotate among different IP addresses, therefore avoiding the block).
