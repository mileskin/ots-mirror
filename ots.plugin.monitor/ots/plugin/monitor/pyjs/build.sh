#!/bin/bash
pyjsbuild demo_chart.py
cp -r output/* /var/www/chart_demo/
ln -s /var/www/chart_demo/demo_chart.html /var/www/chart_demo/index.html