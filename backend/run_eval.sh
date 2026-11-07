#!/bin/bash
# run_eval.sh
#
# Safely runs the evaluation script by removing the problematic Hiddify proxy
# environment variables before execution.
#
# Unlike the previous version, Hugging Face offline mode is no longer forced
# because it would prevent downloading new models that are not already cached.
# Removing the proxy variables alone is sufficient.
#
# Usage (instead of "python3 evaluate.py"):
#   ./run_eval.sh

cd "$(dirname "$0")" || exit 1

source venv/bin/activate

export HF_HUB_DISABLE_XET=1

env -u http_proxy -u https_proxy -u all_proxy -u ftp_proxy \
    -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u FTP_PROXY \
    python3 evaluate.py