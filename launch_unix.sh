#!/bin/bash
# Shell script to download Python (Linux/macOS), extract, install dependencies, and run the bot
REQS_PATH="requirements.txt"

# Check if Python 3.9 is already installed 
if command -v python &> /dev/null && python --version | cut -d '.' -f 1,2 | grep -q "Python 3.9"; then
    PYTHON_EXE="python"
    echo "Using system Python"
else
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        echo "Installing Python..."
        if ! sudo apt-get install -y python3.9.13; then
            echo "Failed to install Python"
            read -p "Press [Enter] to exit..."
            exit 1
        fi
        PYTHON_EXE="python"
        echo "Python installed successfully!"
    elif [[ "$OSTYPE" == "darwin" ]]; then
        # For macOS
        PYTHON_URL="https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg"
        PKG_PATH="python.pkg"
        if [[ -f "$PKG_PATH" ]]; then
            echo "Python is already downloaded!"
        else
            echo "Downloading Python..."
            if ! curl -L "$PYTHON_URL" -o "$PKG_PATH"; then
                echo "Failed to download Python."
                read -p "Press [Enter] to exit..."
                exit 1
            fi
            echo "Download completed successfully."

            echo "Installing Python..."

            sudo installer -pkg "$PKG_PATH" -target /

            if [ $? -eq 0 ]; then
                echo "Installation completed successfully."
            else
                echo "Installation failed."
                read -p "Press [Enter] to exit..."
                exit 1
            fi

            read -p "Press [Enter] after installing python..."
        fi

        # Check if Python executable exists
        if ! command -v "$PYTHON_EXE" &> /dev/null; then
            echo "Python executable not found!"
            read -p "Press [Enter] to exit..."
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys" ]]; then
        echo "This is Windows OS. Please use launch_win.bat to run the bot."
        read -p "Press [Enter] to exit..."
        exit 1
    else
        echo "Unsupported OS: $OSTYPE. Please install Python 3.9.13 manually."
        read -p "Press [Enter] to exit..."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "dokbot" ]]; then
    echo "Creating virtual environment 'dokbot'..."
    "$PYTHON_EXE" -m venv dokbot
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press [Enter] to exit..."
        exit 1
    fi
fi

# Set Python executable to the virtual environment
echo "Activating virtual environment"
command "$PWD/dokbot/scripts/activate"

# Install dependencies
echo "Installing dependencies..."

echo "Upgrading pip..."
if ! "$PYTHON_EXE" -m pip install --upgrade pip; then
    echo "Failed to upgrade pip."
    read -p "Press [Enter] to exit..."
    exit 1
fi
echo "Pip upgrade completed successfully."

echo "Installing packages from requirements.txt..."
if ! "$PYTHON_EXE" -m pip install -r "$REQS_PATH"; then
    echo "Failed to install dependencies."
    read -p "Press [Enter] to exit..."
    exit 1
fi
echo "Package installation completed successfully."

echo "Initialization complete! Starting the bot..."

"$PYTHON_EXE" launch_bot.py