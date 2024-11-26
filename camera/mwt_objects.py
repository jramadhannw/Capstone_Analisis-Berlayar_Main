"""Objects for implementing wave tracking."""

from __future__ import division

import math
from collections import deque

import cv2
import numpy as np

# Pixel height to buffer a section's search region for other sections:
SEARCH_REGION_BUFFER = 15
# Length of Deque to keep track of displacement of the wave:
TRACKING_HISTORY = 21

# Width and height of frame in analysis steps (not original dimensions):
ANALYSIS_FRAME_WIDTH = 320
ANALYSIS_FRAME_HEIGHT = 180

# The minimum orthogonal displacement and mass to be considered an actual wave:
DISPLACEMENT_THRESHOLD = 10
MASS_THRESHOLD = 200

# The axis of major waves in the scene, counter-clockwise from horizon:
GLOBAL_WAVE_AXIS = 5.0

# Global variable seed for naming detected waves:
NAME_SEED = 0


class Section:
    """Define a Section representing a detected wave.

    Filtered contours become "sections" with attributes that are updated dynamically.
    """

    def __init__(self, points, birth):
        """Initialize a new Section object.

        Args:
            points: Array of points representing the wave contour.
            birth: Time of birth for the wave.
        """
        self.name = _generate_name()
        self.points = points
        self.birth = birth
        self.axis_angle = GLOBAL_WAVE_AXIS
        self.centroid = _get_centroid(self.points)
        self.centroid_vec = deque([self.centroid], maxlen=TRACKING_HISTORY)
        self.original_axis = _get_standard_form_line(self.centroid, self.axis_angle)
        self.searchroi_coors = _get_searchroi_coors(self.centroid, self.axis_angle, SEARCH_REGION_BUFFER, ANALYSIS_FRAME_WIDTH)
        self.boundingbox_coors = np.int0(cv2.boxPoints(cv2.minAreaRect(points)))
        self.displacement = 0
        self.max_displacement = self.displacement
        self.displacement_vec = deque([self.displacement], maxlen=TRACKING_HISTORY)
        self.mass = len(self.points)
        self.max_mass = self.mass
        self.recognized = False
        self.death = None

    def update_searchroi_coors(self):
        """Update the search region of interest for tracking the wave."""
        self.searchroi_coors = _get_searchroi_coors(self.centroid, self.axis_angle, SEARCH_REGION_BUFFER, ANALYSIS_FRAME_WIDTH)

    def update_death(self, frame_number):
        """Update the death status of the wave.

        Args:
            frame_number: Current frame number in the video sequence.
        """
        if self.points is None:
            self.death = frame_number

    def update_points(self, frame):
        """Update wave points based on the current frame.

        Args:
            frame: Current frame to obtain a new binary representation of the wave.
        """
        # Create a polygon object of the wave's search region
        rect = self.searchroi_coors
        poly = np.array([rect], dtype=np.int32)

        # Create a zero-valued image to overlay the ROI polygon
        img = np.zeros((ANALYSIS_FRAME_HEIGHT, ANALYSIS_FRAME_WIDTH), np.uint8)

        # Fill the polygon ROI in the zero-value image with ones
        img = cv2.fillPoly(img, poly, 255)

        # Resize mask to match frame size
        img = cv2.resize(img, (frame.shape[1], frame.shape[0]))

        # Perform bitwise AND with the actual image to obtain a "masked" image
        res = cv2.bitwise_and(frame, frame, mask=img)

        # Find all points in the ROI
        points = cv2.findNonZero(res)
        if points is None or len(points) == 0:
            print("No points found in ROI.")
            self.points = None
            return

        # Update points
        self.points = points


    def update_centroid(self):
        """Update the centroid of the wave."""
        self.centroid = _get_centroid(self.points)

        # Update centroid vector
        self.centroid_vec.append(self.centroid)

    def update_boundingbox_coors(self):
        """Update bounding box coordinates for visualization."""
        if self.points is not None:
            # Calculate moments to determine bounding box
            X = [p[0][0] for p in self.points]
            Y = [p[0][1] for p in self.points]
            mean_x = np.mean(X)
            mean_y = np.mean(Y)
            std_x = np.std(X)
            std_y = np.std(Y)

            # Capture points without outliers for display
            points_without_outliers = np.array(
                [p[0] for p in self.points
                 if np.abs(p[0][0] - mean_x) < 3 * std_x and
                    np.abs(p[0][1] - mean_y) < 3 * std_y]
            )

            # Calculate the minimum area rectangle for the bounding box
            rect = cv2.minAreaRect(points_without_outliers)
            box = cv2.boxPoints(rect)
            self.boundingbox_coors = np.int0(box)
        else:
            self.boundingbox_coors = None

    def update_displacement(self):
        """Update wave displacement and maximum displacement."""
        if self.centroid is not None:
            self.displacement = _get_orthogonal_displacement(self.centroid, self.original_axis)

            # Update maximum displacement if necessary
            if self.displacement > self.max_displacement:
                self.max_displacement = self.displacement

            # Update displacement vector
            self.displacement_vec.append(self.displacement)

    def update_mass(self):
        """Update the mass of the wave."""
        self.mass = _get_mass(self.points)

        # Update maximum mass if necessary
        if self.mass > self.max_mass:
            self.max_mass = self.mass

    def update_recognized(self):
        """Update recognized status of the wave based on thresholds."""
        if not self.recognized:
            if self.max_displacement >= DISPLACEMENT_THRESHOLD and self.max_mass >= MASS_THRESHOLD:
                self.recognized = True


def _get_mass(points):
    """Calculate the mass of the wave.

    Args:
        points: Array of non-zero points.

    Returns:
        mass: Total number of points representing the mass.
    """
    return len(points) if points is not None else 0


def _get_orthogonal_displacement(point, standard_form_line):
    """Calculate the orthogonal distance of a point to a line.

    Args:
        point: A two-element array representing a point [x, y].
        standard_form_line: A three-element array representing a line in standard form [A, B, C].

    Returns:
        ortho_disp: Orthogonal distance from the point to the line.
    """
    a, b, c = standard_form_line
    x0, y0 = point
    return int(np.abs(a * x0 + b * y0 + c) / math.sqrt(a**2 + b**2))


def _get_standard_form_line(point, angle):
    """Get the standard form representation of a line based on a point and angle.

    Args:
        point: A two-element array representing a point [x, y].
        angle: Float representing the counterclockwise angle from the horizon of the line.

    Returns:
        coefficients: A three-element array representing line coefficients [A, B, C].
    """
    coefficients = [
        np.tan(np.deg2rad(-angle)),
        -1,
        point[1] - np.tan(np.deg2rad(-angle)) * point[0]
    ]
    return coefficients


def _get_centroid(points):
    """Calculate the centroid of the wave.

    Args:
        points: Array of points representing the wave.

    Returns:
        centroid: A two-element array [x, y] representing the center of mass, or None if points are empty.
    """
    if points is not None:
        x_coords = [p[0][0] for p in points]
        y_coords = [p[0][1] for p in points]
        return [int(sum(x_coords) / len(points)), int(sum(y_coords) / len(points))]
    return None


def _get_searchroi_coors(centroid, angle, searchroi_buffer, frame_width):
    """Get the coordinates of the search region of interest.

    Args:
        centroid: A two-element array representing the center of mass of the wave.
        angle: Counterclockwise angle from the horizon of the wave's axis.
        searchroi_buffer: Buffer in pixels to expand the search region.
        frame_width: Width of the frame to establish bounds.

    Returns:
        polygon_coors: A four-element array representing coordinates of the search region polygon.
    """
    delta_y_left = np.round(centroid[0] * np.tan(np.deg2rad(angle)))
    delta_y_right = np.round((frame_width - centroid[0]) * np.tan(np.deg2rad(angle)))

    upper_left = [0, int(centroid[1] + delta_y_left - searchroi_buffer)]
    upper_right = [frame_width, int(centroid[1] - delta_y_right - searchroi_buffer)]
    lower_left = [0, int(centroid[1] + delta_y_left + searchroi_buffer)]
    lower_right = [frame_width, int(centroid[1] - delta_y_right + searchroi_buffer)]

    return [upper_left, upper_right, lower_right, lower_left]


def _generate_name():
    """Generate a unique name for a wave based on a global seed.

    Returns:
        NAME_SEED: Next integer in a sequence for wave identification.
    """
    global NAME_SEED
    NAME_SEED += 1
    return NAME_SEED
