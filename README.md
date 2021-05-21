[![Maintainability](https://api.codeclimate.com/v1/badges/07710df941a1ba70398e/maintainability)](https://codeclimate.com/github/wagnerdelima/challange_jobandtalent/maintainability)

# Initial Development Setup
Please install and enable the pre-commit tool to your local environment with:

    $ pip install pre-commit
    $ pre-commit install
This guarantees that a few formatting and style guidelines are met before committing your code.

In order to run the project locally without docker, do as follows:

 - Create a virtual environment

        virtualenv venv

 - Enable the virtual environment

        source /path/to/venv/bin/activate

 - Install dependencies

        pip install -r requirements.txt
        pip install -r requirements.dev.txt
        pip install -r requirements.test.txt

 - Run the project with:

        python3 manage.py runserver 0.0.0.0:8000

Please note that the docker-compose for development in this project has a bind mount attached to it. This means that
you may develop whereby docker performs a live reload of your local changes.

# Running the Project for Development Mode
In order to run the project locally in development mode, proceed as described below.

Firstly, build the development image:

    $ docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

Then, run it with

    $ docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

Remove the `-d` to see attached logs to your terminal.

# Running tests locally
Django tests are very simple to run, just a single django command needs to be executed. However, to avoid
the hassle of setting up environment variables, this project has a dockerized mechanism of running the tests.
In order to run the tests, proceed as follows:

Build the development image (unnecessary if image already built):

    $ docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

Then run the tests with:

    $ docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.tests.yml up --exit-code-from app

Once the tests are run locally, you will notice that there's a new folder within your directory structure. This directory
contains the test coverage per file. You may open the index.html and see each file's coverage.

This GitHub repo's has a CI integrated. So everytime there is a PR opened or modified it will run the tests in a
Dockerized way.


# Running for Production Purposes
The application may be run through a solo docker container with:

    $ docker-compose up -d

You do not have to build the image locally as there is a published version of this application's image hosted at Docker
Hub. You may find it at: https://hub.docker.com/repository/docker/waglds/challange_jobandtalent.

Although it's easy to run a solo application's container, it's not scalable, nor it prevents downtime. So instead, the
application may be run with Docker Swarm in an orchestrated way. If you wish to run it like that in your local machine
do as follows:

Step 1: Initiate the docker swarm in your machine:

    $ docker swarm init

Step 2: Run the docker stack

    $ docker stack deploy --compose-file docker-compose.yml challange --with-registry-auth

Step 3 (Optional): You may want to scale up the number of application instances with:

    $ docker service scale <service_name>=<number of replicas>

If you wish to see your Docker Cluster with applications running, please run this simple visualizer:

    $ docker run -it -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock dockersamples/visualizer

Then visit http://127.0.0.1:8080 to see your cluster.

