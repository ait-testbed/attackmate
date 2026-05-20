.. _playwright:

==================
Prepare Playwright
==================

To run browser-based commands with the ``browser`` executor, you need to install the Playwright browser binaries
(as of now, it only supports Chromium, so it's sufficient to install that):

::

  # Install Chromium
  playwright install chromium

  # Update package lists to ensure latest versions are available
  sudo apt-get update

  # Install required system dependencies
  sudo apt-get install -y libnss3 libnspr4 libasound2t64
