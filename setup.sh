#!/bin/bash

# Update and install required packages
echo -e "\033[38;2;0;255;0m[+] Updating packages...\033[0m"
pkg update -y && pkg upgrade -y

echo -e "\033[38;2;0;255;0m[+] Installing required packages...\033[0m"
pkg install -y python wget curl ncurses-utils git openssl nano ffmpeg

# Setup storage permissions
echo -e "\033[38;2;0;255;0m[+] Setting up storage...\033[0m"
termux-setup-storage

# Install Python dependencies
echo -e "\033[38;2;0;255;0m[+] Installing Python libraries...\033[0m"
pip install yt-dlp
pip install requests
pip install bs4
pip install pytube 

# Create necessary directories
echo -e "\033[38;2;0;255;0m[+] Creating directories...\033[0m"
mkdir -p downloads
