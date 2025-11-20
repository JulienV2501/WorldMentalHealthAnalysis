# WorldMentalHealthAnalysis

## Data downloading

To run the application, it is necessary to download the data locally and store it in a “data” folder at the root of the project.

Download and save the following files:

- 1- mental-illnesses-prevalence.csv : https://www.kaggle.com/datasets/imtkaggleteam/mental-health
- API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_130165.csv : https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS
- human-freedom-index-data-2024.csv : https://www.cato.org/human-freedom-index/2024
- total-alcohol-consumption-per-capita-litres-of-pure-alcohol.csv : https://ourworldindata.org/grapher/total-alcohol-consumption-per-capita-litres-of-pure-alcohol
- gender-inequality-index-from-the-human-development-report.csv : https://ourworldindata.org/grapher/gender-inequality-index-from-the-human-development-report

Then, save them as follows in the /data folder

- 1- mental-illnesses-prevalence.csv --> **mental-illness.csv**
- API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_130165.csv --> **unemployment.csv**
- human-freedom-index-data-2024.csv --> **human-freedom-index.csv**
- total-alcohol-consumption-per-capita-litres-of-pure-alcohol.csv --> **alcohol-consumption.csv**
- gender-inequality-index-from-the-human-development-report.csv --> **gender-inequality-index.csv**

## Python environment

Create python environment:

```
python -m venv venv
# or
python3 -m venv venv
```

Then activate:

```
# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

Finally, install requirements

```
pip install -r requirements.txt
```

## Run app

```
python app.py
# or
python3 app.py
```