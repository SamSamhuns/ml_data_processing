#!/bin/bash

echo "Removing all .DS_Store files"
find . -type f -name '*.DS_Store' -delete
find . -type f -name '*._.DS_Store' -delete

echo "Removing all __pycache__ compiled python file directory"
find . -type d -name "__pycache__" -exec rm -r "{}" +
