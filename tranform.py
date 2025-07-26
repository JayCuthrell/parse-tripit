import argparse
import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta

import icalendar
import pytz
import requests

# --- Configuration ---
# Set up basic logging. We'll use this for final status messages.
# The spinner will handle intermediate "in-progress" messages.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- Fun Animation Class ---
class Spinner:
    """A context manager to display a spinner animation in the terminal."""

    def __init__(self, message="Working...", delay=0.1):
        """
        Initializes the Spinner.

        Args:
            message (str): The message to display next to the spinner.
            delay (float): The speed of the animation.
        """
        self.spinner = threading.Thread(target=self._spin)
        self.message = message
        self.delay = delay
        self.running = False
        # Get the current cursor visibility setting to restore it later
        self._cursor_visible = not os.system('tput civis') == 0

    def _spin(self):
        """The target function for the animation thread."""
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Braille pattern spinner
        while self.running:
            for char in spinner_chars:
                # Use \r (carriage return) to move the cursor to the beginning of the line
                sys.stdout.write(f"\r\033[94m{char}\033[0m {self.message}")
                sys.stdout.flush()
                time.sleep(self.delay)
                if not self.running:
                    break

    def start(self):
        """Starts the spinner animation."""
        self.running = True
        # Hide the cursor for a cleaner look
        os.system('tput civis')
        self.spinner.start()

    def stop(self):
        """Stops the spinner animation and cleans up the line."""
        self.running = False
        self.spinner.join()
        # Clear the line by writing spaces over it
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()
        # Restore cursor visibility
        if self._cursor_visible:
            os.system('tput cnorm')

    def __enter__(self):
        """Starts the spinner when entering the 'with' block."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stops the spinner when exiting the 'with' block."""
        self.stop()


# --- Core Transformation Logic ---
class CalendarTransformer:
    # ... (This class remains unchanged from the previous version) ...
    """
    Transforms iCalendar content for better compatibility with Outlook 365.
    The primary transformation is to ensure all datetime values are in UTC.
    """

    def __init__(self):
        """Initializes the transformer."""
        self.logger = logging.getLogger(__name__)

    def _normalize_datetime(self, dt):
        """
        Converts a datetime object to UTC to ensure compatibility.
        Args:
            dt: A datetime object, which may or may not have timezone information.
        Returns:
            A timezone-aware datetime object in UTC.
        """
        if isinstance(dt, datetime):
            if dt.tzinfo is None:
                return pytz.UTC.localize(dt)
            return dt.astimezone(pytz.UTC)
        return dt

    def _transform_event(self, original_event):
        """
        Transforms an individual calendar event.
        Args:
            original_event: The original event component from the icalendar library.
        Returns:
            A new, transformed event component.
        """
        event = icalendar.Event()
        event.add('summary', original_event.get('summary', 'Untitled Event'))
        event.add('description', original_event.get('description', ''))
        event.add('location', original_event.get('location', ''))
        event.add('uid', original_event.get('uid'))
        dtstart = original_event.get('dtstart')
        if dtstart:
            start_dt = self._normalize_datetime(dtstart.dt)
            event.add('dtstart', start_dt)
            dtend = original_event.get('dtend')
            if dtend:
                end_dt = self._normalize_datetime(dtend.dt)
            else:
                end_dt = start_dt + timedelta(hours=1)
            event.add('dtend', end_dt)
        for prop in ['created', 'dtstamp', 'last-modified', 'sequence', 'status', 'transp']:
            if prop in original_event:
                event.add(prop, original_event[prop])
        return event

    def transform_for_outlook(self, ics_content):
        """
        Parses and transforms the entire iCalendar string.
        Args:
            ics_content: A string containing the raw iCalendar data.
        Returns:
            A string containing the transformed iCalendar data.
        """
        try:
            calendar = icalendar.Calendar.from_ical(ics_content)
            new_calendar = icalendar.Calendar()
            new_calendar.add('prodid', '-//Calendar Transformation Script//EN')
            new_calendar.add('version', '2.0')
            for component in calendar.walk():
                if component.name == "VEVENT":
                    transformed_event = self._transform_event(component)
                    if transformed_event:
                        new_calendar.add_component(transformed_event)
            return new_calendar.to_ical().decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed during calendar transformation: {e}")
            raise


# --- Main Execution ---
def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Fetch a TripIt iCalendar URL, transform it for Outlook 365, and save it to a file."
    )
    parser.add_argument("tripit_url", help="The full legacy iCalendar URL from TripIt.")
    parser.add_argument(
        "-o", "--output",
        dest="output_path",
        default="correct.ics",
        help="The path to save the final .ics file. Defaults to 'correct.ics'."
    )
    args = parser.parse_args()
    tripit_url = args.tripit_url
    output_filename = args.output_path

    try:
        # 1. Fetch the calendar data with a spinner animation.
        response = None
        with Spinner(f"Fetching calendar from TripIt..."):
            headers = {'User-Agent': 'Python-Calendar-Transformer/1.0'}
            response = requests.get(tripit_url, timeout=30, headers=headers)
        
        response.raise_for_status()
        logging.info("Successfully fetched calendar data.")

        # 2. Transform the calendar with a spinner animation.
        transformer = CalendarTransformer()
        transformed_content = None
        with Spinner("Transforming calendar for Outlook compatibility..."):
            transformed_content = transformer.transform_for_outlook(response.content)
        logging.info("Transformation complete.")

        # 3. Save the new calendar to a file.
        output_dir = os.path.dirname(output_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(transformed_content)
        logging.info(f"Successfully saved transformed calendar to {output_filename}")

    except requests.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
