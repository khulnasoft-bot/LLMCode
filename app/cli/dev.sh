#!/usr/bin/env bash

OUT="${LLMCODE_DEV_CLI_OUT_DIR:-/usr/local/bin}"
NAME="${LLMCODE_DEV_CLI_NAME:-llmcode-dev}"
ALIAS="${LLMCODE_DEV_CLI_ALIAS:-g4cd}"

# Double quote to prevent globbing and word splitting.
go build -o "$NAME" &&
    rm -f "$OUT"/"$NAME" &&
    cp "$NAME" "$OUT"/"$NAME" &&
    ln -sf "$OUT"/"$NAME" "$OUT"/"$ALIAS" &&
    echo built "$NAME" cli and added "$ALIAS" alias to "$OUT"
