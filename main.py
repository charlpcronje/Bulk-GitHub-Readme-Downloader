"""
Enhanced Bulk GitHub README Downloader with Combination Feature

This script downloads README.md files from multiple GitHub repositories,
including private repositories. It can process a list of GitHub repository URLs
from a file, specify an output folder, and produce a detailed log of the download process.
It now includes real-time progress updates and the option to combine all downloaded
README files into a single document with a table of contents.

Usage:
    python bulk_github_readme_downloader.py [file_path] [output_folder]

If no file path or output folder is provided as arguments, the script will prompt for input.
The input file should contain one GitHub repository URL per line.

Author: Charl Cronje
GitHub: https://github.com/charlpcronje/Bulk-GitHub-Readme-Downloader
"""

import requests
import os
import sys
import subprocess
from urllib.parse import urlparse
import re


def get_input_params():
    """
    Get the input file path and output folder from command-line arguments or user input.

    Returns:
    tuple: (file_path, output_folder)
    """
    if len(sys.argv) > 2:
        file_path, output_folder = sys.argv[1], sys.argv[2]
    elif len(sys.argv) > 1:
        file_path = sys.argv[1]
        output_folder = input("Enter the output folder path: ")
    else:
        file_path = input(
            "Enter the path to the file containing GitHub URLs: ")
        output_folder = input("Enter the output folder path: ")

    # Convert to absolute paths
    file_path = os.path.abspath(file_path)
    output_folder = os.path.abspath(output_folder)

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    return file_path, output_folder


def download_readme(url, output_folder):
    """
    Download the README.md file from a given GitHub repository URL.

    Args:
    url (str): The GitHub repository URL.
    output_folder (str): The folder to save the downloaded README files.

    Returns:
    tuple: (repo_name, status, error_message)
    """
    # Parse the URL to get the owner and repo name
    path = urlparse(url).path.strip("/").split("/")
    if len(path) < 2:
        return None, "Failed", f"Invalid URL format: {url}"

    owner, repo = path[-2], path[-1]

    print(f"Processing: {repo}")  # Progress update

    # Construct the raw content URL for the README.md file
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"

    # Send a GET request to the raw content URL
    response = requests.get(raw_url)

    if response.status_code == 200:
        # Create the filename
        filename = os.path.join(output_folder, f"{repo}.md")

        # Write the content to a file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Successfully downloaded: {repo}.md")  # Success message
        return repo, "Success", None
    elif response.status_code == 404:
        # Update on cloning attempt
        print(f"Public README not found for {repo}. Attempting to clone...")
        # Try to clone the repository and get README.md
        try:
            temp_dir = os.path.join(output_folder, "temp_" + repo)
            os.makedirs(temp_dir, exist_ok=True)
            subprocess.run(["git", "init"], cwd=temp_dir,
                           check=True, capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", url],
                           cwd=temp_dir, check=True, capture_output=True)
            subprocess.run(["git", "pull", "origin", "main", "--depth",
                           "1"], cwd=temp_dir, check=True, capture_output=True)

            readme_path = os.path.join(temp_dir, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as src_file:
                    content = src_file.read()

                dest_path = os.path.join(output_folder, f"{repo}.md")
                with open(dest_path, "w", encoding="utf-8") as dest_file:
                    dest_file.write(content)

                # Success message for cloning
                print(f"Successfully cloned and extracted README for: {repo}")
                return repo, "Success", None
            else:
                # Failure message
                print(f"README.md not found in the repository: {repo}")
                return repo, "Failed", "README.md not found in the repository"
        except subprocess.CalledProcessError as e:
            # Error message for cloning
            print(f"Error cloning repository: {repo}")
            return repo, "Failed", f"Error cloning repository: {str(e)}"
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                subprocess.run(["rm", "-rf", temp_dir], check=True)
    else:
        # Failure message
        print(
            f"Failed to download README for {repo}. Status code: {response.status_code}")
        return repo, "Failed", f"HTTP Error: {response.status_code}"


def combine_readme_files(output_folder, combined_filename):
    """
    Combine all downloaded README files into a single file with a table of contents.

    Args:
    output_folder (str): The folder containing the downloaded README files.
    combined_filename (str): The name of the combined file to be created.

    Returns:
    str: Path to the created combined file.
    """
    readme_files = [f for f in os.listdir(output_folder) if f.endswith(
        '.md') and f != 'download_report.txt']

    combined_content = "# Combined README.md files\n\n## Table of Contents\n"

    # Create table of contents
    for readme in readme_files:
        repo_name = readme[:-3]  # Remove .md extension
        anchor = re.sub(r'[^a-z0-9]+', '-', repo_name.lower())
        combined_content += f"- [{repo_name}](#{anchor})\n"

    combined_content += "\n"

    # Add content of each README file
    for readme in readme_files:
        repo_name = readme[:-3]  # Remove .md extension
        combined_content += f"## {repo_name}\n"

        with open(os.path.join(output_folder, readme), 'r', encoding='utf-8') as file:
            content = file.read()
            combined_content += f"```markdown\n{content}\n```\n\n"

    # Write combined content to file
    combined_file_path = os.path.join(output_folder, combined_filename)
    with open(combined_file_path, 'w', encoding='utf-8') as file:
        file.write(combined_content)

    return combined_file_path


def main():
    """
    Main function to orchestrate the README downloading process.
    """
    file_path, output_folder = get_input_params()

    print(f"Input file: {file_path}")
    print(f"Output folder: {output_folder}")

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read URLs from the file
    with open(file_path, "r") as file:
        urls = file.read().splitlines()

    total_urls = len(urls)
    successful = 0
    failed = 0
    results = []

    print(f"Found {total_urls} URLs to process.")

    # Download README for each URL
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing URL {i}/{total_urls}")
        repo, status, error = download_readme(url.strip(), output_folder)
        if status == "Success":
            successful += 1
        else:
            failed += 1
        results.append((repo, url, status, error))

    # Generate report
    report = f"""Bulk GitHub README Downloader
URLs: {total_urls}
Downloaded: {successful}
Failed: {failed}

"""
    for repo, url, status, error in results:
        if repo:
            report += f"{repo}.md from {url} - {status}"
            if error:
                report += f" with Error: {error}"
            report += "\n"
        else:
            report += f"Invalid URL: {url}\n"

    # Write report to file
    report_path = os.path.join(output_folder, "download_report.txt")
    with open(report_path, "w") as report_file:
        report_file.write(report)

    print(f"\nDownload complete. Report saved to {report_path}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")

    # Ask user if they want to combine README files
    combine_files = input(
        "\nDo you want to combine all README files into one? (yes/no): ").lower().strip()
    if combine_files in ['yes', 'y']:
        combined_filename = input(
            "Enter the name for the combined file (e.g., combined_readmes.md): ").strip()
        if not combined_filename.endswith('.md'):
            combined_filename += '.md'
        combined_file_path = combine_readme_files(
            output_folder, combined_filename)
        print(f"Combined README file created at: {combined_file_path}")


if __name__ == "__main__":
    main()
