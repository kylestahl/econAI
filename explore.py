#! pip install ai-economist


from ai_economist import foundation
from ai_economist.foundation.base.base_env import BaseEnvironment, scenario_registry

test_env_cls = scenario_registry.get("layout_from_file/simple_wood_and_stone")
test_env_cls.name


@scenario_registry.add
class NewEnvironment(BaseEnvironment):
    name = "NewEnvironment"

new_env_cls = scenario_registry.get("NewEnvironment")
new_env_cls.name


# These are the Scenario classes registered in scenario_registry
print(scenario_registry.entries)

# Scenarios:
print(foundation.scenarios.entries)

# Entities (landmarks, resources, endogenous):
print(foundation.landmarks.entries)
print(foundation.resources.entries)
print(foundation.endogenous.entries)

# Agents:
print(foundation.agents.entries)

# Components:
print(foundation.components.entries)




# Define the configuration of the environment that will be built

env_config = {
    # ===== STANDARD ARGUMENTS ======
    'n_agents': 4,          # Number of non-planner agents
    'world_size': [15, 15], # [Height, Width] of the env world
    'episode_length': 1000, # Number of timesteps per episode
    
    # In multi-action-mode, the policy selects an action for each action subspace (defined in component code)
    # Otherwise, the policy selects only 1 action
    'multi_action_mode_agents': False,
    'multi_action_mode_planner': True,
    
    # When flattening observations, concatenate scalar & vector observations before output
    # Otherwise, return observations with minimal processing
    'flatten_observations': False,
    # When Flattening masks, concatenate each action subspace mask into a single array
    # Note: flatten_masks = True is recommended for masking action logits
    'flatten_masks': True,
    
    
    # ===== COMPONENTS =====
    # Which components to use (specified as list of {"component_name": {component_kwargs}} dictionaries)
    #   "component_name" refers to the component class's name in the Component Registry
    #   {component_kwargs} is a dictionary of kwargs passed to the component class
    # The order in which components reset, step, and generate obs follows their listed order below
    'components': [
        # (1) Building houses
        {'Build': {}},
        # (2) Trading collectible resources
        {'ContinuousDoubleAuction': {'max_num_orders': 5}},
        # (3) Movement and resource collection
        {'Gather': {}},
    ],
    
    # ===== SCENARIO =====
    # Which scenario class to use (specified by the class's name in the Scenario Registry)
    'scenario_name': 'uniform/simple_wood_and_stone',
    
    # (optional) kwargs of the chosen scenario class
    'starting_agent_coin': 10,
    'starting_stone_coverage': 0.10,
    'starting_wood_coverage':  0.10,
}



env = foundation.make_env_instance(**env_config)
obs = env.reset()

uniform_cls = scenario_registry.get(env_config['scenario_name'])
isinstance(env, uniform_cls)
isinstance(env, BaseEnvironment)

@scenario_registry.add
class EmptyScenario(BaseEnvironment):
    name = "Empty"
    required_entities = []

    def reset_layout(self):
        """Resets the state of the world object (self.world)."""
        pass

    def reset_agent_states(self):
        """Resets the state of the agent objects (self.world.agents & self.world.planner)."""
        pass

    def scenario_step(self):
        """Implements the passive dynamics of the environment."""
        pass

    def generate_observations(self):
        """Yields some basic observations about the world/agent states."""
        pass

    def compute_reward(self):
        """Determines the reward each agent receives at the end of each timestep."""
        pass



# For each key, the maps object has a [Height, Width] array for the 
# spatial layout of that Entity in the world.
env.world.maps.keys()

# Note: this map has the same size as our world (15 by 15)
env.world.maps.get("Stone")

env.world.location_resources(0, 0)
env.world.location_landmarks(0, 0)


house = foundation.landmarks.get("House")
water = foundation.landmarks.get("Water")
source_block_wood = foundation.landmarks.get("WoodSourceBlock")


env.world.maps










