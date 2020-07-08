#!/bin/bash
add-apt-repository -y ppa:avsm/ppa
apt update -y
apt install -y git gcc make m4
apt install -y opam strace
