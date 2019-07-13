# Mikaponics IoT - Mikapod (Soil) - Persistent Storage Service
The ``storage_service.py`` application is responsible for providing an interface for all applications to access and GET/SET key-value paired data in a local database.

## Installation

1. Setup our virtual environment

    ```bash
    virtualenv -p python3.6 env
    ```

2. Now lets activate virtual environment

    ```bash
    source env/bin/activate
    ```

3. Install the ``Python`` dependencies.

    ```bash
    pip install pytz                          # World Timezone Definitions
    pip install python-dotenv                 # Environment variable loader.
    pip install Pyro4                         # Distrubted objects library.
    pip install peewee                        # Peewee is a simple and small ORM.
    ```

4. In this directorym create a file called ``.env`` and populate it with the following content:

    ```
    DATABASE=storage.db
    LOCAL_TIMEZONE_NAME=America/Toronto
    ```

5. Please change the contents of the ``.env`` file to match the configuration found in your systen.

## Usage


1. Turn on our distrubted objects name-server if it has not been done already. If you are about to run this command, do not close the terminal.

  ```
  python -m Pyro4.naming
  ```

2. Open up another terminal and run our service, make sure we have the above code running before running the code below.

  ```
  python storage_service.py
  ```

3. Verify our service is working:

  ```
  pyro4-nsc list
  ```
