#!/bin/bash
#cp -rpv *.py  $HOME/.coursetools/
rm -f /opt/conda/lib/python3.9/site-packages/coursetools
ln -sf $PWD /opt/conda/lib/python3.9/site-packages/coursetools
