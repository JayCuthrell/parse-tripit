# TripIt iCal Parser

A Python script to parse TripIt iCal (.ics) files and output upcoming events in various formats, including Markdown, plain text, and CSV for import into tools like Asana.

## Prerequisites

- Python 3.6 or higher
- Virtual environment (created via setup.sh)

## Setup

1. Clone or download this repository.
2. Run the setup script to create a virtual environment and install dependencies:

   ```bash
   ./setup.sh
   ```

3. Activate the virtual environment:

   ```bash
   source my_env/bin/activate
   ```

4. Create a `.env` file in the project root with your TripIt iCal URL:

   ```
   TRIPIT_ICAL=https://www.tripit.com/feed/ical/private/YOUR_PRIVATE_KEY/tripit.ics
   ```

   Replace `YOUR_PRIVATE_KEY` with your actual TripIt iCal feed key.

## Usage

```bash
python3 ./countdown.py [ical_url] [options]
```

If no `ical_url` is provided, the script will use the `TRIPIT_ICAL` environment variable from the `.env` file.

## Options

- `ical_url`: The URL of the .ics file to process (optional if set in `.env`).
- `--plain`: Output in plain text format (no Markdown).
- `--dates`: Include the start and end dates in the output.
- `--report_due <days>`: Subtract `<days>` from the current date for countdown calculations.
- `--csv`: Output in basic CSV format (Task, Due Date, Notes).
- `--asana_csv`: Output in CSV format suitable for Asana import.

## Examples

- Default Markdown output using URL from `.env`:

  ```bash
  python3 ./countdown.py
  ```

- Plain text output:

  ```bash
  python3 ./countdown.py --plain
  ```

- Include dates in output:

  ```bash
  python3 ./countdown.py --dates
  ```

- Output as basic CSV:

  ```bash
  python3 ./countdown.py --csv
  ```

- Output as Asana-compatible CSV:

  ```bash
  python3 ./countdown.py --asana_csv
  ```

- Using a custom iCal URL with options:

  ```bash
  python3 ./countdown.py https://example.com/calendar.ics --plain --dates
  ```

## Environment Variables

- `TRIPIT_ICAL`: URL of the TripIt iCal feed. If not provided as a command-line argument, this is used.

## Notes

- Events are filtered to show only upcoming events (where the start date is today or in the future, adjusted by `--report_due` if specified).
- The script handles TripIt-specific placeholders and formats event summaries accordingly.
- YMMV (Your Mileage May Vary) - This script is provided as-is and may need adjustments based on your specific iCal feed structure.
