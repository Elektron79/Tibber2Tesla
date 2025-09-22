# Tibber2Tesla
Python Script to create a Tesla Timeplan based on Tibber Prices

The Inital Script is copied from the post under: https://github.com/evcc-io/evcc/discussions/10344#discussioncomment-7578731

The Script was not running for me because the used Tesla.py Module has (currently) an issue with the responsecode from the Tesla Backend.
Background could be found here: https://github.com/tdorssers/TeslaPy/issues/172

The Script runs in an endless loop, checking every minute if midnight is crossed and updates the prices for the new day at 0:01.</br>
I use the Script on my Raspbery running in a Screen-Console to ensure that it is running even when I'm logged out.

# Modules needed:
1.) Tibber   install via `python3 -m pip install tibber` </br>
2.) Tesla.py install via `python3 -m pip install tesla.py`
