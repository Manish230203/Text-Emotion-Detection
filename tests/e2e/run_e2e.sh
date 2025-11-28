#!/bin/bash
set -e
URL=http://127.0.0.1:5000/predict
curl -s -X POST -H "Content-Type: application/json" -d '{"text":"I am very happy today"}' $URL | jq .
