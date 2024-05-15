# Production Setup
## Setup .env file
Copy the same .env file as used in this project for local development and edit the individual variables.

## Run the project
Since there is no docker-compose in production, which we wanted to use to run the whole project, we use individual **redeploy\*.sh** scripts for this. These scripts are used to stop a given service, delete a given docker image, restore it from the registry, and restart it.

## Notes:
We planned to create an **updater.sh** script that would automatically look at the docker registry at regular intervals and compare the hash of the downloaded docker image with the latest image hash in the registry. If a new version was detected, that image would be automatically downloaded. Due to lack of time, we did not manage to implement this.
