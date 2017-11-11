import battlecode
import time
import random
import numpy as np

#Start a game
game = battlecode.Game('SAMplayer')

start = time.clock()

#define helper functions here
def nearest_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist< nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def get_entity_sector(state, entity):
    standard_size= (state.map.width/5, state.map.height/5)
    return(int(entity.location.x/5), int(entity.location.y/5))

for state in game.turns():
    # Your Code will run within this loop
#    print(len(list(state.get_entities(team=state.my_team))))
    for entity in state.get_entities(team=state.my_team):
        # Get nearest glass statue
        nearstat = nearest_glass_state(state, entity)
        # This line gets all the bots on your team
#        print(get_entity_sector(state, entity))
        # Try to build statue every 50th turn (every 100th turn overall)
        if(state.turn % 50 == 0 or (state.turn + 1) % 50 == 0 and True):
            for direction in np.random.permutation(battlecode.Direction.directions()):
                # Check if you can build in the selected direction
                if entity.can_build(direction):
                    # Check if glass statue exists
                    if(nearstat != None):
                        print('Testing nearstat')
                        # Check if nearest glass statue is in same sector as entity
                        if(get_entity_sector(state, nearstat) != get_entity_sector(state, entity)):
#                    print('SAMplayer should be building.')
                            
                            entity.queue_build(direction)

        my_location = entity.location
        near_entities = entity.entities_within_euclidean_distance(1.9)
        near_entities = list(filter(lambda x: x.can_be_picked, near_entities))

        for pickup_entity in near_entities:
            assert entity.location.is_adjacent(pickup_entity.location)
            if entity.can_pickup(pickup_entity):
                entity.queue_pickup(pickup_entity)

        statue = nearest_glass_state(state, entity)
        if(statue != None and statue.team != state.my_team):
            direction = entity.location.direction_to(statue.location)
            if entity.can_throw(direction):
                print('thrown!')
                entity.queue_throw(direction)

        for direction in np.random.permutation(battlecode.Direction.directions()):
            if entity.can_move(direction):
                entity.queue_move(direction)

end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
