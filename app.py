import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_caching import Cache
from datetime import datetime
import requests
import re

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

cache = Cache(app,config={'CACHE_TYPE': 'SimpleCache'})

@app.route("/", methods=["GET"])
def home():
    mission = getUpcomingMissions()
    return render_template("index.html", mission=mission)

#Function caches every two hours. 7200 seconds. Saves API requests and improves performance.
@cache.cached(timeout=7200)
def getUpcomingMissions():
    #API url limits to 2 in json format and orders by datetime and only shows SpaceX launches.
    print("Fetching data from the API...")  # Debug print
    url = "https://ll.thespacedevs.com/2.3.0/launches/upcoming/?format=json&limit=2&ordering=net&lsp__name=SpaceX"
    response = requests.get(url)
    if response.status_code == 200:
        #Grab list of launches
        apiData = response.json()
        if not apiData:
            return None
        #Launch library api data for launches is contained within a list called results. This accesses it.
        launches = apiData["results"]
        print(launches)
        #Get the next launch (first in the list) and sort by most recent in terms of date/time.
        next_launch = sorted(launches, key=lambda x: x["net"])[0]
        
        #Grab the sorted date time. Then format into what we want to see.
        launch_time = datetime.strptime(next_launch["net"], "%Y-%m-%dT%H:%M:%SZ")
        formatted_time = launch_time.strftime("%A, %d %B %Y at %H:%M UTC")

        # Avoids returning No description string if description is missing. Try name and then pass empty string to avoid error if name doesn't exist.
        checkdesc = ( 
                next_launch.get("mission", {}).get("description")
                or next_launch.get("name")
                or ""
            )
       # Grab mission patch from program > mission_patches
        mission_patch = None
        programs = next_launch.get("program", [])
        if programs and isinstance(programs, list):
            first_program = programs[0]
            patches = first_program.get("mission_patches", [])
            if patches and isinstance(patches, list) and "image_url" in patches[0]:
                mission_patch = patches[0]["image_url"]

        #Call get payload info function passing in checkdesc to grab mission description or name and filter using regex.
        payload_info = get_payload_info(checkdesc)
        #Dict to map name to a key value for use in index. {} is used to stop key errors for nested data
        mission = {
            "name": next_launch["name"],
            "date_utc": formatted_time,
            "description": next_launch.get("mission", {}).get("description","No description available for this launch."),
            "payload":payload_info,
            "payload_destination":next_launch.get("mission",{}).get("orbit",{}).get("name","No orbit information available."),
            "rocket":next_launch.get("rocket",{}).get("configuration",{}).get("full_name","Rocket Information Unavailable"),
            "launch_pad":next_launch.get("pad",{}).get("name"),
            "mission_patch":mission_patch
        }
      
        return mission
    else:
        return None
#Debugging only to test API's and caching
@app.route('/clear-cache')
def clear_cache():
    cache.clear()
    return "Cache cleared"

#Method to extract payload information from description or name as Launch Library does not have a 
#dedicated payload field
def get_payload_info(data):
    if not data:
        return "Payload is Unknown"
    
    # Regex Pattern one to Look for brand names and payloads, note r in the pattern tells python to not treat backslashes as escape characters
    patternMatch = re.search(r'(\d+)\s+(Starlink|OneWeb|Iridium|Skynet|NASA|payloads?)',data,re.IGNORECASE)
    if patternMatch:
        return f"{patternMatch.group(1)} {patternMatch.group(2).capitalize()}"
    
    #Regex pattern 2 to look for Starlink group launches
    patternMatchTwo = re.search(r'(Starlink\s+Group\s+\d+-\d+)', data, re.IGNORECASE)
    if patternMatchTwo:
        return patternMatchTwo.group(1)
    
    # Third pattern to look for launches of ships or satellites that include payloads
    patternMatchThree = re.search(r'includes\s+(\d+)\s+payloads?', data, re.IGNORECASE)
    if patternMatchThree:
        return f"{patternMatchThree.group(1)} payloads"
    else:
        return "Payload is unknown."


if __name__ == "__main__":
    app.run(debug=True)