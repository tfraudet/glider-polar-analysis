![GitHub](https://img.shields.io/github/license/tfraudet/glider-polar-analysis) ![GitHub last commit](https://img.shields.io/github/last-commit/tfraudet/glider-polar-analysis)

# Glider speed polar curve analysis tool

The speed polar curve shows the sink rate of a glider against its airspeed. Polar curve are used to calculate the glider's minimum sink rate, best lift/drag ratio (L/D) and flight speed. This project provides a tool to compute the flight speed for the minimum sink rate and for the best lift/drag ratio when you increased or decreased the glider's weight (adding water ballast for example)

* The first tab **Effect of wing loading** allows you select a glider polar among the one of the database and increase or decrease the glider's wing loading, see how the polar shift and what are the new speeds flight for minimum sink rate and for best L/D ratio.
* The second tab **Compare Polars** allow you to select up to 4 glider polars from the database and compare them.

![glider flight polar][main-screen]

## Requirements

* Python 3.10

## How to run this app locally with python 3

We suggest you to create a virtual environment for running this app with Python 3. Clone this repository and open your terminal/command prompt in a folder.

```bash
git clone https://github.com/tfraudet/glider-polar-analysis.git
cd ./glider-polar-analysis
python3 -m venv myenv
```

On Unix systems

```bash
source myenv/bin/activate
```

On Window systems

```bash
myenv\scripts\activate
```

Install all required packages by running:

```bash
pip3 install -r requirements.txt
```

Then run the app locally:

```bash
python3 app.py
````

You shoud see the following in the terminal

![terminal screen][dashapp-runing-terminal]

And open browser at [localhost:8050](http://127.0.0.1:8050/)

## How to run this app locally using docker (pull image)

```bash
# pull the image from Docker Hub
docker pull tfraudet/gliderpolaranalysis:0.9

# Then run the image inside a container, mapping the host’s port 8050 to the container’s port 8050
docker run -d -p 8050:8050 tfraudet/gliderpolaranalysis:0.9
````

And open browser at [localhost:8050](http://127.0.0.1:8050/)

## How to run this app locally using docker (build image)

```bash
# First build the image from dockerfile
docker build --tag gliderpolaranalysis --file './Dockerfile' .

# Then run the image inside a container, mapping the host’s port 8050 to the container’s port 8050
docker run -d -p 8050:8050 gliderpolaranalysis:latest
````

And open browser at [localhost:8050](http://127.0.0.1:8050/)

## Some usefull links

* [Glider polar from xp-soaring](https://xp-soaring.github.io/dev/polars/polar.html)
* [Wikipedia](https://en.wikipedia.org/wiki/Drag_curve)
* [How to Execute Jupyter Notebooks from GitHub](https://soshnikov.com/education/how-to-execute-notebooks-from-github/)

[main-screen]: ./polars-analysis.png
[dashapp-runing-terminal]: ./dash-app-runing.png
