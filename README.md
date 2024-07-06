![10a25dab-de92-42ec-a5dc-12aea06a8cb4](https://github.com/europybots2024/vendeeglobe/assets/39047984/9032ef05-07c8-4d13-807c-bad82e0f89f0)

# EuroPython 2024 video game tournament

## What is the tournament about?

We have created a video game that is designed to be played by a small python program, rather than a human.
Conference attendees can participate in a tournament where they (either alone or in a team) each submit a bot that will play the game, and at the end of the conference, we will have a tournament session where everyone can come and watch our strange creations play against each other (either brilliantly or it may all go wrong!).

## How to participate?

- Create a repository for your bot from [the template](https://github.com/new?owner=europybots2024&template_name=template_bot&template_owner=europybots2024).
- Register your team: fill in the form at https://forms.gle/TosuLTY1zo59FNSz5 (no limit on the number of participants)
- Read the game rules below and start working on your bot
- Ask questions on the Discord forum `pybot-game-tournament`
- Once your bot is ready, make sure you have merged all your changes into the `main` branch of the repo you created
- Deadline is 12:30 on Friday July 12th
- Tournament will be 13:00 - 14:30 on Friday July 12th in the Open Space area

## TL;DR

1. Create a repository for your bot from [the template](https://github.com/new?owner=europybots2024&template_name=template_bot&template_owner=europybots2024).

2. Get started with:

### conda

```
conda create -n <NAME> -c conda-forge python=3.10.*
conda activate <NAME>
git clone https://github.com/europybots2024/vendeeglobe.git
git clone https://github.com/<USERNAME>/<MYBOTNAME>.git
cd vendeeglobe/
python -m pip install -e .
cd run/
ln -s ../../<MYBOTNAME> .
python play.py
```

### venv

```
git clone https://github.com/europybots2024/vendeeglobe.git
git clone https://github.com/<USERNAME>/<MYBOTNAME>.git
cd vendeeglobe/
python -m venv .<NAME>
source .<NAME>/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cd run/
ln -s ../../<MYBOTNAME> .
python play.py
```

## The game: Vendeeglobe

Around the world sailing race

Preview

![Screenshot at 2023-11-14 17-34-45](https://github.com/europybots2024/vendeeglobe/assets/39047984/a2b029a4-325d-42bc-8e89-6b7783765c98)



## Goal & general rules

- Sail around the world as fast as possible
- Start from les Sables-d’Olonne in France
- There are two mandatory checkpoints
- Each round has a time limit of 8 minutes (=80 days)
- The tournament on the final day consist of 8 rounds, where the scores from each round are summed

## Mandatory checkpoints

- A checkpoint is a location on the globe (latitude+longitude) with a radius
- If you sail within the checkpoint radius, the checkpoint has been reached
- The first mandatory checkpoint is located in the middle of the pacific ocean and has a radius of 2000 km
- The second mandatory checkpoint is located in the middle of the indian ocean and has a radius of 1200 km

![Screenshot at 2024-06-05 21-24-26](https://github.com/europybots2024/vendeeglobe/assets/39047984/5a34e09d-91c4-4f46-9e96-183cbf0735bd)

## Weather

- Only the wind is a factor (there are no ocean currents)
- Wind is randomly generated for every game, and stays static for 12 hours during a round

## Sailing

- The angle between ship and wind affects ship speed

<img src="https://github.com/europybots2024/vendeeglobe/assets/39047984/89de9e74-7296-465c-8814-c61de2d36214" width="500" />

- With a wind force of 1, the ship will go as fast as the wind
- Ships will get stuck when reaching land (obviously!), but will not crash: you can turn around
- Ships cannot crash into each other (they behave like ghosts)

## Scoring

- Points from 1st to last place decay exponentially (and depend on the number of players)

<img src="https://github.com/europybots2024/vendeeglobe/assets/39047984/6b7de608-71a7-4bd0-8fa5-0da02cf035d3" width="500" />

- Back home with 2 checkpoints is best (or closest to home)
- Then closest to 2nd checkpoint, then closest to 1st checkpoint

## Timing

Here is a table that gives the correspondance between real/user time duration and the amount of time that goes by in the game.

| Real/User time | Time in game |
| --- | --- |
| 8 mins   | 80 days  |
| 1 min    | 10 days  |
| 6 sec    |  1 day   |
| 1 sec    |  4 hours |
| 0.25 sec |  1 hour  |

## The control center - the Bot

- To play the game, you will have to create a Python program.
- It should contain a class named `Bot` and that class should have a method named `run`.
- Every time step, the `run` method will be called, and it will be inside that function that you should control your ship.
- You are provided with a `bot.py` in the `template_bot` repository to give you an example.

Look at the comments in `bot.py` for details on what information is available to you at every time step and how to control your vessel.

## The weather forecast

- The weather `forecast` is one of the arguments the `run` function will receive.
- It is a method that lets you access the wind data for the 5 days to come (for the entire globe).
- The accuracy of the forecast decreases the further in time you look: the figure below shows the same weather data (value of the horizontal `u` wind component) 1 day in the future, and 5 days in the future

![Screenshot at 2024-06-06 22-26-09](https://github.com/europybots2024/vendeeglobe/assets/39047984/f5f20fbb-385c-49ff-bc59-2753f04af0d4)
 
- It is a callable which can get the wind horizontal (`u`) and vertical (`v`) vector components for any given location(s) in space (latitude and longitude) and time (from 0 to 5 days).
```Py
u, v = forecast(latitudes, longitudes, times)
```

## The world map

- The `world_map` is another of the arguments received by your bot's `run` function.
- It is also a callable which provides the world map values (1 = sea, 0 = land) for any given latitude(s) and longitude(s):
```Py
map_values = world_map(latitudes, longitudes)
```

## Instructions for the ship

The bot will control the ship by returning a set of instructions that will then be read and applied by the game engine.
You initialize a `Instructions` object, and then set one of the following attributes:

- `Location`: a latitude/longitude to go to (using the shortest straight-line path on the surface of the globe, ignoring land mass)
- `Heading`:	heading for the ship in degrees (East is 0, North is 90, West is 180, South is 270)
- `Vector`: vector for the ship (instead of heading)
- `Left`:	turn left X degrees
- `Right`:	turn right X degrees
- `sail`: you can also control the ship's speed by choosing how much sail to deploy (a number between 0 and 1)

## Optimizing development

There are 4 ways you can speed up your development.

### 1. Course preview

You can show a preview of your course using a `course_preview`.
This is an argument of the `play` function.
A list of checkpoints should be supplied:
```Py
vendeeglobe.play(...,
                 course_preview=[
                     Checkpoint(latitude=43.797109, longitude=-11.264905, radius=50),
                     Checkpoint(longitude=-29.908577, latitude=17.999811, radius=50),
                     ...
                 ])
```
Note that, while it tries hard to be, the course preview may not be 100% accurate.

### 2. Change your starting location

You can supply any starting location on the globe, if you want to e.g. test the middle or end part of your course.
```Py
vendeeglobe.play(...,
                 start=vendeeglobe.Location(longitude=-68.004373, latitude=18.180470)
                 )
```
If you are using a course of checkpoints (as in the `template_bot`), remember to set all of the checkpoints that come before `start` to `.reached = True`!

### 3. Use the high-contrast mode

- Sometimes, it can be a little unclear whether a small island or shallow water is an actual obstacle on the map or not.
- You can use the high-contrast mode to view a two-color map which will clearly differentiate land and sea.
- This can be done by either using the `high_contrast=True` argument, or using the in-game checkbox in the left side bar.

![Screenshot at 2024-06-06 23-00-06](https://github.com/europybots2024/vendeeglobe/assets/39047984/99e20350-0a92-4282-bb66-aa26c2bdc6b7)

### 4. Speed up time

You can speed up time using e.g. `speedup=2.0` as an argument to `vendeeglobe.play`, but note that **this one is a little buggy!**

Because the ships advance using a time step mechanism, this may cause you to overshoot a checkpoint (or oscillate around it),
or you might crash into land if you're navigating close to a coast line.

## Tips and recommendations

- It is strongly recommended to start by just plotting a course (Google Maps is your friend!).
- Explore the map in the game: **some parts have deliberately been edited to allow different routes to be taken**.
- Unlike in real life, the wind direction is predominantly from East to West.
- Once you have a course that works, you can then start thinking more about the wind.

## Acknowledgements

- The game was developed by @nvaytet and @gergely-elias.
- The game was inspired by the [Virtual Regatta](https://www.virtualregatta.com/en/) game and [this cool visualization](https://earth.nullschool.net/) of wind conditions on Earth.
- The cover image was created using https://deepai.org/machine-learning-model/
- We thank the developers at the European Spallation Source's Data Management and Software Center for testing the game!
