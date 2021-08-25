# PyHOLA

A Python implementation to download sensor data using HOLOGRAM API.

The base module contains the `Hologram` Class. This class is initialized with the device, organization and API key data. The `retrieve` method downloads the data, and stores it as unique records in the `records` instance variable.

## TODOS
- Download data as CSV file with column names.
- GUI implementation