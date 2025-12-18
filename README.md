# WorldMentalHealthAnalysis

From VPN/HE-Arc network : [visu.utorque.ch](http://visu.utorque.ch)

## Data downloading

The following data files should be present in the data folder:
- mental-illness.csv
- unemployment.csv
- human-freedom-index.csv
- alcohol-consumption.csv
- gender-inequality-index.csv

Otherwise there are available at the following urls:
- https://www.kaggle.com/datasets/imtkaggleteam/mental-health
- https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS
- https://www.cato.org/human-freedom-index/2024
- https://ourworldindata.org/grapher/total-alcohol-consumption-per-capita-litres-of-pure-alcohol
- https://ourworldindata.org/grapher/gender-inequality-index-from-the-human-development-report

*Please make sure the filenames are consistents*

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
