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
- Once your bot is ready, make sure you copy it into the `main` branch of the repo you created
- Deadline is 15:00 on Friday July 12th
- Tournament will be 15:30 - 16:45 on Friday July 12th in the Open Space area

## TL;DR

1. Create a repository for your bot from [the template](https://github.com/new?owner=europybots2024&template_name=template_bot&template_owner=europybots2024).

2. Get started with:

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

## The game: Vendeeglobe

Around the world sailing race

Preview

![Preview](https://github.com/europybots2024/vendeeglobe/assets/39047984/1ed0ec51-4d42-40de-bed6-88eefebab866)


## Goal & general rules

- Sail around the world as fast as possible
- Start from les Sables-d’Olonne in France
- There are two mandatory checkpoints
- Each round has a time limit of 8 minutes (=80 days)

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
- Ships cannot crash into each other (ghosts)


