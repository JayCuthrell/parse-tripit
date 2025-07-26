TripIt ICS parsing... YMMV

```
$ python3 ./countdown.py
Usage: python your_script_name.py <ical_url> [options]

Options:
  <ical_url>          The URL of the .ics file to process (required).
  --plain             Output in plain text format (no Markdown).
  --dates             Include the start and end dates in the output.
  --report_due <days> Subtract <days> from the current date for countdown.
  --csv               Output in CSV format for importing into Asana.
```

Also to make an ics that can be parsed by Outlook 

```
$ python3 tranform.py 
usage: tranform.py [-h] [-o OUTPUT_PATH] tripit_url
```
