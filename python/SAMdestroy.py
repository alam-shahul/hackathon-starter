import battlecode
import time
import random
import numpy as np

#Start a game
game = battlecode.Game('SAMattack')

start = time.clock()

#define helper functions here
def nearest_my_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.my_team):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist< nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def nearest_enemy_glass_state_in_any_sector(state, entity):
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

def is_throw_path_valid(state, source, target):
    # Checks if the path between source and target is clear of hedges and target is on a throwable trajectory

    direction = source.location.direction_to(target.location)

    dx = target.location.x - source.location.x
    dy = target.location.y - source.location.y
    
    if (abs(dx) != abs(dy) and dx != 0 and dy != 0):                                         
        print(dx, dy)
        return False

    print('Got past')
    initial = source.location

    for i in range(max(abs(dx), abs(dy))):
        interm_loc = battlecode.Location(initial.x+ i*direction.dx, initial.y+i*direction.dy)
        on_map = state.map.location_on_map(interm_loc)
        if (not on_map):
            return False

        is_occupied = len(list(state.get_entities(location = interm_loc, entity_type=battlecode.Entity.HEDGE))) > 0

        if is_occupied:
            return False

    return True

""" Don't use this; use sector_at
def get_entity_sector(entity):
    return(entity.location.x // 5, entity.location.y // 5)
"""

"""
Destroy code below
"""
   
for state in game.turns():
    # Your Code will run within this loop
#    print(len(list(state.get_entities(team=state.my_team))))
    
    for entity in state.get_entities(team=state.my_team):
        if entity.cooldown != 0:
            continue

        my_neighbors = list(entity.entities_within_adjacent_distance(1, iterator=list(state.get_entities(entity_type=battlecode.Entity.THROWER, team=state.my_team))))
        enemy_neighbors = list(entity.entities_within_adjacent_distance(1, iterator=list(state.get_entities(entity_type=battlecode.Entity.THROWER, team = state.other_team))))

        hitable = list(entity.entities_within_adjacent_distance(7, iterator=list(state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team))))
        obj_thrown = False

        if len(enemy_neighbors) + len(my_neighbors) > 0:
#            print(len(enemy_neighbors) + len(my_neighbors))
            if len(hitable) > 0:
                print(len(hitable))
                if len(enemy_neighbors) > 0:  
                   # print(len(list(hitable)))
                    for statue in hitable:
                        print('Something should be hit.')
                        if is_throw_path_valid(state, entity, statue):
                            # Pick up enemy neighbor if possible
                            for pickup_entity in enemy_neighbors:
                                if entity.can_pickup(pickup_entity):
                                    entity.queue_pickup(pickup_entity)
                                    break
                           
                            # Throw object towards nearest statue
                            direction = entity.location.direction_to(statue.location)
                            if entity.can_throw(direction):
                                entity.queue_throw(direction)
                                obj_thrown = True
                                break

                    if obj_thrown:
                        continue
                elif len(my_neighbors) > 0:   
                    if len(hitable) > 0:
                        for statue in hitable:   
                            if is_throw_path_valid(state, entity, statue):
                                # Pick up enemy neighbor if possible
                                for pickup_entity in my_neighbors:
                                    if entity.can_pickup(pickup_entity):
                                        entity.queue_pickup(pickup_entity)
                                        break
    
                                # Throw object towards nearest statue
                                direction = entity.location.direction_to(statue.location)
                                if entity.can_throw(direction):
                                    entity.queue_throw(direction)
                                    obj_thrown = True
                                    break

                        if obj_thrown:
                            continue

            # Nothing hitable, but enemy neighbors available
            elif len(enemy_neighbors) > 0:
                nearest_statue = nearest_enemy_glass_state_in_any_sector(state, entity)
                direction = entity.location.direction_to(nearest_statue.location)
                if entity.can_pickup(enemy_neighbors[0]):
                    entity.queue_pickup(enemy_neighbors[0])
                if entity.can_throw(direction):
                    entity.queue_throw(direction)
                for direction in np.random.permutation(battlecode.Direction.directions()):
                    if entity.can_throw(direction):
                       entity.queue_throw(direction)
                       obj_thrown = True
                       break
                if obj_thrown:
                    continue

        else:
            # No objects thrown, move towards nearest enemy statue
            nearest_statue = nearest_enemy_glass_state_in_any_sector(state, entity)
            if nearest_statue is None:
                break
            towards_enemy = entity.location.direction_to(nearest_statue.location)
            if entity.can_move(towards_enemy):
                entity.queue_move(towards_enemy)
            else:
               for direction in np.random.permutation(battlecode.Direction.directions()):
                   if entity.can_move(direction):
                       entity.queue_move(direction)

end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
