# Mikapod Soil
[![Documentation Status](https://readthedocs.org/projects/mikapod-soil/badge/?version=latest)](https://mikapod-soil.readthedocs.io/en/latest/?badge=latest)

## Introduction

Mikapod Soil is an open-source application software used by IoT devices to track time-series data of soil-based plants and upload the data to [Mikaponics.com](https://mikaponics.com) where it will be analyed and processed for customers so they can know the health and well-being of their plants.

## Features

* Supports collection of instrument time-series data from 6 different sensors:
    - Temperature
    - Humidity
    - Pressure
    - Altitude
    - Illuminance
    - Soil Moisture
* Stores time-series data in local database
* Upload time-series data to [Mikaponics API Web-service](https://github.com/mikaponics/mikaponics-back).
* Supports **OAuth 2.0 Client credentials** authorization and SSL communication
* Supports **MessagePack** encoding format for more efficient bandwith and energy usage
* Powered by open-source hardware and software!

## Installation

Please read the [documentation](https://mikapod-soil.readthedocs.io/en/latest/) on instructions for installation.

## License
This application is licensed under the **BSD** license. See [LICENSE](LICENSE) for more information.
