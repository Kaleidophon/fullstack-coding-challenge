# Hackebabel

## Requirements
* Recommended on local machines: sudo apt-get install python-virtualenv

## Setting up and starting preisvergleich_api on local machine
1. Working with virtualenv and installing requirements

        $ virtualenv virtual-env
        $ source virtual-env/bin/activate
        $ pip install -r requirements.txt

	Make also use you have MongoDB installed. If not, follow the instructions
	under https://www.mongodb.com/
	Then, use the following commands:

		$ cd Hackerbabel/data/db
		$ cd mongod --dpath ./

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
	$ nosetests -vsxd --nologcapture hackerbabel/testing/
