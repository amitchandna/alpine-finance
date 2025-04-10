#!/bin/zsh

# Add the Alpine Finance Directory to the path to be found by python moving forward.
current_directory="$PWD"
export PATH="$PATH:$current_directory"
echo "Added the current_directory to the system path."
python3 -m pip install -r requirements.txt
echo "Installed the python package requirements"

echo "Would you like to spin up the Docker Container for the psql db? (y/n)"
read input
if [ "$input" == "y" ]
then
echo "..."
cd django_project
docker-compose up -d
echo "Initialized the docker container containing the psql database"
else
echo "No database initialized"
fi



