"""Functions for using tracking to recognize actual waves.

Method for recognition is:
-1. merge potential waves
-2. track potential waves
-3. declare actual waves conditional on wave dynamics
"""

from __future__ import division

import numpy as np


def will_be_merged(section, list_of_waves):
    """Return whether or not a section is in an existing wave's search region.

    Args:
        section: a wave object
        list_of_waves: a list of waves having search regions in which a
                       wave might fall

    Returns:
        going_to_be_merged: evaluates to True if the section is in an
                            existing wave's search region.
    """
    # All sections are initially new waves & will not be merged.
    going_to_be_merged = False

    # Find the section's major axis' projection on the y axis.
    delta_y_left = np.round(
        section.centroid[0] * np.tan(np.deg2rad(section.axis_angle))
    )
    left_y = int(section.centroid[1] + delta_y_left)

    # For each existing wave, see if the section's axis falls in
    # another wave's search region.
    for wave in list_of_waves:
        if (
            left_y >= wave.searchroi_coors[0][1]
            and left_y <= wave.searchroi_coors[3][1]
        ):
            going_to_be_merged = True
            break

    return going_to_be_merged

def track(list_of_waves, frame, frame_number, last_frame):
    """Track a wave.

    Updates the dynamic Wave attributes.

    Args:
        list_of_waves: a list of waves to track
        frame: a frame from a cv2.video_reader object
        frame_number: number of the frame in a sequence
        last_frame: final frame number, provided to kill all waves if
                    necessary
    """

    # Ensure frame_number is a scalar
    if isinstance(frame_number, (np.ndarray, list)):
        frame_number = frame_number.item() if isinstance(frame_number, np.ndarray) else frame_number[0]

    # Ensure last_frame is a scalar
    if isinstance(last_frame, np.ndarray):
        if last_frame.size == 1:
            last_frame = last_frame.item()
        else:
            print("Warning: last_frame is an array with multiple elements. Using only the first element.")
            last_frame = last_frame[0]  # or handle this case as needed
    elif isinstance(last_frame, list):
        last_frame = last_frame[0]  # or handle this case as needed

    for wave in list_of_waves:
        # Update search roi for tracking waves and merging waves.
        wave.update_searchroi_coors()

        # Capture all non-zero points in the new roi.
        wave.update_points(frame)

        # Check if wave has died.
        wave.update_death(frame_number)

        # Modify the comparison to handle last_frame as an array
        if isinstance(last_frame, (np.ndarray, list)):
            if frame_number in last_frame:  # Check if frame_number is in last_frame array
                wave.death = frame_number
        else:
            if frame_number == last_frame:
                wave.death = frame_number

        # Update centroids.
        wave.update_centroid()

        # Update bounding boxes for display.
        wave.update_boundingbox_coors()

        # Update displacement vectors.
        wave.update_displacement()

        # Update wave masses.
        wave.update_mass()

        # Check masses and dynamics conditionals.
        wave.update_recognized()

    return






