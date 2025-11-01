#!/bin/bash

ADDRESSBOOK="addressbook.txt"

search_entry() {
    echo -n "Enter search term: "
    read term
    grep -i "$term" "$ADDRESSBOOK"
}

add_entry() {
    echo -n "Enter Name: "
    read name
    echo -n "Enter Surname: "
    read surname
    echo -n "Enter Email: "
    read email
    echo -n "Enter Phone: "
    read phone
    record="$name|$surname|$email|$phone"

    echo "New record: $record"
    echo -n "Save this record? (y/n): "
    read confirm
    if [ "$confirm" = "y" ]; then
        echo "$record" >> "$ADDRESSBOOK"
        echo "Record saved."
    else
        echo "Cancelled."
    fi
}

remove_entry() {
    echo -n "Enter search term for record to remove: "
    read term
    grep -in "$term" "$ADDRESSBOOK"
    echo -n "Enter line number of record to delete: "
    read lineno
    if [ -n "$lineno" ]; then
        sed -i "${lineno}d" "$ADDRESSBOOK"
        echo "Record deleted."
    else
        echo "Cancelled."
    fi
}

display_entries() {
    echo "------ Address Book ------"
    nl -w2 -s". " "$ADDRESSBOOK"
    echo "--------------------------"
}

while true; do
    echo
    echo "===== Address Book Menu ====="
    echo "1. Search Address Book"
    echo "2. Add Entry"
    echo "3. Remove Entry"
    echo "4. Display All Entries"
    echo "5. Exit"
    echo "============================="
    echo -n "Enter choice [1-5]: "
    read choice

    case $choice in
        1) search_entry ;;
        2) add_entry ;;
        3) remove_entry ;;
        4) display_entries ;;
        5) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid choice, try again." ;;
    esac
done

