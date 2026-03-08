import requests
from icalendar import Calendar
from datetime import datetime, date, timedelta
import sys
import csv
import os
from dotenv import load_dotenv

def calculate_days_remaining(event_start, subtract_days=0):
    today = date.today()
    adjusted_today = today + timedelta(days=subtract_days)
    if isinstance(event_start, datetime):
        start_date = event_start.date()
    else:
        start_date = event_start
    time_difference = start_date - adjusted_today
    return time_difference.days

def format_date_asana(dt_object):
    if isinstance(dt_object, datetime) or isinstance(dt_object, date):
        return dt_object.strftime("%Y-%m-%d")
    return ""

def parse_ical_to_asana_csv(ical_url, report_due_offset=0):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        asana_csv_data = [["Task ID", "Created At", "Completed At", "Last Modified", "Name", "Section/Column", "Assignee", "Assignee Email", "Start Date", "Due Date", "Tags", "Notes", "Projects", "Parent task", "Blocked By (Dependencies)", "Blocking (Dependencies)", "Responsible (Department)", "Expected Cost", "Complete By"]] # Asana CSV Header

        for event in cal.walk('VEVENT'):
            name = event.get('SUMMARY', '').replace("PLACEHOLDER ONLY:", "").strip()
            start = event.get('DTSTART').dt
            end = event.get('DTEND').dt
            location = event.get('LOCATION', '')
            url = event.get('URL', '')

            start_date_str = format_date_asana(start)
            due_date_str = format_date_asana(end)
            notes = location
            if url:
                if notes:
                    notes += f" | {url}"
                else:
                    notes = url

            days_remaining = calculate_days_remaining(start, report_due_offset)
            if days_remaining >= 0:
                asana_csv_data.append([
                    "",  # Task ID
                    format_date_asana(datetime.now().date()),  # Created At (using current date)
                    "",  # Completed At
                    format_date_asana(datetime.now().date()),  # Last Modified (using current date)
                    name,  # Name
                    "",  # Section/Column
                    "",  # Assignee
                    "",  # Assignee Email
                    start_date_str,  # Start Date
                    due_date_str,  # Due Date
                    "",  # Tags
                    notes,  # Notes
                    "",  # Projects
                    "",  # Parent task
                    "",  # Blocked By (Dependencies)
                    "",  # Blocking (Dependencies)
                    "",  # Responsible (Department)
                    "",  # Expected Cost
                    start_date_str  # Complete By (using Due Date)
                ])

        return asana_csv_data

    except requests.exceptions.RequestException as e:
        return f"Error fetching iCal data: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def parse_ical_to_csv(ical_url, report_due_offset=0):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        csv_data = [["Task", "Due Date", "Notes"]]  # Basic CSV Header

        for event in cal.walk('VEVENT'):
            name = event.get('SUMMARY', '').replace("PLACEHOLDER ONLY:", "").strip()
            start = event.get('DTSTART').dt
            end = event.get('DTEND').dt
            location = event.get('LOCATION', '')
            url = event.get('URL', '')

            due_date_str = format_date_asana(end)
            notes = location
            if url:
                if notes:
                    notes += f" | {url}"
                else:
                    notes = url

            days_remaining = calculate_days_remaining(start, report_due_offset)
            if days_remaining >= 0:
                csv_data.append([
                    name,  # Task
                    due_date_str,  # Due Date
                    notes  # Notes
                ])

        return csv_data

    except requests.exceptions.RequestException as e:
        return f"Error fetching iCal data: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def calculate_days_remaining_general(event_start, subtract_days=0):
    today = date.today()
    adjusted_today = today + timedelta(days=subtract_days)
    if isinstance(event_start, datetime):
        start_date = event_start.date()
    else:
        start_date = event_start
    time_difference = start_date - adjusted_today
    return time_difference.days

def format_date_general(dt_object):
    if isinstance(dt_object, datetime) or isinstance(dt_object, date):
        return dt_object.strftime("%B %d")
    return "Unknown"

def format_date_with_year_general(dt_object):
    if isinstance(dt_object, datetime) or isinstance(dt_object, date):
        return dt_object.strftime("%B %d, %Y")
    return "Unknown"

def format_summary_countdown_general(event, plain_text=False, show_dates=False, report_due_offset=0):
    summary = event.get('SUMMARY', '').replace("PLACEHOLDER ONLY:", "").strip()
    location = event.get('LOCATION', 'No Location Specified')
    start = event.get('DTSTART').dt
    end = event.get('DTEND').dt

    start_date_str = format_date_general(start)
    end_date_str = format_date_with_year_general(end)

    if isinstance(start, datetime) or isinstance(start, date):
        days_remaining = calculate_days_remaining_general(start, report_due_offset)
        date_info = f" ({start_date_str} to {end_date_str})" if show_dates else ""
        if days_remaining >= 0:
            if plain_text:
                return f"- {summary} - {location} (in {days_remaining} days){date_info}\n"
            else:
                return f"- **{summary}** - {location} (in {days_remaining} days){date_info}\n"
        else:
            return None
    else:
        if plain_text:
            return f"- {summary} - {location} (Date/Time Unknown)\n"
        else:
            return f"- **{summary}** - {location} (Date/Time Unknown)\n"

def parse_ical_to_summary_countdown_general(ical_url, plain_text=False, show_dates=False, report_due_offset=0):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        heading = "Upcoming Events:\n\n" if plain_text else "### Upcoming Events:\n\n"
        summary_output = heading
        upcoming_events = False

        for event in cal.walk('VEVENT'):
            formatted_summary = format_summary_countdown_general(event, plain_text, show_dates, report_due_offset)
            if formatted_summary:
                summary_output += formatted_summary
                upcoming_events = True

        if not upcoming_events:
            summary_output += "No upcoming events found.\n"

        return summary_output

    except requests.exceptions.RequestException as e:
        return f"Error fetching iCal data: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    load_dotenv()
    ical_url = os.getenv('TRIPIT_ICAL', '')
    plain_text_output = False
    show_dates_output = False
    report_due_offset = 0
    output_format = "text"

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--plain":
            plain_text_output = True
        elif arg == "--dates":
            show_dates_output = True
        elif arg == "--report_due" and i + 1 < len(sys.argv):
            try:
                report_due_offset = int(sys.argv[i + 1])
                i += 1
            except ValueError:
                print("Error: --report_due argument must be an integer.")
                sys.exit(1)
        elif arg == "--csv":
            output_format = "csv"
        elif arg == "--asana_csv":
            output_format = "asana_csv"
        elif not arg.startswith("--"):
            # Assume it's the ical_url
            ical_url = arg
        else:
            print(f"Unknown option: {arg}")
            sys.exit(1)
        i += 1

    if not ical_url:
        print("Usage: python your_script_name.py [ical_url] [options]")
        print("\nIf no ical_url is provided, it will use the TRIPIT_ICAL environment variable from .env file.")
        print("\nOptions:")
        print("  ical_url           The URL of the .ics file to process (optional if set in .env).")
        print("  --plain             Output in plain text format (no Markdown).")
        print("  --dates             Include the start and end dates in the output.")
        print("  --report_due <days> Subtract <days> from the current date for countdown.")
        print("  --csv               Output in basic CSV format (Task, Due Date, Notes).")
        print("  --asana_csv         Output in CSV format for Asana import.")
        sys.exit(1)

    if ical_url:
        if output_format == "csv":
            csv_data = parse_ical_to_csv(ical_url, report_due_offset)
            if isinstance(csv_data, str):
                print(csv_data)
            else:
                writer = csv.writer(sys.stdout)
                writer.writerows(csv_data)
        elif output_format == "asana_csv":
            asana_csv_data = parse_ical_to_asana_csv(ical_url, report_due_offset)
            if isinstance(asana_csv_data, str):
                print(asana_csv_data)
            else:
                writer = csv.writer(sys.stdout)
                writer.writerows(asana_csv_data)
        else:
            markdown_output = parse_ical_to_summary_countdown_general(ical_url, plain_text_output, show_dates_output, report_due_offset)
            print(markdown_output)
