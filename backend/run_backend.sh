#!/bin/bash
# run_backend.sh
#
# Safely runs the backend by removing problematic proxy environment variables
# (from Hiddify) before starting the application.
#
# Hugging Face offline mode is intentionally not enabled because it would
# prevent downloading new models that are not already cached.
# Removing the proxy variables is sufficient for downloading and running models.
#
# Always use this script instead of:
#   uvicorn app.main:app --reload
#
# Run:
#   ./run_backend.sh

cd "$(dirname "$0")" || exit 1

source venv/bin/activate

export HF_HUB_DISABLE_XET=1

env -u http_proxy -u https_proxy -u all_proxy -u ftp_proxy \
    -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u FTP_PROXY \
    uvicorn app.main:app --reload