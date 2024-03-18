# SPDX-License-Identifier: BSD-3-Clause

import os
from typing import Dict

import numpy as np

from . import config
from .player import Player
from .utils import distance_on_surface


def _make_folder(folder: str):
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass


def read_scores(players: Dict[str, Player]) -> Dict[str, int]:
    scores = {p: 0 for p in players}
    folder = ".scores"
    if not os.path.exists(folder):
        return scores
    for player in players:
        fname = os.path.join(folder, f"{player}_scores.txt")
        if os.path.exists(fname):
            with open(fname, "r") as f:
                contents = f.readlines()
            scores[player] = sum(int(line.strip()) for line in contents)
    return scores


def _write_scores(scores: Dict[str, int]):
    folder = ".scores"
    _make_folder(folder)
    for name, score in scores.items():
        fname = os.path.join(folder, f"{name}_scores.txt")
        mode = 'w+' if os.path.exists(fname) else 'w'
        with open(fname, mode) as f:
            f.write(f'{score}\n')


def get_player_points(player: Player) -> int:
    checkpoints_reached = len([ch for ch in player.checkpoints if ch.reached])

    points = checkpoints_reached * config.score_step + player.bonus
    if checkpoints_reached == 2:
        dist = distance_on_surface(
            longitude1=player.longitude,
            latitude1=player.latitude,
            longitude2=config.start.longitude,
            latitude2=config.start.latitude,
        )
        points += config.score_step - int(dist)
    elif checkpoints_reached == 1:
        for ch in player.checkpoints:
            if not ch.reached:
                dist = distance_on_surface(
                    longitude1=player.longitude,
                    latitude1=player.latitude,
                    longitude2=ch.longitude,
                    latitude2=ch.latitude,
                )
                points += config.score_step - int(dist)
    elif checkpoints_reached == 0:
        dist = min(
            distance_on_surface(
                longitude1=player.longitude,
                latitude1=player.latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            for ch in player.checkpoints
        )
        points += config.score_step - int(dist)

    return points


def get_rankings(
    players: Dict[str, Player], player_points: np.ndarray
) -> Dict[str, int]:
    status = [
        (player_points[i], player.team) for i, player in enumerate(players.values())
    ]
    return [team for _, team in sorted(status, reverse=True)]


def _get_final_scores(
    players: Dict[str, Player], scores: Dict[str, int], player_points: np.ndarray
):
    rankings = get_rankings(players, player_points)
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
    all_scores = [
        (team, round_scores[team], final_scores[team]) for team in final_scores
    ]
    sorted_scores = sorted(all_scores, key=lambda tup: tup[2], reverse=True)
    print("Scores:")
    for i, (name, score, total) in enumerate(sorted_scores):
        print(f"{i + 1}. {name}: {total} ({score})")


def finalize_scores(players: Dict[str, Player], player_points: np.ndarray):
    scores = read_scores(players)
    round_scores, final_scores = _get_final_scores(players, scores, player_points)
    _print_scores(round_scores=round_scores, final_scores=final_scores)
    _write_scores(round_scores)
    return final_scores


def read_fastest_times(players: Dict[str, Player]) -> Dict[str, int]:
    times = {p: np.inf for p in players}
    folder = ".scores"
    if not os.path.exists(folder):
        return times
    for name in players:
        fname = os.path.join(folder, f"{name}_times.txt")
        if os.path.exists(fname):
            with open(fname, "r") as f:
                contents = f.readlines()
            times[name] = min(float(t.strip()) for t in contents)
    return times


def write_times(times: Dict[str, Player]):
    folder = ".scores"
    _make_folder(folder)
    for name, t in times.items():
        fname = os.path.join(folder, f"{name}_times.txt")
        mode = 'w+' if os.path.exists(fname) else 'w'
        with open(fname, mode) as f:
            f.write(f"{t}\n")
