# SPDX-License-Identifier: BSD-3-Clause

import os
from typing import Dict, List

import numpy as np

from . import config
from .player import Player
from .utils import distance_on_surface


def _read_scores(players: Dict[str, Player], test: bool) -> Dict[str, int]:
    scores = {p: 0 for p in players}
    fname = "scores.txt"
    if os.path.exists(fname) and (not test):
        with open(fname, "r") as f:
            contents = f.readlines()
        for line in contents:
            name, score = line.split(":")
            scores[name] = int(score.strip())
    # print("Scores:", scores)
    return scores


def _write_scores(scores: Dict[str, int]):
    fname = "scores.txt"
    with open(fname, "w") as f:
        for name, score in scores.items():
            f.write(f"{name}: {score}\n")


def get_player_points(player: Player) -> int:
    start = [config.start.longitude, config.start.latitude]
    checkpoints_reached = len([ch for ch in player.checkpoints if ch.reached])
    # npoints = 1_000_000

    points = checkpoints_reached * config.score_step + player.bonus
    if checkpoints_reached == 2:
        dist = distance_on_surface(
            origin=[player.longitude, player.latitude],
            to=start,
        )
        points += config.score_step - int(dist)
    elif checkpoints_reached == 1:
        for ch in player.checkpoints:
            if not ch.reached:
                dist = distance_on_surface(
                    origin=[player.longitude, player.latitude],
                    to=[ch.longitude, ch.latitude],
                )
                points += config.score_step - int(dist)
    elif checkpoints_reached == 0:
        dist = min(
            distance_on_surface(
                origin=[player.longitude, player.latitude],
                to=[ch.longitude, ch.latitude],
            )
            for ch in player.checkpoints
        )
        points += config.score_step - int(dist)

    return points


def get_rankings(players: Dict[str, Player]) -> Dict[str, int]:
    status = [
        (
            get_player_points(player),
            # player.distance_travelled,
            player.team,
            # len([ch for ch in player.checkpoints if ch.reached]),
        )
        for player in players.values()
    ]
    return [team for _, team in sorted(status, reverse=True)]
    # for i, (_, team) in enumerate(sorted(status, reverse=True)):
    #     self.player_boxes[i].setText(f"{i+1}. {team}: {int(dist)} km [{nch}]")


# def get_current_scores(players: Dict[str, Player]) -> Dict[str, int]:
#     player_groups = {0: [], 1: [], 2: []}

#     current_scores = {}
#     for player in players.values():
#         n = len([ch for ch in player.checkpoints if ch.reached])
#         player_groups[n].append(player)

#     start = [config.start.longitude, config.start.latitude]

#     # Players that reached 2 checkpoints
#     group_players = []
#     for player in player_groups[2]:
#         if player.score is None:
#             dist = distance_on_surface(
#                 origin=[player.longitude, player.latitude],
#                 to=start,
#             )
#             group_players.append((dist, player))
#         else:
#             current_scores[player.team] = player.score
#     group_players.sort()
#     for _, player in group_players:
#         current_scores[player.team] = config.pop_score()
#     # for player in player_groups[2]:
#     #     current_scores[player.team] = scores[player.team] + player.score

#     # Players that reached 1 checkpoint
#     group_players = []
#     for player in player_groups[1]:
#         for ch in player.checkpoints:
#             if not ch.reached:
#                 dist = distance_on_surface(
#                     origin=[player.longitude, player.latitude],
#                     to=[ch.longitude, ch.latitude],
#                 ) + distance_on_surface(
#                     origin=[ch.longitude, ch.latitude],
#                     to=start,
#                 )
#                 group_players.append((dist, player))
#     group_players.sort()
#     for _, player in group_players:
#         current_scores[player.team] = config.pop_score()
#     # for player in player_groups[1]:
#     #     current_scores[player.team] = scores[player.team] + player.score

#     # Players that reached 0 checkpoints
#     group_players = []
#     for player in player_groups[0]:
#         dists = [
#             distance_on_surface(
#                 origin=[player.longitude, player.latitude],
#                 to=[ch.longitude, ch.latitude],
#             )
#             for ch in player.checkpoints
#         ]
#         ind = np.argmin(dists)
#         dist = (
#             dists[ind]
#             + distance_on_surface(
#                 origin=[
#                     player.checkpoints[0].longitude,
#                     player.checkpoints[1].latitude,
#                 ],
#                 to=[
#                     player.checkpoints[1].longitude,
#                     player.checkpoints[1].latitude,
#                 ],
#             )
#             + distance_on_surface(
#                 origin=[
#                     player.checkpoints[(ind + 1) % 2].longitude,
#                     player.checkpoints[(ind + 1) % 2].latitude,
#                 ],
#                 to=start,
#             )
#         )
#         group_players.append((dist, player))
#     group_players.sort()
#     for _, player in group_players:
#         current_scores[player.team] = config.pop_score()
#     # for player in player_groups[0]:
#     #     final_scores[player.team] = scores[player.team] + player.score
#     return current_scores


def _get_final_scores(players: Dict[str, Player], scores: Dict[str, int]):
    # current_scores = get_current_scores(players)
    rankings = get_rankings(players)
    for_grabs = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    final_scores = {}
    round_scores = {}
    for team in rankings:
        round_scores[team] = for_grabs.pop(0) if for_grabs else 0
        final_scores[team] = scores[team] + round_scores[team]
    return round_scores, final_scores


def _print_scores(
    round_scores: Dict[str, int],
    final_scores: Dict[str, int],
):
    # Print scores
    all_scores = [
        (team, round_scores[team], final_scores[team]) for team in final_scores
    ]
    sorted_scores = sorted(all_scores, key=lambda tup: tup[2], reverse=True)
    print("Scores:")
    for i, (name, score, total) in enumerate(sorted_scores):
        print(f"{i + 1}. {name}: {total} ({score})")


def finalize_scores(players: Dict[str, Player], test: bool = False):
    scores = _read_scores(players, test=test)
    round_scores, final_scores = _get_final_scores(players, scores)
    _print_scores(round_scores=round_scores, final_scores=final_scores)
    _write_scores(final_scores)
