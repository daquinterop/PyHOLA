# PyHOLA

A Python implementation to download sensor data using HOLOGRAM API.

The base module contains the `Hologram` Class. This class is initialized with the device, organization and API key data. The `retrieve` method downloads the data, and stores it as unique records in the `records` instance variable. The `save_records` method writes the downloaded records to a new file, or append the new records to an existing file.

## TODOS
- Renaming columns in the file to save
- GUI implementation

## INSTALL

You can Install the Library using pip:

`pip install PyHOLA`
