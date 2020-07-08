#!/bin/bash

force_if_conda="true"
echo "$force_if_conda"

if [ -x "$(command -v conda)" ] && [ "$force_if_conda" != "true" ]
then
    echo 'miniconda install aborted: conda is already present'
    exit 1
fi

miniconda_prefix=$1

if [ -z $miniconda_prefix ]
then
    echo 'usage: setup-conda-linux miniconda_prefix'
    exit 1
fi


if [ -d "$HOME/$miniconda_prefix" ]
then
    echo "miniconda install aborted: $HOME/$miniconda_prefix directory already exists"
    exit 1
fi

miniconda_linux=Miniconda3-latest-Linux-x86_64.sh
miniconda_darwin=Miniconda3-latest-MacOSX-x86_64.sh

miniconda_host=https://repo.anaconda.com/miniconda/


case $(uname -s) in
    Linux)
	miniconda=$miniconda_linux
	;;
    Darwin)
	miniconda=$miniconda_darwin
	;;
    *)
	echo "Unknown Operating system " $(uname -s)
	exit 1
	;;
esac

echo "downloading miniconda install..."
tmpdir=$(mktemp -d -t ci-XXXXXXXXXX)
curl $miniconda_host$miniconda -o $tmpdir/$miniconda

echo "running miniconda install..."
chmod +x $tmpdir/$miniconda
$tmpdir/$miniconda -b -p $HOME/$miniconda_prefix

echo "cleaning up the download dir..."
rm -fr tmpdir 


