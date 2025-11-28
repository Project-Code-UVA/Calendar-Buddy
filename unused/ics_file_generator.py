from ics import Calendar, Event
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path so we can import data_extractor
sys.path.insert(0, str(Path(__file__).resolve().parent))

def generate_ics_from_file(file_name="complicated_sample.txt", output_file="events.ics"):
    """
    Generate an ICS calendar file from a text file containing events and dates.
    
    Args:
        file_name: Input text file with event descriptions (e.g., "complicated_sample.txt")
        output_file: Output ICS file name (default: "events.ics")
    
    Returns:
        Path to the generated ICS file
    """
    import datefinder
    
    # Look for the input file in the parent directory (Calendar-Buddy folder)
    # since data_extractor is in the unused folder
    parent_dir = Path(__file__).resolve().parent.parent
    file_path = parent_dir / file_name
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return None
    
    parsed_events = []
    
    # Parse dates from the input file directly
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parsed_date = list(datefinder.find_dates(line))
            if parsed_date:
                parsed_events.append((line, parsed_date))
                print(f"✓ Found event: {line}")
    
    if not parsed_events:
        print(f"No events found in {file_name}")
        return None
    
    # Create calendar
    calendar = Calendar()
    calendar.prodid = "-//Calendar Buddy//EN"
    calendar.version = "2.0"
    
    # Add each event to the calendar
    event_count = 0
    for event_text, date_objects in parsed_events:
        if not date_objects:
            continue
        
        # Create event with the first parsed date
        event = Event()
        event.name = event_text[:255]  # ICS has name length limits
        event.begin = date_objects[0]  # Use first parsed datetime as begin date
        
        # Set end time based on available data
        if len(date_objects) > 1 and date_objects[1] > date_objects[0]:
            # If multiple dates found and end is after begin, use as end date
            event.end = date_objects[1]
        else:
            # Default: 1 hour duration (using arrow's shift method)
            try:
                event.end = event.begin.shift(hours=1)
            except:
                event.end = event.begin.shift(days=1)
        
        calendar.events.add(event)
        event_count += 1
        print(f"  → Added to calendar: {event.begin}")
    
    # Write to ICS file in the same directory as this script
    output_path = Path(__file__).resolve().parent / output_file
    with open(output_path, "w") as f:
        f.writelines(calendar)
    
    print(f"✓ Successfully created {output_file} with {event_count} events at {output_path}\n")
    return output_path


def main():
    """Test ICS file generation on sample files"""
    print("=" * 70)
    print("ICS File Generator - Test")
    print("=" * 70)
    
    # Generate ICS from basic sample
    print("\n--- Processing basic_sample.txt ---")
    basic_ics = generate_ics_from_file("basic_sample.txt", "basic_events.ics")
    
    # Generate ICS from complicated sample
    print("\n--- Processing complicated_sample.txt ---")
    complicated_ics = generate_ics_from_file("complicated_sample.txt", "complicated_events.ics")
    
    print("\n" + "=" * 70)
    print("ICS file generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
