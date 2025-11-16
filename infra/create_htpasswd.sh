#!/bin/bash

FILENAME="users.htpasswd"
PASSWORD="hello"

echo "Generating $FILENAME..."

# Loop from 1 to 50
for i in {1..50}
do
    USERNAME="user$i"

    if [ $i -eq 1 ]; then
        htpasswd -c -b "$FILENAME" "$USERNAME" "$PASSWORD"
    else
        htpasswd -b "$FILENAME" "$USERNAME" "$PASSWORD"
    fi
done

echo "Success! Created 50 users in $FILENAME."