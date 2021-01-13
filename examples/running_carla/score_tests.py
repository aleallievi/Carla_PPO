# !/usr/bin/env python

# Copyright (c) 2018-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
This module provides all atomic evaluation criteria required to analyze if a
scenario was completed successfully or failed.
Criteria should run continuously to monitor the state of a single actor, multiple
actors or environmental parameters. Hence, a termination is not required.
The atomic criteria are implemented with py_trees.
"""

import weakref
import math
import numpy as np
import py_trees
import shapely

import carla

# from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
# from srunner.scenariomanager.timer import GameTime
from traffic_events import TrafficEvent, TrafficEventType


class Criterion(object):

    """
    Base class for all criteria used to evaluate a scenario for success/failure
    Important parameters (PUBLIC):
    - name: Name of the criterion
    - expected_value_success:    Result in case of success
                                 (e.g. max_speed, zero collisions, ...)
    - expected_value_acceptable: Result that does not mean a failure,
                                 but is not good enough for a success
    - actual_value: Actual result after running the scenario
    - test_status: Used to access the result of the criterion
    - optional: Indicates if a criterion is optional (not used for overall analysis)
    """

    def __init__(self,
                 name,
                 actor,
                 _map
                 ):
        super(Criterion, self).__init__()

        self.name = name
        self.actor = actor
        self.map = _map
        self.actual_value = 0
        self.list_traffic_events = []


class RouteCompletionTest(Criterion):

    """
    Check at which stage of the route is the actor at each tick
    Important parameters:
    - actor: CARLA actor to be used for this test
    - route: Route to be checked
    - terminate_on_failure [optional]: If True, the complete scenario will terminate upon failure of this test
    """
    DISTANCE_THRESHOLD = 10.0  # meters
    WINDOWS_SIZE = 2

    def __init__(self, actor, route, _map, name="RouteCompletionTest", terminate_on_failure=False):
        """
        """
        super(RouteCompletionTest, self).__init__(name, actor, _map)
        self._actor = actor
        self._route = route
        self._map = _map

        self._wsize = self.WINDOWS_SIZE
        self._current_index = 0
        self._route_length = len(self._route)
        # self._waypoints, _ = zip(*self._route)
        self._waypoints = self._route
        self.target = self._waypoints[-1]

        self._accum_meters = []
        prev_wp = self._waypoints[0]
        for i, wp in enumerate(self._waypoints):
            d = wp.transform.location.distance(prev_wp.transform.location)
            if i > 0:
                accum = self._accum_meters[i - 1]
            else:
                accum = 0

            self._accum_meters.append(d + accum)
            prev_wp = wp

        self._traffic_event = TrafficEvent(event_type=TrafficEventType.ROUTE_COMPLETION)
        self.list_traffic_events.append(self._traffic_event)
        self._percentage_route_completed = 0.0
        self.is_route_completed = False

    def update(self):
        """
        Check if the actor location is within trigger region
        """

        # location = CarlaDataProvider.get_location(self._actor)
        location = self._actor.get_location()

        for index in range(self._current_index, min(self._current_index + self._wsize + 1, self._route_length)):

            # Get the dot product to know if it has passed this location
            ref_waypoint = self._waypoints[index].transform.location
            wp = self._map.get_waypoint(ref_waypoint)
            # wp = self._waypoints[index]
            wp_dir = wp.transform.get_forward_vector()          # Waypoint's forward vector
            wp_veh = location - ref_waypoint                    # vector waypoint - vehicle
            dot_ve_wp = wp_veh.x * wp_dir.x + wp_veh.y * wp_dir.y + wp_veh.z * wp_dir.z
            if dot_ve_wp > 0 or index == self._current_index:
                # DEBUG
                # print(f'wp idx:{index}')
                # increment completion based on cleared waypoint segment, include negative progress wrt current wp
                self._current_index = index
                self._percentage_route_completed = 100.0 * (
                            float(self._accum_meters[self._current_index]) + float(dot_ve_wp)) \
                                                   / float(self._accum_meters[-1])
                self._traffic_event.set_dict({
                    'route_completed': self._percentage_route_completed})
                self._traffic_event.set_message(
                    "Agent has completed > {:.2f}% of the route".format(
                        self._percentage_route_completed))

        if self._percentage_route_completed > 99.0 and location.distance(self.target) < self.DISTANCE_THRESHOLD:
            self.is_route_completed = True
            route_completion_event = TrafficEvent(event_type=TrafficEventType.ROUTE_COMPLETED)
            route_completion_event.set_message("Destination was successfully reached")
            self.list_traffic_events.append(route_completion_event)
            self._percentage_route_completed = 100

        self.actual_value = round(self._percentage_route_completed, 2)

        return self.actual_value, self._current_index, self.is_route_completed

