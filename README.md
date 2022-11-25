Download the latest server.jar from here and rename it to server.jar: https://www.minecraft.net/en-us/download/server

Create a directory called 'java_server' inside of the github repo and put ther server.jar file inside of it.

Run the python script from the command line. You will likely need to run 'pip install PyDrive2' once before you do this to install the necessary python dependencies

If nether and end aren't working, check that all DIM folders are located in the world directory, not in the world_nether and world_the_end directory - there is a different structure for paper vs java servers.