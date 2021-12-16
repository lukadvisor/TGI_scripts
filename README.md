# TGI_scripts

Pre-requisite:
```shell script
sudo apt install python3 python3-pip
```

To install:
```shell script
git clone https://github.com/lukadvisor/TGI_scripts
cd TGI_scripts
pip install scrapy
pip install bs4
pip install -U deep_translator
pip install adal
```
To compile just one module (e.g. discounto):
```shell script
make discounto
```
To compile all module at once:
```shell script
make all
```

To run one crawler (e.g. aldisued) and create its .csv file:
```shell script
python run_crawler.py aldisued
```
Now you can write data from .csv into database. Before doing so, you have to create a .env containing CLIENT_ID, CLIENT_SECRET etc. (see .env_example for reference). The value of these variables must remain secret, so the .env SHOULD NEVER be committed.

After that, to write data from .csv file into database:
```shell script
python write_to_db_v1.py aldisued
```

To run crawler+script to write into database in one go:
```shell script
python crawl_and_write_to_db.py aldisued
```