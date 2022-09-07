#!/bin/bash

echo "Testing API"
cd api
python -m pytest test_api.py
cd ..

echo "Testing Parser"
cd parse
python -m pytest test_abundance.py
cd ..

echo "Testing Misc"
cd misc
python -m pytest test_utils.py
cd ..

