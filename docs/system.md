# Installation systeme

## Global

```
apt update
apt install sqlite3 nginx grafana  python3-pip python3-virtualenv certbot python3-certbot-nginx
```

## Postgresql

## Grafana

```
apt install -y apt-transport-https
apt install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -

echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

```

## Admin web UI

https://github.com/nodesource/distributions/blob/master/README.md#debinstall

(As ubuntu user)

Install nodejs & yarn :
```
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install --global yarn
```

Configure :
```
cp .env.example .env
# edit .env
```

Build the app (static html) :
```
cd /srv/aereni/admin
yarn install
yarn build
```

Content root for nginx is : `/srv/aereni/admin/build`


## Backend API

```
cd /srv/aereni/backend

virtualenv venv
source venv/bin/activate
python --version # should be 3.8 !
pip install -r requirements.txt

cp aereni.cfg.example aereni.cfg
# edit aereni.cfg

sudo ln -s $(pwd)/aereni-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aereni-backend.service 
```
