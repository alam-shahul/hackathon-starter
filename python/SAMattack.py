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

def nearest_enemy_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team):
        if(entity == other_entity or state.map.sector_at(other_entity.location).team != state.other_team):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist< nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def is_small_map(state):
    return state.map.height <= 10 or state.map.width <= 10

""" Don't use this; use sector_at
def get_entity_sector(entity):
    return(entity.location.x // 5, entity.location.y // 5)
"""

"""
Attack code below
"""
   
for state in game.turns():
    # Your Code will run within this loop
#    print(len(list(state.get_entities(team=state.my_team))))
    
    for entity in state.get_entities(team=state.my_team):
        if entity.cooldown != 0:
            continue

        enemy_statue = nearest_enemy_glass_state(state, entity)
        my_statue = nearest_my_glass_state(state, entity)
        
        done = False

        for direction in np.random.permutation(battlecode.Direction.directions()):
           if(state.map.location_on_map(entity.location.adjacent_location_in_direction(direction))):
               if state.map.sector_at(entity.location.adjacent_location_in_direction(direction)).team == state.other_team:
                   if entity.can_build(direction):
                        entity.queue_build(direction)
                        done = True
        if(done):
            continue

        if enemy_statue != None:
            towards_enemy= entity.location.direction_to(enemy_statue.location)
            if state.map.sector_at(enemy_statue.location) != state.map.sector_at(entity.location):
                if entity.can_move(towards_enemy):
                    entity.queue_move(towards_enemy)
                else: 
                   for direction in np.random.permutation(battlecode.Direction.directions()):
                       if entity.can_move(direction):
                           entity.queue_move(direction)
            else:
                if entity.can_build(towards_enemy):
                    entity.queue_build(towards_enemy)
                else:
                   for direction in np.random.permutation(battlecode.Direction.directions()):
                       if entity.can_build(direction):
                           entity.queue_build(direction)
        else:
            if state.map.sector_at(entity.location).team != state.my_team:
               for direction in np.random.permutation(battlecode.Direction.directions()):
                   if entity.can_build(direction):
                       entity.queue_build(direction)
#            if my_statue != None:
#                towards_my= entity.location.direction_to(my_statue.location)
#                if state.map.sector_at(my_statue.location) != state.map.sector_at(entity.location):
#                    if entity.can_build(towards_my):
#                        entity.queue_build(towards_my)
#                    else:
#                       for direction in np.random.permutation(battlecode.Direction.directions()):
#                           if entity.can_build(direction):
#                               entity.queue_build(direction)
            
            else:
                for direction in np.random.permutation(battlecode.Direction.directions()):
                    if entity.can_move(direction):
                        entity.queue_move(direction)
    
end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
