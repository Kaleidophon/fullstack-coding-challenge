# Hackebabel

## Requirements
* Recommended on local machines: sudo apt-get install python-virtualenv

## Setting up and starting preisvergleich_api on local machine
0. Getting the project

	Download it from github.com as a .zip or use
	
		$ git clone https://github.com/Kaleidophon/fullstack-coding-challenge.git 
		$ cd fullstack-coding-challenge
		$ git checkout dev

1. Working with virtualenv and installing requirements

        $ virtualenv virtual-env
        $ source virtual-env/bin/activate
        $ pip install -r requirements.txt

	Make also use you have MongoDB installed. If not, follow the instructions
	under https://www.mongodb.com/
	Then, use the following commands:

		$ mkdir data
		$ cd data
		$ mkdir db
		$ cd mongod --dpath db/

2. Adjust configuration using python file:

		The API expects a "config.py" in the root directory and / or that all
		necessary parameters are
		provided through environment variables.

3. Starting HackerBabel

        # starting preisvergleich by using provided runserver script
        $ cd preisvergleich_api/
        $ python runserver.py

4. See if it works

	Go to browser: http://127.0.0.1:5000/start
	Everything else will run automatically following the parameters stated in
	config.py.

5. Testing

	Nosetest was used in development. If you want to test the project, use e.g.
	
		$ nosetests -vsxd --nologcapture hackerbabel/testing/*
		
	Note: Because the unit test require a stable internet connection, some unit tests
	can sometimes fail due to your internet connection. If so, try to restart them
	and / or adjust EXPECTED_SPEED in hackerbabel/testing/hackernews_test.py
	specifically. Within this test failures can also occur because there are new Hacker 
	News on the webpage which the API hasn't updated yet. In this case, just try a minute
	or so later to re-run the tests.
