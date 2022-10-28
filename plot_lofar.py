from lofarantpos.db import LofarAntennaDatabase
from lofarantpos.geo import localnorth_to_etrs

db = LofarAntennaDatabase()

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

def plot_hba(station_name, ax=None, centre=None, subfield="", labels=False):
    """
    Plot LOFAR HBA tiles for one station

    Args:
        station_name: Station name, without suffix. E.g. "CS001"
        ax: existing matplotlib axes object to use
        centre: etrs coordinates of origin. Default: LBA phase centre of station.
        subfield: '0', '1' or ''to suffix after 'HBA' for e.g. CS002HBA1)
        labels: add labels
    """
    if centre is None:
        centre = db.phase_centres[station_name + "LBA"]

    if ax is None:
        fig, ax = plt.subplots()
        ax.set_aspect("equal")

    etrs_to_xyz = localnorth_to_etrs(centre).T

    if station_name + "HBA" + subfield not in db.hba_rotations:
        plot_hba(station_name, ax=ax, centre=centre, subfield="0", labels=labels)
        plot_hba(station_name, ax=ax, centre=centre, subfield="1", labels=labels)
        return

    etrs_delta = db.antenna_etrs(station_name + "HBA" + subfield) - centre
    xys = (etrs_to_xyz @ etrs_delta.T)[:2, :].T

    theta = db.hba_rotations[station_name + "HBA" + subfield]
    c, s = np.cos(theta), np.sin(theta)
    rot_mat = db.pqr_to_localnorth(station_name + "HBA")[:2, :2] @ np.array(
        ((c, s), (-s, c))
    )
    x_dir = rot_mat @ [5.15, 0]
    y_dir = rot_mat @ [0, 5.15]

    tile = np.array(
        [
            -0.5 * x_dir - 0.5 * y_dir,
            +0.5 * x_dir - 0.5 * y_dir,
            +0.5 * x_dir + 0.5 * y_dir,
            -0.5 * x_dir + 0.5 * y_dir,
            -0.5 * x_dir - 0.5 * y_dir,
        ]
    )

    for num, xy in enumerate(xys):
        x, y = xy
        ax.plot((x + tile)[:, 0], (y + tile)[:, 1], "k")
        if labels:
            if subfield == "1":
                num += 24
            ax.text(x, y, str(num))

def plot_lba(station_name, ax=None, centre=None, labels=False):
    """
    Plot LOFAR LBA locations for one station

    Args:
        station_name: Station name, without suffix. E.g. "CS001"
        ax: existing matplotlib axes object to use
        centre: etrs coordinates of origin. Default: LBA phase centre of station.
        labels: add labels
    """
    if centre is None:
        centre = db.phase_centres[station_name + "LBA"]

    if ax is None:
        fig, ax = plt.subplots()
        ax.set_aspect("equal")

    etrs_to_xyz = localnorth_to_etrs(centre).T
    etrs_delta = db.antenna_etrs(station_name + "LBA") - centre
    xys = (etrs_to_xyz @ etrs_delta.T)[:2, :].T

    ax.plot(xys[:, 0], xys[:, 1], "ko")

    if labels:
        for num, xy in enumerate(xys):
            x, y = xy
            ax.text(x, y, str(num))

def plot_cabinet(station_name, ax=None, centre=None, labels=False):
    """
    Plot LOFAR cabinet location for one station

    Args:
        station_name: Station name, without suffix. E.g. "CS001"
        ax: existing matplotlib axes object to use
        centre: etrs coordinates of origin. Default: LBA phase centre of station.
        labels: add label
    """
    if centre is None:
        centre = db.phase_centres[station_name + "LBA"]

    if ax is None:
        fig, ax = plt.subplots()
        ax.set_aspect("equal")

    etrs_to_xyz = localnorth_to_etrs(centre).T
    etrs_delta = db.cabinet_etrs[station_name] - centre
    x, y, _ = etrs_to_xyz @ etrs_delta

    ax.plot(x, y, "ro")
    if labels:
        ax.text(x, y, station_name + " cabinet")

def plot_station(station_name, ax=None, centre=None, labels=False):
    """
    Plot a LOFAR station

    Args:
        station_name: Station name, without suffix. E.g. "CS001"
        ax: existing matplotlib axes object to use
        labels: add labels
    """
    if centre is None:
        centre = db.phase_centres[station_name + "LBA"]

    if ax is None:
        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_title("LOFAR station " + station_name)

    plot_lba(station_name, ax=ax, centre=centre, labels=labels)
    plot_hba(station_name, ax=ax, centre=centre, labels=labels)
    plot_cabinet(station_name, ax=ax, centre=centre, labels=labels)

def plot_superterp(ax=None, labels=False, plot_circle=True):
    """
    Plot the LOFAR superterp
    
    Args:
        ax: existing matplotlib axes object to use
        labels: add labels
        plot_circle: plot a surrounding circle
    """
    if ax is None:
        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_xlabel("Local East (m)")
        ax.set_ylabel("Local North (m)")
        ax.set_title("LOFAR superterp")

    if plot_circle:
        circle1 = ax.add_patch(Circle((0, 0), radius=185, fill=False, edgecolor="k"))

    centre = db.phase_centres["CS002LBA"]
    for station_name in "CS002", "CS003", "CS004", "CS005", "CS006", "CS007":
        plot_station(station_name, ax=ax, centre=centre, labels=labels)
