import battlecode
import time
import random
import numpy as np

#Start a game
game = battlecode.Game('SAMplayer')

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

"""
Colonization code below
"""

for state in game.turns():
    # Your Code will run within this loop

    num_entities = len(list(state.get_entities(team=state.my_team)))
    num_entities_to_run = num_entities if num_entities <= 80 else 80
    unoccupied_sectors = get_unoccupied_sectors(state)

    for entity in state.get_entities(team=state.my_team):
        if num_entities_to_run > 0:
            num_entities_to_run -= 1
        else:
            break

        my_location = entity.location
        # near_entities = entity.entities_within_euclidean_distance(1.9)
        # near_entities = list(filter(lambda x: x.can_be_picked, near_entities))
        is_building = False

        # Check for possibility of building in unowned sector
        for d in battlecode.Direction.directions():
            if state.map.location_on_map(my_location.adjacent_location_in_direction(d)):
                sector_in_direction = state.map.sector_at(my_location.adjacent_location_in_direction(d))
                if entity.can_build(d) and sector_in_direction in unoccupied_sectors:
                    entity.queue_build(d)
                    is_building = True

        if not is_building:
            unowned_sectors = []
            for top_left in state.map._sectors:
                sector = state.map.sector_at(top_left)
                if sector.team != state.my_team:
                    unowned_sectors.append(sector)
            # if len(unowned_sectors) > 0:
            #     print(unowned_sectors)

            closest_center = None
            dist_closest_sector = np.inf
            for s in get_unoccupied_sectors(state):
                center = battlecode.Location(s.top_left.x + 2, s.top_left.y + 2)
                if my_location.adjacent_distance_to(center) < dist_closest_sector:
                    closest_center = center
                    dist_closest_sector = my_location.distance_to(center)
            if closest_center is not None:
                opt_direction = my_location.direction_to(closest_center)
                for _ in range(9):
                    if entity.can_move(opt_direction):
                        entity.queue_move(opt_direction)
                        break
                    opt_direction = opt_direction.rotate_counter_clockwise_degrees(45)


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
