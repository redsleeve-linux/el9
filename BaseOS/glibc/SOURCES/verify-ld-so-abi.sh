#!/bin/bash
#
# This script verifies the ABI of ld.so by comparing the layout of
# critical data structures against a known baseline for a given architecture.
#
# This is useful to prevent unintentional ABI breaks between releases.
#
# Usage: ./elf/verify-ld-so-abi.sh <arch> <path-to-ld.so> [--generate-baseline]

set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <arch> <path-to-ld.so> [--generate-baseline]"
  exit 1
fi

ARCH="$1"
LDSO_PATH="$2"
GENERATE_BASELINE=false
if [ "${3:-}" == "--generate-baseline" ]; then
  GENERATE_BASELINE=true
fi

# The script is expected to be in the 'elf' directory and run from the glibc root.
SCRIPT_DIR="$(dirname "$0")"
BASELINE_DIR="$SCRIPT_DIR"
BASELINE_FILE="$BASELINE_DIR/ld-so-abi-$ARCH.baseline"

# List of structs and global variables to check in ld.so.
# These are critical for the dynamic linker's internal ABI.
SYMBOLS_TO_CHECK=(
  "_rtld_global_ro"
  "_rtld_global"
  "struct link_map"
  "struct pthread"
)

# Check for dependencies.
if ! command -v gdb &> /dev/null; then
  echo "Error: gdb is not installed. Please install it to continue." >&2
  exit 127
fi

if [ ! -f "$LDSO_PATH" ]; then
  echo "Error: ld.so not found at '$LDSO_PATH'" >&2
  exit 1
fi

TEMP_FILE=$(mktemp)
# Ensure the temporary file is cleaned up on script exit.
trap 'rm -f "$TEMP_FILE"' EXIT

echo "Generating current ABI layout for '$ARCH' from '$LDSO_PATH'..."

for symbol in "${SYMBOLS_TO_CHECK[@]}"; do
  echo "--- $symbol ---" >> "$TEMP_FILE"
  # Use ptype/o to get the struct layout with offsets.
  # If a symbol does not exist, GDB will exit with an error, which is
  # caught by 'set -e'.
  gdb -batch -ex "ptype/o $symbol" "$LDSO_PATH" >> "$TEMP_FILE"
done

if [ "$GENERATE_BASELINE" = true ]; then
  echo "Generating new baseline for '$ARCH'..."
  mkdir -p "$BASELINE_DIR"
  # Atomically move the new baseline into place.
  mv "$TEMP_FILE" "$BASELINE_FILE"
  echo "Baseline created at $BASELINE_FILE"
  # The temp file has been moved, so disable the trap.
  trap - EXIT
  exit 0
fi

# --- Comparison Mode ---

if [ ! -f "$BASELINE_FILE" ]; then
  echo "Error: Baseline file for architecture '$ARCH' does not exist." >&2
  echo "Path: $BASELINE_FILE" >&2
  echo >&2
  echo "To generate a new baseline, run this command with the --generate-baseline flag:" >&2
  echo "$0 $ARCH '$LDSO_PATH' --generate-baseline" >&2
  exit 77
fi

echo "Comparing with baseline file: $BASELINE_FILE"

# Compare the generated layout with the official baseline.
if ! diff -u "$BASELINE_FILE" "$TEMP_FILE"; then
  echo >&2
  echo "Error: ABI layout mismatch for '$ARCH' has been detected." >&2
  echo "The layout of structs in '$LDSO_PATH' has changed." >&2
  echo >&2
  echo "If this change is intentional, update the baseline file by running:" >&2
  echo "$0 $ARCH '$LDSO_PATH' --generate-baseline" >&2
  echo "Or by applying the diff using 'patch -R'"
  exit 1
else
  echo "OK: ABI layout for '$ARCH' is consistent with the baseline."
  exit 0
fi

