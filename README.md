# Enhanced Bulk GitHub README Downloader

## Description

The Enhanced Bulk GitHub README Downloader is a Python script that automates the process of downloading README.md files from multiple GitHub repositories, including both public and private repositories. This tool is particularly useful for developers, researchers, or anyone who needs to quickly gather documentation from various GitHub projects.

## Features

- Download README.md files from multiple GitHub repositories in one go
- Support for both public and private repositories
- Accept input from a file containing GitHub repository URLs
- Specify custom output folder for downloaded files
- Generate a detailed report of the download process
- Combine all downloaded README files into a single document with a table of contents (optional)
- Support for command-line arguments or interactive input
- Handle both absolute and relative file paths
- Real-time progress updates during the download process

## Requirements

- Python 3.6+
- `requests` library
- Git (for handling private repositories)

## Installation

1. Clone the repository:
```
git clone https://github.com/charlpcronje/Bulk-GitHub-Readme-Downloader.git
```

2. Navigate to the project directory:
```
cd Bulk-GitHub-Readme-Downloader
```

3. Install the required library:
```
pip install requests
```

4. Ensure Git is installed on your system

## Usage

You can run the script in three ways:

1. With both input file and output folder as command-line arguments:
```
python main.py path/to/your/file.txt path/to/output/folder
```

2. With only the input file as a command-line argument (you'll be prompted for the output folder):
```
python main.py path/to/your/file.txt
```

3. Without arguments (you'll be prompted to enter both the file path and output folder):
```
python main.py
```

The input file should contain one GitHub repository URL per line. For example:

```
https://github.com/username/repo1
https://github.com/username/repo2
https://github.com/another-user/another-repo
```

## Output

The script will create the specified output folder if it doesn't exist. Each downloaded README.md file will be saved in this directory, named after its respective repository.

A detailed report of the download process will be generated and saved as `download_report.txt` in the output folder.

After the download process, you'll be asked if you want to combine all README files into a single document. If you choose to do so, you'll be prompted to provide a name for the combined file.

## Error Handling

- If the input file is not found, the script will display an error message and exit.
- For public repositories, if a README.md file cannot be downloaded, the script will print an error message in the report.
- For private repositories, the script will attempt to clone the repository, extract the README.md, and then remove the cloned repository.
- The script provides real-time updates on the progress, including success and failure messages for each repository.

## Limitations

- The script assumes that the README.md file is in the main branch of the repository. It may not work for repositories that use