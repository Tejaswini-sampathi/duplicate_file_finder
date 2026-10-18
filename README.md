
# Duplicate File Finder and Organizer

A Python application that identifies duplicate files and helps organize files into folders based on their file types. It provides filtering options, numbered duplicate groups, and CSV export for easy analysis.

## Features

- **Duplicate Detection:** Uses SHA-256 hashing to identify files with identical content.
- **File Type Filter:** Scan specific file types such as PDF, TXT, JPG, and PNG.
- **Minimum File Size Filter:** Ignore files smaller than a specified size.
- **Numbered Duplicate Groups:** Display duplicate files grouped with unique group numbers.
- **CSV Export:** Export duplicate findings to a CSV file for viewing in spreadsheet applications.
- **File Organization:** Create copies of files organized by extension.
- **Undo Option:** Remove copies created by the application, provided they have not been modified.
- **Original File Protection:** Original files are retained during organization.

## Technologies Used

- Python
- SHA-256 hashing
- pathlib
- CSV
- File handling
- Git and GitHub

## Project Structure

```text
01_duplicate_file_finder/
├── app.py
├── common.py
├── data.json
├── .gitignore
└── README.md
```

The `data.json` file stores the scan plan, duplicate findings, and details needed for the undo operation. It may be created automatically by the application's Store class.

## Requirements

- Python 3.10 or later recommended
- The `common.py` helper module included with this project

The application uses Python standard-library modules, so no additional third-party packages are required by `app.py` itself.

## How to Run

1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Ensure `app.py` and `common.py` are in the same folder.
4. Run the application using:

```bash
python app.py
```

## How to Use

1. Enter the folder path you want to scan.
2. Optionally enter file extensions separated by commas, such as `pdf,txt`.
3. Enter the minimum file size in bytes. Use `0` to include files of any size.
4. Scan the folder and review the numbered duplicate groups.
5. Export the findings as a CSV file if needed.
6. Preview the organization plan before creating organized copies.
7. Use the undo option to remove copies created by the application when safe.

## Safety Notes

- Test the application using a folder containing sample files first.
- The organization feature creates copies rather than moving or deleting originals.
- The undo operation checks whether created copies have changed before removing them.
- Review the folder path and proposed destinations before creating copies.

## Future Improvements

- Add a graphical dashboard for scan statistics.
- Display file sizes in KB and MB.
- Add progress indicators for large folders.
- Improve CSV reports with duplicate-group summaries.

## Author

Tejaswini Sampathi

---

*Built as a hands-on Python practice project.*
