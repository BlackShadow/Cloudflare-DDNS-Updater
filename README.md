# Cloudflare-DDNS-Updater
A simple python script automatically updates your A records IP address in Cloudflare. Great tool for people without Static IP addresses.


# Usage

Method A: 
>Download the zip file on release tags.
>Edit settings.ini accordingly to your Cloudflare cridentials
>Run Cloudflare.exe

You don't need to install Python for Method A.

Method B: 
>Download Cloudflare.py
>Install requests using pip
>Edit settings.ini accordingly to your Cloudflare cridentials
>Run Cloudflare.py

Script will run on background and check every 15 minutes for IP changes. If settings.ini file is not present, it will create one.
