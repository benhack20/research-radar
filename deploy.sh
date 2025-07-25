#!/bin/bash

# 首次部署需要在根目录增加.env文件，在aminer目录增加TOKEN文件，并配置nginx代理

# 以下为更新部署的脚本

git pull

docker compose up -d --build

sudo rm -rf /www/server/nginx/proxy_cache_dir/*

sudo nginx -s reload

echo "Deploy completed"#!/bin/bash

# 首次部署需要在根目录增加.env文件，在aminer目录增加TOKEN文件，并配置nginx代理

# 以下为更新部署的脚本

git pull

docker compose up -d --build

sudo rm -rf /www/server/nginx/proxy_cache_dir/*

sudo nginx -s reload

echo "Deploy completed"