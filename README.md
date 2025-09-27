# Tibber2Tesla
Python Script to create a Tesla Timeplan based on Tibber Prices

The Inital Script is copied from the post under: https://github.com/evcc-io/evcc/discussions/10344#discussioncomment-7578731

The Script was not running for me because the used Tesla.py Module has (currently) an issue with the responsecode from the Tesla Backend.
Background could be found here: https://github.com/tdorssers/TeslaPy/issues/172

The Script runs in an endless loop, checking every minute if midnight is crossed and updates the prices for the new day at 0:01.</br>
I use the Script on my Raspbery running in a Screen-Console to ensure that it is running even when I'm logged out.

# Update in Version 2.x.y
The Script now supports the prices to be changed every 15 Minutes - in the Version 1.x.y it was only once per hour.
This is required as the prices in germany from 1.october on wille be changed/different every 15 minutes. 

ä known issues:
It seems to be that tesla is currently havin issues with quaterly time frames. The schedule is correctly shown in the App, but the powerwall behaivs strange. I tested to create a Plan in the App but was not able as I was onyl able to select 30 Miniutes as minimum.
So currently it's better to use the version 1

# Modules needed:
1.) Tibber   install via `python3 -m pip install tibber` </br>
2.) Tesla.py install via `python3 -m pip install teslapy`
