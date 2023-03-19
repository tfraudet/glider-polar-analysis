# Glider speed polars curve analysis tool

The speed polar curve shows the sink rate of a glider against its airspeed. Polar curves are used to calculate the glider's minimum sink rate, best lift/drag ratio (L/D) and flight speed.

This project provides various notebook to compute/analysis glider polars.

![glider flight polar ][def]

## Requirements

* Python 3.10 or higher

## How to run this app locally with python 3

We suggest you to create a virtual environment for running this app with Python 3. Clone this repository and open your terminal/command prompt in the root folder.

```bash
git clone https://github.com/tfraudet/glider-polar-analysis.git
cd ./glider-polar-analysis
python3 -m virtualenv venv
```

On Unix systems

```bash
source venv/bin/activate
```

On Window systems

```bash
venv\scripts\activate
```

Install all required packages by running:

```bash
pip install -r requirements.txt
```

To run the app locally:

```bash
python app.py
````

And open browser at [localhost:8050](http://127.0.0.1:8050/)

## How to run this app locally using docker (pull image)

* docker pull wasa000/waves
* docker run -p [your port]:8050 wasa000/waves

## How to run this app locally using docker (build image)

* [good example docker](https://github.com/danny-baker/atlas)
* [another example here](https://github.com/SINTEF-9012/SINDIT)
* [example running gunicorn](https://github.com/Sentdex/socialsentiment/)

## Some usefull links

* [Glider polar from xp-soaring](https://xp-soaring.github.io/dev/polars/polar.html)
* [Wikipedia](https://en.wikipedia.org/wiki/Drag_curve)
* [How to Execute Jupyter Notebooks from GitHub](https://soshnikov.com/education/how-to-execute-notebooks-from-github/)

[def]: ./polars-analysis.png
