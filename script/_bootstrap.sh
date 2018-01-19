#!/bin/bash

# Pull in the config from /books.txt . This path is relative to the root of the repo (parent of ./script/)
source ./books.txt

# A helper function that looks up the uuid of a book given the book name as the argument
style_name_to_uuid() {
  style_name_arg="${1}"

  for config in "${BOOK_CONFIGS[@]}"; do
    read -r uuid _ style_name _ <<< "${config}"

    if [[ "${style_name}" == "${style_name_arg}" ]]; then
      echo "${uuid}"
    fi
  done
}
