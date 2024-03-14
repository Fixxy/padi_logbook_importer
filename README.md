# PADI Logbook Importer

This Python script allows you to import your recreational dive logs in CSV format into your PADI.com logbook.

## Installation

1. Clone or download this repository to your local machine.

```
git clone https://github.com/Fixxy/padi_logbook_importer.git
```

2. Navigate to the directory where you cloned/downloaded the repository.

```
cd padi_logbook_importer
```

3. Install the required dependencies using pip.

```
pip install -r requirements.txt
```

## Usage

To use the script, execute it from the command line with the following arguments:

- `username`: Your PADI.com username (required).
- `password`: Your PADI.com password (required).
- `file`: The path to the CSV file containing diving logs (required).
- `type`: Specifies the data format/type ("custom_csv" by default).

```bash
python run.py [-h] -u USERNAME -p PASSWORD -f FILE -t DATA_TYPE
```

Example:

```bash
python run.py [-h] -u example@example.org -p 12345 -f diving_logs.csv -t custom_csv
```

## CSV file format
- The CSV file must contain the following columns:
  - **General (required):**
    - "dive_type": Type of dive, how did you get in the water ("Boat", "Shore" or "Other");
    - "dive_title": Dive title, name of your dive;
    - "dive_location": Name of the dive location;
    - "dive_date": Date of your dive ("MM/DD/YYYY");
  - **Depth/Time (required):**
    - "max_depth": Max dive depth, how deep did you go;
    - "bottom_time": Bottom time, how long was your dive;

- The CSV file can additionally contain the following columns:
  - **Conditions (not required):**
    - "water_type": Water Type ("Salt" or "Fresh");
    - "body_of_water": Body of water, what body of water did you dive in ("Ocean", "Lake", "Quarry", "River", "Other");
    - "weather": Weather ("Sunny", "PartlyCloudy", "Cloudy", "Rainy", "Windy", "Foggy");
    - "air_temp": Air temperature;
    - "surface_water_temp": Surface temperature;
    - "bottom_water_temp": Bottom temperature;
    - "visibility": Visibility ("Average", "High", "Low");
    - "visibility_distance": Visibility distance, how far could you see;
    - "wave_condition": How were the waves ("MediumWaves", "SmallWaves", "LargeWaves", "NoWaves");
    - "current": How was the current ("NoCurrent", "SomeCurrent", "MediumCurrent", "StrongCurrent");
    - "surge": How was the surge ("SomeSurge", "MediumSurge", "BigSurge");
  - **Equipment (not required):**
    - "starting_pressure": Starting cylinder pressure;
    - "ending_pressure": Remaining cylinder pressure;
    - "suit_type": What suit did you wear ("FullSuit_5mm", "FullSuit_3mm", "FullSuit_7mm", "SemiDrySuit", "DrySuit", "Shorty")
    - "weight": The amount of weight you used;
    - "weight_type": How was the amount of weight ("Good", "Heavy", "Light");
    - "additional_equipment": Comma separated list of additional gear (Hood,Gloves,Boots);
    - "cylinder_type": What kind of cylinder did you use ("Aluminum", "Steel", "Other");
    - "cylinder_size": What was the cylinder size
    - "gas_mixture": "Enriched", "Trimix", "Rebreather", "Air"
    - "oxygen": Oxygen %
    - "nitrogen": Nitrogen %
    - "helium": Helium %
  - **Experience (not required):**
    - "feeling": How did you feel about the dive ("Good", "Amazing", "Average", "Poor");
    - "notes": Notes for the dive;
    - "buddies": Who did you go with;
    - "dive_center": What dive center did you dive with?

## Future plans

- Add support for log files from diving computers;

## Disclaimer

This script is provided as-is and without warranty. Use it responsibly and at your own risk.

## Contributing

If you encounter any issues or have suggestions for improvement, feel free to open an issue or create a pull request.
