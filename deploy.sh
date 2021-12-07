#!/usr/bin/env bash

set -xe

git pull origin main
cd admin
yarn build
cd -
sudo systemctl restart aereni-backend
systemctl status aereni-backend
