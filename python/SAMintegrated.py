import battlecode
import time
import random
import numpy as np

#Start a game
game = battlecode.Game('SAMintegrated')
start = time.clock()

DEBUG_FLAG = False

##################################
#                                #
#        HELPER FUNCTIONS        #
#                                #
##################################

def nearest_my_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = np.inf
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.my_team):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist < nearest_dist):
            nearest_dist = dist
            nearest_statue = other_entity

    return nearest_statue

def nearest_enemy_glass_state_in_oppsector(state, entity):
    nearest_statue = None
    nearest_dist = np.inf
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team):
        if entity == other_entity:
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if state.map.sector_at(other_entity.location).team == state.other_team and dist < nearest_dist:
            nearest_dist = dist
            nearest_statue = other_entity

    return nearest_statue

def nearest_enemy_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = np.inf
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team):
        if entity == other_entity:
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_statue = other_entity

    return nearest_statue

def farthest_enemy_glass_state(state, entity):
    farthest_statue = None
    farthest_dist = 0
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist > farthest_dist):
            farthest_dist = dist
            farthest_statue = other_entity

    return farthest_statue

def is_small_map(state):
    return state.map.height <= 10 or state.map.width <= 10

def get_entity_sector(entity):
    return(int(entity.location.x/5), int(entity.location.y/5))

def get_unoccupied_sectors(state):
    """
    Returns list of sectors which do not have one of our towers in it.
    """
    sectors_they_own = 0

    unoccupied_sectors = [state.map._sectors[k] for k in state.map._sectors]
    total_num_sectors = len(unoccupied_sectors)
    our_glass_statues = state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.my_team)
    their_glass_statues = state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team)
    for statue in our_glass_statues:
        sector = state.map.sector_at(statue.location)
        if sector in unoccupied_sectors:
            unoccupied_sectors.remove(sector)
    for statue in their_glass_statues:
        sector = state.map.sector_at(statue.location)
        if sector in unoccupied_sectors:
            sectors_they_own += 1
    return unoccupied_sectors, 1 - len(unoccupied_sectors) / total_num_sectors, sectors_they_own / total_num_sectors

def get_closest_cell(map, my_location, sector):
    min_x = sector.top_left.x
    max_x = min_x + map.sector_size - 1
    min_y = sector.top_left.y
    max_y = min_y + map.sector_size - 1

    if my_location.x <= min_x:
        loc_x = min_x
    elif my_location.x >= max_x:
        loc_x = max_x
    else:
        loc_x = my_location.x

    if my_location.y <= min_y:
        loc_y = min_y
    elif my_location.y >= max_y:
        loc_y = max_y
    else:
        loc_y = my_location.y

    return battlecode.Location(loc_x, loc_y)

def distance_to_sector(map, my_location, sector):
    return my_location.distance_to(get_closest_cell(map, my_location, sector))

def move_in_direction(entity, optimal_direction):
    if entity.can_move(optimal_direction):  # can move in optimal direction
        entity.queue_move(optimal_direction)
        return True
    else:  # try other directions at random until one works
        other_directions = battlecode.Direction.directions()
        other_directions.remove(optimal_direction)
        other_directions = np.random.permutation(other_directions)
    for dir in other_directions:
        if entity.can_move(dir):
            entity.queue_move(dir)
            return True
    return False

def print_state_machine_count(turn, state_machine):
    num_colonizing = 0
    num_aggressing = 0
    num_destroying = 0
    num_supporting = 0
    num_standby = 0
    for s in state_machine.values():
        if s == COLONIZING:
            num_colonizing += 1
        elif s == AGGRESSING:
            num_aggressing += 1
        elif s == DESTROYING:
            num_destroying += 1
        elif s == SUPPORTING:
            num_supporting += 1
        else:
            num_standby += 1

    print("STATE at turn", str(turn) + ":", num_colonizing, num_aggressing, num_destroying, num_supporting, num_standby)
    return


def is_throw_path_valid(state, source, target):
    # Checks if the path between source and target is clear of hedges and target is on a throwable trajectory

    direction = source.location.direction_to(target.location)

    dx = target.location.x - source.location.x
    dy = target.location.y - source.location.y

    if (abs(dx) != abs(dy) and dx != 0 and dy != 0):
        return False

    initial = source.location

    for i in range(max(abs(dx), abs(dy))):
        interm_loc = battlecode.Location(initial.x + i * direction.dx, initial.y + i * direction.dy)
        on_map = state.map.location_on_map(interm_loc)
        if (not on_map):
            return False

        is_occupied = len(list(state.get_entities(location=interm_loc, entity_type=battlecode.Entity.HEDGE))) > 0

        if is_occupied:
            return False
    return True

def move_randomly(entity):
    for direction in np.random.permutation(battlecode.Direction.directions()):
        if entity.can_move(direction):
            entity.queue_move(direction)
            break

def move_towards_nearest_enemy_statue(state, entity):
    nearest_statue = nearest_enemy_glass_state(state, entity)
    if nearest_statue is None:
        # Move randomly since no statues left
        for direction in np.random.permutation(battlecode.Direction.directions()):
            if entity.can_move(direction):
                entity.queue_move(direction)
                break
    else:
        # Move towards nearest statue
        towards_enemy = entity.location.direction_to(nearest_statue.location)
        if entity.can_move(towards_enemy):
            entity.queue_move(towards_enemy)
        else:
            # Move randomly
            move_randomly(entity)

def throw_away(state, entity):
    nearest_statue = nearest_enemy_glass_state(state, entity)
    if nearest_statue is None:
        # Throw randomly since no statues left
        move_randomly(entity)
    else:
        # Move towards nearest statue
        towards_enemy = entity.location.direction_to(nearest_statue.location)
        if entity.can_throw(towards_enemy):
            entity.queue_throw(towards_enemy)
        else:
            # Move randomly
            move_randomly(entity)

############################
#                          #
#        STATE CODE        #
#                          #
############################

def initialize_state(state_machine, prop_occupied_sectors, prop_oppteam_sectors):
    colonizing_weight_num = 5
    colonizing_weight_prop_occupied = colonizing_weight_num / 5
    aggressing_weight_num = 3
    aggressing_weight_prop_oppteam = aggressing_weight_num / 1.25
    destroying_weight_prop_oppteam = 0.0001

    num_colonizing = 0
    num_aggressing = 0
    num_destroying = 0
    for s in state_machine.values():
        if s == COLONIZING:
            num_colonizing += 1
        elif s == AGGRESSING:
            num_aggressing += 1
        elif s == DESTROYING:
            num_destroying += 1

    if num_colonizing < MAX_NUM_COLONIZING_EARLY:
        colonizing_factor = colonizing_weight_num * (1 - (num_colonizing / MAX_NUM_COLONIZING_EARLY) ** 2) + \
                            colonizing_weight_prop_occupied * (1 - prop_occupied_sectors)
    else:
        colonizing_factor = 0

    if num_aggressing < MAX_NUM_AGGRESSIVE:
        aggressing_factor = aggressing_weight_num * (1 - (num_aggressing / MAX_NUM_AGGRESSIVE)**0.5) + \
                            aggressing_weight_prop_oppteam * (prop_oppteam_sectors)
    else:
        aggressing_factor = 0
    destroying_factor = destroying_weight_prop_oppteam * (prop_oppteam_sectors + 0.001)
    supporting_factor = 0

    normalization = colonizing_factor + aggressing_factor + destroying_factor + supporting_factor

    prob_distribution = [0] * NUM_STATES
    prob_distribution[COLONIZING] = colonizing_factor / normalization
    prob_distribution[AGGRESSING] = aggressing_factor / normalization
    prob_distribution[DESTROYING] = destroying_factor / normalization
    prob_distribution[SUPPORTING] = supporting_factor / normalization

    return np.random.choice(NUM_STATES, size=1, p=prob_distribution)

def check_transition_mid_game(state_machine, prop_occupied_sectors):
    global game_state

    if game_state == EARLY_GAME:
        if 1 - prop_occupied_sectors < 0.01:
            count_supporting = 0

            for entity_id in state_machine:
                if state_machine[entity_id] == AGGRESSING:
                    state_machine[entity_id] = DESTROYING
                elif state_machine[entity_id] == COLONIZING:
                    if count_supporting < MAX_NUM_COLONIZING_MID:
                        state_machine[entity_id] = SUPPORTING
                        count_supporting += 1
                    else:
                        state_machine[entity_id] = DESTROYING
            game_state = MID_GAME


def do_colonizing(state, entity):
    global unoccupied_sectors, sector_assignments

    my_location = entity.location

    # Check for possibility of building in unowned sector
    for d in np.random.permutation(battlecode.Direction.directions()):
        adj_loc = my_location.adjacent_location_in_direction(d)
        if state.map.location_on_map(adj_loc):
            sector_in_direction = state.map.sector_at(my_location.adjacent_location_in_direction(d))
            if entity.can_build(d) and sector_in_direction in unoccupied_sectors:
                entity.queue_build(d)
                return

    # Initialize max tracking variables
    closest_sector_index = -1
    dist_closest_sector = np.inf

    # Find nearest unfilled sector
    for i in range(len(unoccupied_sectors)):
        s = unoccupied_sectors[i]
        dist_sector = distance_to_sector(state.map, my_location, s)

        if dist_sector < dist_closest_sector and sector_assignments[i] <= cap_assignments:
            closest_sector_index = i
            dist_closest_sector = dist_sector

    # Move toward nearest unfilled sector
    if closest_sector_index != -1:
        target_cell = get_closest_cell(state.map, my_location, unoccupied_sectors[closest_sector_index])
        if my_location != target_cell:
            optimal_direction = my_location.direction_to(target_cell)
        else:
            optimal_direction = battlecode.Direction.directions()[np.random.randint(8)]
        if move_in_direction(entity, optimal_direction):
            sector_assignments[closest_sector_index] += 1

def do_aggression(state, entity):
    global first_aggressor_id, first_target_statue, prop_oppteam_sectors

    if first_aggressor_id is None:
        first_aggressor_id = entity.id
        first_target_statue = farthest_enemy_glass_state(state, entity)

    if entity.id == first_aggressor_id and first_target_statue is not None:
        enemy_statue = first_target_statue
    else:
        enemy_statue = nearest_enemy_glass_state_in_oppsector(state, entity)

    my_location = entity.location

    if prop_oppteam_sectors > 0.01 and enemy_statue is not None:
        # Check for possibility of building in opponent's sector
        for d in np.random.permutation(battlecode.Direction.directions()):
            adj_loc = my_location.adjacent_location_in_direction(d)
            if state.map.location_on_map(adj_loc):
                sector_in_direction = state.map.sector_at(my_location.adjacent_location_in_direction(d))
                if first_aggressor_id == entity.id and sector_in_direction == state.map.sector_at(enemy_statue.location):
                    if entity.can_build(d):
                        entity.queue_build(d)
                        if entity.id == first_aggressor_id:
                            first_target_statue = None
                        return
                elif (first_aggressor_id != entity.id or first_target_statue is None) \
                                and sector_in_direction.team == state.other_team:
                    if entity.can_build(d):
                        entity.queue_build(d)
                        return

        towards_enemy = entity.location.direction_to(enemy_statue.location)
        move_in_direction(entity, towards_enemy)
    else: # transition to new state
        state_machine[entity.id] = COLONIZING
        do_colonizing(state, entity)
        pass

def do_destruction(state, entity):
    my_neighbors = list(entity.entities_within_adjacent_distance(1, iterator=list(
        state.get_entities(entity_type=battlecode.Entity.THROWER, team=state.my_team))))
    enemy_neighbors = list(entity.entities_within_adjacent_distance(1, iterator=list(
        state.get_entities(entity_type=battlecode.Entity.THROWER, team=state.other_team))))

    hitable = list(entity.entities_within_adjacent_distance(7, iterator=list(
        state.get_entities(entity_type=battlecode.Entity.STATUE, team=state.other_team))))
    obj_thrown = False

    if len(hitable) > 0:
        if len(enemy_neighbors) > 0:
            if entity.can_pickup(enemy_neighbors[0]):
                # print('Can pick up enemy neighbor')
                entity.queue_pickup(enemy_neighbors[0])
            for target in hitable:
                if is_throw_path_valid(state, entity, target):
                    direction = entity.location.direction_to(target.location)
                    if entity.can_throw(direction):
                        entity.queue_throw(direction)
                        obj_thrown = True
                        break
            if obj_thrown:
                return
            else:
                move_randomly(entity)
        elif len(my_neighbors) > 0:
            if entity.can_pickup(my_neighbors[0]):
                # print('Can Pickup my neighbor')
                entity.queue_pickup(my_neighbors[0])
            for target in hitable:
                if is_throw_path_valid(state, entity, target):
                    direction = entity.location.direction_to(target.location)
                    if entity.can_throw(direction):
                        entity.queue_throw(direction)
                        obj_thrown = True
                        break
            if obj_thrown:
                return
            else:
                move_randomly(entity)
        else:
            # No neighbors to pick up
            move_towards_nearest_enemy_statue(state, entity)
    else:
        # no hitables, defent yourself (throw neighbors) and move towards nearest statue or move randomly
        if len(enemy_neighbors) > 0:
            for neighbor in enemy_neighbors:
                if entity.can_pickup(enemy_neighbors[0]):
                    # print('Can pick up enemy neighbor')
                    entity.queue_pickup(enemy_neighbors[0])
                    throw_away(state, entity)
                    obj_thrown = True
                    break
            if not obj_thrown:
                move_towards_nearest_enemy_statue(state, entity)
        else:
            move_towards_nearest_enemy_statue(state, entity)

def do_supporting(state, entity):
    global unoccupied_sectors, sector_assignments

    my_location = entity.location

    # Check for possibility of building in unowned sector
    for d in np.random.permutation(battlecode.Direction.directions()):
        adj_loc = my_location.adjacent_location_in_direction(d)
        if state.map.location_on_map(adj_loc):
            sector_in_direction = state.map.sector_at(my_location.adjacent_location_in_direction(d))
            if entity.can_build(d) and sector_in_direction in unoccupied_sectors:
                entity.queue_build(d)
                return

    # Initialize max tracking variables
    closest_sector_index = -1
    dist_closest_sector = np.inf

    # Find nearest unfilled sector
    for i in range(len(unoccupied_sectors)):
        s = unoccupied_sectors[i]
        dist_sector = distance_to_sector(state.map, my_location, s)

        if dist_sector < dist_closest_sector and sector_assignments[i] <= cap_assignments:
            closest_sector_index = i
            dist_closest_sector = dist_sector

    # Move toward nearest unfilled sector
    if closest_sector_index != -1:
        target_cell = get_closest_cell(state.map, my_location, unoccupied_sectors[closest_sector_index])
        optimal_direction = my_location.direction_to(target_cell)
        if move_in_direction(entity, optimal_direction):
            sector_assignments[closest_sector_index] += 1

############################
#                          #
#        ROBOT CODE        #
#                          #
############################

# Global Constants
MAX_NUM_COLONIZING_EARLY = 40
MAX_NUM_COLONIZING_MID = 12
MAX_NUM_AGGRESSIVE = 6
COLONIZING = 0
AGGRESSING = 1
DESTROYING = 2
SUPPORTING = 3
STANDBY = 4
NUM_STATES = STANDBY
EARLY_GAME = 0
MID_GAME = 1

# State Variables
state_machine = {}
exists_unoccupied_sectors = False
game_state = EARLY_GAME
first_aggressor_id = None
first_target_statue = None


for state in game.turns():
    all_entities = list(state.get_entities(team=state.my_team))
    num_entities = len(all_entities)

    # COLONIZING PREPARATION CODE
    num_supporting = sum(1 for s in state_machine.values() if s == COLONIZING)
    unoccupied_sectors, prop_occupied_sectors, prop_oppteam_sectors = get_unoccupied_sectors(state)
    sector_assignments = [0] * len(unoccupied_sectors)
    if len(unoccupied_sectors) > 0:
        cap_assignments = num_supporting // len(unoccupied_sectors)
        exists_unoccupied_sectors = True
    else:
        cap_assignments = 0

    # ITERATE THROUGH ALL ROBOTS
    for entity in all_entities:
        if entity.id not in state_machine: # new robot
            state_machine[entity.id] = initialize_state(state_machine, prop_occupied_sectors, prop_oppteam_sectors)

        if entity.cooldown > 0:
            continue

        if state_machine[entity.id] == COLONIZING:
            if exists_unoccupied_sectors: # exists colonizing work to do
                do_colonizing(state, entity)
        elif state_machine[entity.id] == AGGRESSING:
            do_aggression(state, entity)
        elif state_machine[entity.id] == DESTROYING:
            do_destruction(state, entity)
        elif state_machine[entity.id] == SUPPORTING:
            do_supporting(state, entity)

    check_transition_mid_game(state_machine, prop_occupied_sectors)

    if DEBUG_FLAG:
        print_state_machine_count(state.turn, state_machine)


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
