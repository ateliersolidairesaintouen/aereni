# Installation systeme

## Influxdb
https://docs.influxdata.com/influxdb/v1.8/introduction/install/#influxdb-oss-installation-requirements

```
wget -qO- https://repos.influxdata.com/influxdb.key | gpg --dearmor > /etc/apt/trusted.gpg.d/influxdb.gpg
export DISTRIB_ID=$(lsb_release -si); export DISTRIB_CODENAME=$(lsb_release -sc)
echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" > /etc/apt/sources.list.d/influxdb.list
```

## Grafana

```
apt install -y apt-transport-https
apt install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -

echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

```

## Global

```
apt update
apt install sqlite3 nginx influxdb grafana python3-pip python3-virtualenv certbot python3-certbot-nginx
```

## NodeJS

https://github.com/nodesource/distributions/blob/master/README.md#debinstall
```
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```


