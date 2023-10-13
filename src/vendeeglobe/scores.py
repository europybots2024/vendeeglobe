# SPDX-License-Identifier: BSD-3-Clause

import os
from typing import Dict

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
    print("Scores:", scores)
    return scores


def _write_scores(scores: Dict[str, int]):
    fname = "scores.txt"
    with open(fname, "w") as f:
        for name, score in scores.items():
            f.write(f"{name}: {score}\n")


def get_current_scores(players: Dict[str, Player]) -> Dict[str, int]:
    player_groups = {0: [], 1: [], 2: []}

    current_scores = {}
    for player in players.values():
        n = len([ch for ch in player.checkpoints if ch.reached])
        player_groups[n].append(player)

    start = [config.start.longitude, config.start.latitude]

    # Players that reached 2 checkpoints
    group_players = []
    for player in player_groups[2]:
        if player.score is None:
            dist = distance_on_surface(
                origin=[player.longitude, player.latitude],
                to=start,
            )
            group_players.append((dist, player))
        else:
            current_scores[player.team] = player.score
    group_players.sort()
    for _, player in group_players:
        current_scores[player.team] = config.pop_score()
    # for player in player_groups[2]:
    #     current_scores[player.team] = scores[player.team] + player.score

    # Players that reached 1 checkpoint
    group_players = []
    for player in player_groups[1]:
        for ch in player.checkpoints:
            if not ch.reached:
                dist = distance_on_surface(
                    origin=[player.longitude, player.latitude],
                    to=[ch.longitude, ch.latitude],
                ) + distance_on_surface(
                    origin=[ch.longitude, ch.latitude],
                    to=start,
                )
                group_players.append((dist, player))
    group_players.sort()
    for _, player in group_players:
        current_scores[player.team] = config.pop_score()
    # for player in player_groups[1]:
    #     current_scores[player.team] = scores[player.team] + player.score

    # Players that reached 0 checkpoints
    group_players = []
    for player in player_groups[0]:
        dists = [
            distance_on_surface(
                origin=[player.longitude, player.latitude],
                to=[ch.longitude, ch.latitude],
            )
            for ch in player.checkpoints
        ]
        ind = np.argmin(dists)
        dist = (
            dists[ind]
            + distance_on_surface(
                origin=[
                    player.checkpoints[0].longitude,
                    player.checkpoints[1].latitude,
                ],
                to=[
                    player.checkpoints[1].longitude,
                    player.checkpoints[1].latitude,
                ],
            )
            + distance_on_surface(
                origin=[
                    player.checkpoints[(ind + 1) % 2].longitude,
                    player.checkpoints[(ind + 1) % 2].latitude,
                ],
                to=start,
            )
        )
        group_players.append((dist, player))
    group_players.sort()
    for _, player in group_players:
        current_scores[player.team] = config.pop_score()
    # for player in player_groups[0]:
    #     final_scores[player.team] = scores[player.team] + player.score
    return current_scores


def _get_final_scores(players: Dict[str, Player], scores: Dict[str, int]):
    current_scores = get_current_scores(players, scores)
    final_scores = {
        team: scores[team] + current_scores[team] for team in current_scores
    }
    return final_scores


def _print_scores(players: Dict[str, Player], final_scores: Dict[str, int]):
    # Print scores
    all_scores = [(p.team, p.score, final_scores[p.team]) for p in players.values()]
    sorted_scores = sorted(all_scores, key=lambda tup: tup[2], reverse=True)
    print("Scores:")
    for i, (name, score, total) in enumerate(sorted_scores):
        print(f"{i + 1}. {name}: {score} ({total})")


def finalize_scores(players: Dict[str, Player], test: bool = False):
    scores = _read_scores(players, test=test)
    final_scores = _get_final_scores(players, scores)
    _print_scores(players, final_scores)
    _write_scores(final_scores)
