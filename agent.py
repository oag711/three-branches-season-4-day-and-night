
"""A small Days at Three Branches starter built entirely from ``sandbox.village``."""

from sandbox.observation_types import ThreeBranchesAction, ThreeBranchesObservation
from sandbox.village import action, day, geometry, layout, me, people, props


def _cell_centre(cell: dict[str, int]) -> dict[str, float]:
    """Return the point at the centre of one village cell."""
    return {"x": cell["x"] + 0.5, "y": cell["y"] + 0.5}


class Agent:
    """Villagers have different jobs around the village."""

    def reset(self, seed: int, observation: ThreeBranchesObservation) -> None:
        """Prepare for a day."""

        # Find this villager's number.
        player_id = me.player_id(observation)
        number = int(player_id.split("_")[1])

        # Give each villager a different role.
        if number == 1:
            self.role = "pump"
        elif number == 2:
            self.role = "bench1"
        elif number == 3:
            self.role = "bench2"
        elif number == 4:
            self.role = "crop1"
        elif number == 5:
            self.role = "crop2"
        elif number == 6:
            self.role = "crate1"
        elif number == 7:
            self.role = "crate2"
        elif number == 8:
            self.role = "wander1"
        elif number == 9:
            self.role = "wander2"
        else:
            self.role = "home"

        # Find the home doorway.
        home = me.home(observation)

        if home != "none":
            self.door = layout.doorway(observation, home)
        else:
            self.door = None

        # Remember the village props.
        self.pump = None
        self.benches = []
        self.crops = []
        self.crates = []

        for prop in props.all(observation):
            if prop["type"] == "pump":
                self.pump = _cell_centre(prop["cell"])

            if prop["type"] == "bench":
                self.benches.append(_cell_centre(prop["cell"]))

            if "crop" in prop["type"]:
                self.crops.append(_cell_centre(prop["cell"]))

            if "crate" in prop["type"]:
                self.crates.append(_cell_centre(prop["cell"]))

        # Route information.
        self.route = []
        self.route_index = 0
        self.route_target = None

        # Wait before waving again.
        self.wave_cooldown = 0

        # Count ticks where the current route is blocked.
        self.stuck_ticks = 0

        # Build the first route.
        self._make_route(observation)

    def _find_target(self, observation):
        """Find this villager's target for the current time of day."""

        phase = day.phase(observation)

        # Everyone heads home at night.
        if phase == "night":
            return self.door

        # Most workers finish early and go home in the evening.
        if phase == "evening":
            if self.role != "pump":
                if self.role != "bench1" and self.role != "bench2":
                    return self.door

        # At midday, crop and crate workers take a break.
        if phase == "midday":
            if self.role == "crop1" or self.role == "crop2":
                if len(self.benches) > 0:
                    return self.benches[0]
                return self.pump

            if self.role == "crate1" or self.role == "crate2":
                if len(self.benches) > 1:
                    return self.benches[1]
                if len(self.benches) > 0:
                    return self.benches[0]
                return self.pump

            if self.role == "wander1" or self.role == "wander2":
                return self.pump

        target = None

        if self.role == "pump":
            target = self.pump

        elif self.role == "bench1":
            if len(self.benches) > 0:
                target = self.benches[0]

        elif self.role == "bench2":
            if len(self.benches) > 1:
                target = self.benches[1]

        elif self.role == "crop1":
            if len(self.crops) > 0:
                target = self.crops[0]

        elif self.role == "crop2":
            if len(self.crops) > 1:
                target = self.crops[1]
            elif len(self.crops) > 0:
                target = self.crops[0]

        elif self.role == "crate1":
            if len(self.crates) > 0:
                target = self.crates[0]

        elif self.role == "crate2":
            if len(self.crates) > 1:
                target = self.crates[1]
            elif len(self.crates) > 0:
                target = self.crates[0]

        elif self.role == "wander1":
            if len(self.crops) > 0:
                target = self.crops[0]
            elif self.pump is not None:
                target = self.pump

        elif self.role == "wander2":
            if len(self.crates) > 0:
                target = self.crates[0]
            elif self.pump is not None:
                target = self.pump

        elif self.role == "home":
            target = self.door

        return target

    def _make_route(self, observation: ThreeBranchesObservation) -> None:
        """Build a route using one grid search."""

        target = self._find_target(observation)

        if target is None:
            self.route = []
            self.route_index = 0
            self.route_target = None
            return

        start = layout.cell_at(
            observation,
            me.position(observation)
        )

        if start is None:
            self.route = []
            self.route_index = 0
            self.route_target = target
            return

        frame = layout.frame(observation)
        cells_x = int(frame["cells_x"])
        cells_y = int(frame["cells_y"])
        max_cells = cells_x * cells_y

        # Search the grid and remember how each cell was reached.
        queue = [start]
        visited = set()
        visited.add((start["x"], start["y"]))
        previous = {}

        best_cell = start
        best_distance = geometry.distance(
            _cell_centre(start),
            target
        )

        for current in queue:
            current_centre = _cell_centre(current)
            distance = geometry.distance(
                current_centre,
                target
            )

            if distance < best_distance:
                best_distance = distance
                best_cell = current

            # Stop when we find a cell close to the target.
            if distance <= 1.1:
                best_cell = current
                break

            neighbors = []
            neighbors.append({"x": current["x"] + 1, "y": current["y"]})
            neighbors.append({"x": current["x"] - 1, "y": current["y"]})
            neighbors.append({"x": current["x"], "y": current["y"] + 1})
            neighbors.append({"x": current["x"], "y": current["y"] - 1})

            for neighbor in neighbors:
                x = neighbor["x"]
                y = neighbor["y"]
                key = (x, y)

                inside = (
                    x >= 0
                    and x < cells_x
                    and y >= 0
                    and y < cells_y
                )

                if inside and key not in visited:
                    if layout.can_step(
                        observation,
                        current,
                        neighbor
                    ):
                        visited.add(key)
                        previous[key] = current
                        queue.append(neighbor)

        # Build the route backward, then reverse it.
        route = []
        current = best_cell
        found_start = False

        for _ in range(max_cells):
            route.append(current)

            if (
                current["x"] == start["x"]
                and current["y"] == start["y"]
            ):
                found_start = True
                break

            key = (current["x"], current["y"])

            if key in previous:
                current = previous[key]
            else:
                break

        if found_start:
            route.reverse()
            self.route = route
            self.route_index = 0
            self.route_target = target
        else:
            self.route = []
            self.route_index = 0
            self.route_target = target

    def _route_needs_rebuild(self, observation) -> bool:
        """Check whether the current route should be rebuilt."""

        target = self._find_target(observation)

        if target is None:
            return False

        if self.route_target is None:
            return True

        if geometry.distance(
            target,
            self.route_target
        ) > 0.1:
            return True

        return False

    def _next_route_position(self, observation):
        """Return the next safe position on the current route."""

        current_cell = layout.cell_at(
            observation,
            me.position(observation)
        )

        if current_cell is None:
            return None

        # Remove route cells already reached.
        while self.route_index < len(self.route):
            route_cell = self.route[self.route_index]

            if (
                current_cell["x"] == route_cell["x"]
                and current_cell["y"] == route_cell["y"]
            ):
                self.route_index += 1
            else:
                break

        if self.route_index >= len(self.route):
            return None

        next_cell = self.route[self.route_index]

        if layout.can_step(
            observation,
            current_cell,
            next_cell
        ):
            return _cell_centre(next_cell)

        return None

    def act(
        self,
        observation: ThreeBranchesObservation
    ) -> ThreeBranchesAction:
        """Choose one simple order from the current observation."""

        heading = me.heading(observation)

        # Wave sometimes, not on every tick.
        expression = "none"

        if self.wave_cooldown > 0:
            self.wave_cooldown -= 1

        if self.wave_cooldown == 0:
            if day.phase(observation) != "night":
                if people.seen(observation):
                    expression = "wave"
                    self.wave_cooldown = 30

        # Use a nearby bench during the day.
        usable = props.usable(observation)

        if day.phase(observation) != "night":
            if usable is not None and usable["type"] == "bench":
                if self.role == "bench1" or self.role == "bench2":
                    return action.stand(
                        heading,
                        "use"
                    )

        here = me.position(observation)

        # Rebuild the route only when necessary.
        if self._route_needs_rebuild(observation):
            self._make_route(observation)

        # Get the next position on the route.
        next_position = self._next_route_position(observation)

        if next_position is not None:
            self.stuck_ticks = 0

            return action.walk(
                geometry.heading_to(
                    here,
                    next_position
                ),
                1.0,
                expression
            )

        # Rebuild after several blocked ticks.
        if self.route_index < len(self.route):
            self.stuck_ticks += 1

            if self.stuck_ticks >= 10:
                self._make_route(observation)
                self.stuck_ticks = 0

        # If the target is reached, stop turning toward it.
        return action.stand(
            heading,
            expression
        )


# Optional: messaging.
# On your turn, chat receives messages addressed to your player since
# its previous turn. Return messages with a recipient and text, or nothing
# to stay silent. Use None as the recipient to broadcast.
#
# def chat(self, inbox: list[dict]) -> list[dict] | None:
#     ...