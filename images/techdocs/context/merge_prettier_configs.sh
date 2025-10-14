#!/usr/bin/env bash

# Saner programming environment. Turns common developer mistakes into errors.
set -eu -o pipefail

if [[ $# -ne 3 ]]; then
    echo "Not the right number of arguments. Got $# but expected 3."
    exit 1
fi

BASE_CONFIG_PATH="$1"
TECHDOCS_CONFIG_PATH="$2"
OUTPUT_PATH="$3"

# Exit if you don't have jq
command -v jq >/dev/null 2>&1 || {
  echo "This script requires jq: https://github.com/jqlang/jq" >&2
  exit 2
}

jq -s '
  .[0] as $base |
  .[1] as $techdocs |
  $base |
  .overrides = (
    # Start with base overrides
    .overrides as $baseOverrides |
    # Get techdocs overrides
    ($techdocs.overrides // []) as $techdocsOverrides |
    
    # For each base override, check if there is a matching techdocs override
    ($baseOverrides | map(
      . as $baseItem |
      # Find matching techdocs override by files property
      ($techdocsOverrides | map(select(.files == $baseItem.files)) | .[0]) as $matchingtechdocs |
      if $matchingtechdocs then
        # Merge options from both
        $baseItem | .options = ($baseItem.options + $matchingtechdocs.options)
      else
        # Keep base override as is
        $baseItem
      end
    )) +
    # Add techdocs overrides that dont match any base override
    ($techdocsOverrides | map(
      . as $techdocsItem |
      if ($baseOverrides | map(.files) | index($techdocsItem.files)) == null then
        $techdocsItem
      else
        empty
      end
    ))
  )
' "$BASE_CONFIG_PATH" "$TECHDOCS_CONFIG_PATH" > "$OUTPUT_PATH"

echo "Merged config written to $OUTPUT_PATH"