import battlecode
import time
import random
import numpy as np

#Start a game
game = battlecode.Game('MilesTest')

start = time.clock()

#define helper functions here and global variables
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

def get_entity_sector(entity):
    return(entity.location.x // 5, entity.location.y // 5)

def is_throw_path_valid(state, source, target):
    # Checks if the path between source and target is clear of hedges and target is on a throwable trajectory
    dx = target.location.x - source.location.x
    dy = target.location.y - source.location.y

    if not(abs(dx) == abs(dy) or dx == 0 or dy == 0):
        return False
        
    if abs(dx) == abs(dy):
        # aligned along diagonal
        for i in range(dx):
            obstacles = list(state.get_entities(location = battlecode.Location(source.location.x + i + 1, source.location.y + i + 1)))
            if len(obstacles) > 0 and obstacles[0].type == battlecode.Entity.HEDGE:
                return False
        return True

    if dx == 0:
        # aligned along diagonal
        for i in range(dx):
            obstacles = list(state.get_entities(location = battlecode.Location(source.location.x, source.location.y + i + 1)))
            if len(obstacles) > 0 and obstacles[0].type == battlecode.Entity.HEDGE:
                return False
        return True

    if dy == 0:
        # aligned along diagonal
        for i in range(dx):
            obstacles = list(state.get_entities(location = battlecode.Location(source.location.x + i + 1, source.location.y)))
            if len(obstacles) > 0 and obstacles[0].type == battlecode.Entity.HEDGE:
                return False
        return True

for state in game.turns():
    # Your Code will run within this loop
    for entity in state.get_entities(team=state.my_team):
        # Seek out opposing statue and destroy

        if entity.cooldown != 0:
            continue

        # for direction in np.random.permutation(battlecode.Direction.directions()):
        #     if entity.can_throw(direction):
        #         entity.queue_throw(direction)
        #         break
        
        obj_thrown = False
        for direction in battlecode.Direction.directions():
            loc = entity.location.adjacent_location_in_direction(direction)
            if(state.map.location_on_map(loc)):
                neighbor = list(state.get_entities(location=loc, team=state.other_team))
                if len(neighbor) > 0:
                    if entity.can_pickup(neighbor[0]):
                        entity.queue_pickup(neighbor[0])
                        nearest_statue = nearest_enemy_glass_state_in_any_sector(state, entity)
                        if nearest_statue is not None:
                            direction = entity.location.direction_to(nearest_statue.location)
                            if entity.can_throw(direction):
                                entity.queue_throw(direction)
                                obj_thrown = True
                                break
                        for direction in np.random.permutation(battlecode.Direction.directions()):
                            if entity.can_throw(direction):
                                entity.queue_throw(direction)
                                obj_thrown = True
                                break
        if obj_thrown:
            break

        # If within 7 units of statue and on a straight path, pick up item and throw
        hitable = entity.entities_within_adjacent_distance(7, iterator=list(state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team)))
        obj_thrown = False
        for statue in hitable:
            if is_throw_path_valid(state, entity, statue):
                # Find all throwable objects adjacent to me
                my_location = entity.location
                near_entites = entity.entities_within_euclidean_distance(1.9)
                near_entites = list(filter(lambda x: x.can_be_picked, near_entites))
                for pickup_entity in near_entites:
                    assert entity.location.is_adjacent(pickup_entity.location)
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
