#!/bin/bash
git add .
read -p "Commit msg: " commit_msg
git commit -m "$commit_msg"
git push