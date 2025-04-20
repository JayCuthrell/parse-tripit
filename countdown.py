import requests
from icalendar import Calendar
from datetime import datetime, date, timedelta
import sys
import csv

def calculate_days_remaining(event_start, subtract_days=0):
    today = date.today()
    adjusted_today = today + timedelta(days=subtract_days)
    if isinstance(event_start, datetime):
        start_date = event_start.date()
    else:
        start_date = event_start
    time_difference = start_date - adjusted_today
    return time_difference.days

def format_date_csv(dt_object):
    if isinstance(dt_object, datetime) or isinstance(dt_object, date):
        return dt_object.strftime("%Y-%m-%d")
    return ""

def parse_ical_to_csv(ical_url, report_due_offset=0):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        csv_data = [["Task", "Due Date", "Notes"]] # CSV Header

        for event in cal.walk('VEVENT'):
            summary = event.get('SUMMARY', '').replace("PLACEHOLDER ONLY:", "").strip()
            end = event.get('DTEND').dt
            location = event.get('LOCATION', '')
            url = event.get('URL', '')

            due_date_str = format_date_csv(end)

            notes = location
            if url:
                if notes:
                    notes += f" | {url}"
                else:
                    notes = url

            start = event.get('DTSTART').dt
            days_remaining = calculate_days_remaining(start, report_due_offset)
            if days_remaining >= 0:
                csv_data.append([summary, due_date_str, notes])

        return csv_data

    except requests.exceptions.RequestException as e:
        return f"Error fetching iCal data: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def parse_ical_to_summary_countdown(ical_url, plain_text=False, show_dates=False, report_due_offset=0):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        heading = "Upcoming Events:\n\n" if plain_text else "### Upcoming Events:\n\n"
        summary_output = heading
        upcoming_events = False

        def format_date_local(dt_object):
            if isinstance(dt_object, datetime) or isinstance(dt_object, date):
                return dt_object.strftime("%B %d")
            return "Unknown"

        def format_date_with_year_local(dt_object):
            if isinstance(dt_object, datetime) or isinstance(dt_object, date):
                return dt_object.strftime("%B %d, %Y")
            return "Unknown"

        def format_summary_countdown_local(event, plain_text=False, show_dates=False, report_due_offset=0):
            summary = event.get('SUMMARY', '').replace("PLACEHOLDER ONLY:", "").strip()
            location = event.get('LOCATION', 'No Location Specified')
            start = event.get('DTSTART').dt
            end = event.get('DTEND').dt

            start_date_str = format_date_local(start)
            end_date_str = format_date_with_year_local(end)

            if isinstance(start, datetime) or isinstance(start, date):
                days_remaining = calculate_days_remaining(start, report_due_offset)
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

        for event in cal.walk('VEVENT'):
            formatted_summary = format_summary_countdown_local(event, plain_text, show_dates, report_due_offset)
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
    ical_url = ""
    plain_text_output = False
    show_dates_output = False
    report_due_offset = 0
    output_format = "text"

    if len(sys.argv) > 1:
        ical_url = sys.argv[1]
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--plain":
                plain_text_output = True
            elif sys.argv[i] == "--dates":
                show_dates_output = True
            elif sys.argv[i] == "--report_due" and i + 1 < len(sys.argv):
                try:
                    report_due_offset = int(sys.argv[i + 1])
                    i += 1
                except ValueError:
                    print("Error: --report_due argument must be an integer.")
            elif sys.argv[i] == "--csv":
                output_format = "csv"
            i += 1
    else:
        print("Usage: python your_script_name.py <ical_url> [options]")
        print("\nOptions:")
        print("  <ical_url>          The URL of the .ics file to process (required).")
        print("  --plain             Output in plain text format (no Markdown).")
        print("  --dates             Include the start and end dates in the output.")
        print("  --report_due <days> Subtract <days> from the current date for countdown.")
        print("  --csv               Output in CSV format for importing into Asana.")
        sys.exit(1)

    if ical_url:
        if output_format == "csv":
            csv_data = parse_ical_to_csv(ical_url, report_due_offset)
            if isinstance(csv_data, str):
                print(csv_data)
            else:
                writer = csv.writer(sys.stdout)
                writer.writerows(csv_data)
        else:
            markdown_output = parse_ical_to_summary_countdown(ical_url, plain_text_output, show_dates_output, report_due_offset)
            print(markdown_output)
