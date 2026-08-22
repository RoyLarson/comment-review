#!/usr/bin/env bash
# fx.sh -- one small script.

set -euo pipefail

# Prints the sum of two integers.
function add() {
  echo $(( $1 + $2 ))  # a trailing comment
}

url="http://example.com/not-a-comment"

add 1 2
