# Quote-Manager
A program that allows readers to organize quotes from a book. Written in Python using MySQL.

Quote Manager is a simple desktop application that allows you to manage and store your favorite quotes. It uses an SQLite database to store quotes locally, and provides an easy-to-use graphical interface built with Tkinter.

## Features
- Store, manage and view your quotes.
- SQLite database to save your quotes locally.
- Simple and intuitive GUI built with Tkinter.
- No installation required.
- If a database file (`quotes.db`) already exists in the current directory, it will be used; otherwise, a new one will be created.
- Users can choose to store and keep the database file for future use.

## Installation
### For Windows (64-bit)
1. Download the [Quote_Manager.exe](https://github.com/camelogue/Quote-Manager/releases/download/v1.1-windows/Quote_Manager.exe) file for Windows.

2. No installation required. Simply run the `.exe` file to start using the application.

### For Linux (64-bit)
1. Download and extract the [Quote_Manager_Linux.zip](https://github.com/camelogue/Quote-Manager/releases/download/v1.1-linux/Quote_Manager.zip) file for Linux.

2. Open a terminal in the extracted folder.

3. Give executable permission to the file:
```
chmod +x Quote_Manager
```

4. Run the application:
```
./Quote_Manager
```

**Dependencies**

For Linux, ensure that Tkinter is installed on your system. You can install it using:

```
sudo apt-get install python3-tk
```

## Usage

When you run the application, it will:

- Check if a file named `quotes.db` exists in the current directory.
  - If the file exists, it will use the existing database to store and retrieve quotes.
  - If the file does not exist, a new `quotes.db` file will be created in the same directory.


You can:
- Add new quotes.
- View all stored quotes.
- Edit and delete quotes as needed.

The quotes are saved locally in the `quotes.db` SQLite database file, so you can manage them even if you're offline.

## Supported Platforms
- Windows 10/11 (64-bit)
- Linux (64-bit, tested on Ubuntu 22.04)

## License
This project is licensed under the MIT License.
