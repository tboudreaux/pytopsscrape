#!/bin/bas

echo "Testing API"
python -m pytest api/test_api.py

echo "Testing Parser"
python -m pytest parse/test_abundance.py

echo "Testing Misc"
python -m pytest misc/test_utils.py
