import battlecode
import time
import random
import numpy as np


# Global Constants
CAP_ROBOTS_TO_PROCESS = 80

#Start a game
game = battlecode.Game('SAMcolonize')

start = time.clock()

#define helper functions here
def nearest_my_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.my_team):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist < nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def nearest_enemy_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist< nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def is_small_map(state):
    return state.map.height <= 10 or state.map.width <= 10

def get_entity_sector(entity):
    return(int(entity.location.x/5), int(entity.location.y/5))

def get_unoccupied_sectors(state):
    occupied_sectors = [state.map._sectors[k] for k in state.map._sectors]
    our_glass_statues = state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.my_team)
    for statue in our_glass_statues:
        sector = state.map.sector_at(statue.location)
        if sector in occupied_sectors:
            occupied_sectors.remove(sector)
    return occupied_sectors

def get_move_direction(destination):
    pass

"""
Colonization code below
"""

for state in game.turns():
    # Your code will run within this loop

    all_entities = list(state.get_entities(team=state.my_team))
    num_entities = len(all_entities)
    num_entities_to_run = num_entities if num_entities <= CAP_ROBOTS_TO_PROCESS else CAP_ROBOTS_TO_PROCESS
    unoccupied_sectors = get_unoccupied_sectors(state)
    sector_assignments = [0]*len(unoccupied_sectors)
    if len(unoccupied_sectors) > 0:
        cap_assignments = num_entities_to_run // len(unoccupied_sectors)
    else:
        cap_assignments = 0

    for entity in all_entities:
        if num_entities_to_run > 0:
            num_entities_to_run -= 1
        else:
            break

        my_location = entity.location
        is_building = False

        # Check for possibility of building in unowned sector
        for d in battlecode.Direction.directions():
            if state.map.location_on_map(my_location.adjacent_location_in_direction(d)):
                sector_in_direction = state.map.sector_at(my_location.adjacent_location_in_direction(d))
                if entity.can_build(d) and sector_in_direction in unoccupied_sectors:
                    entity.queue_build(d)
                    is_building = True

        # If not building this turn
        if not is_building:
            unowned_sectors = []
            for top_left in state.map._sectors:
                sector = state.map.sector_at(top_left)
                if sector.team != state.my_team:
                    unowned_sectors.append(sector)

            # Initialize max tracking variables
            closest_center = None
            closest_sector_index = -1
            dist_closest_sector = np.inf

            for i in range(len(unoccupied_sectors)):
                s = unoccupied_sectors[i]
                center = battlecode.Location(s.top_left.x + 2, s.top_left.y + 2)

                is_closer = my_location.distance_to(center) < dist_closest_sector
                is_not_capped = sector_assignments[i] <= cap_assignments

                if is_closer and is_not_capped:
                    closest_center = center
                    closest_sector_index = i
                    dist_closest_sector = my_location.distance_to(center)
            if closest_center is not None:
                opt_direction = my_location.direction_to(closest_center)
                if entity.can_move(opt_direction):
                    sector_assignments[closest_sector_index] += 1
                    entity.queue_move(opt_direction)
                    continue
                else:
                    other_directions = battlecode.Direction.directions()
                    other_directions.remove(opt_direction)
                    other_directions = np.random.permutation(other_directions)
                for dir in other_directions:
                    if entity.can_move(dir):
                        sector_assignments[closest_sector_index] += 1
                        entity.queue_move(dir)
                        break


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
