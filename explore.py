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

# Landmarks
house = foundation.landmarks.get("House")
water = foundation.landmarks.get("Water")
source_block_wood = foundation.landmarks.get("WoodSourceBlock")

[k for k in dir(house) if k[0] != "_"]
env.world.maps
env.get_agent(agent_idx=0).inventory


# Resources
wood = foundation.resources.get("Wood")
wood.name, wood.collectible, wood.color

coin = foundation.resources.get("Coin")
coin.collectible


# Endogenous entities
labor = foundation.endogenous.get("Labor")
[k for k in dir(labor) if k[0] != "_"]

agent0 = env.get_agent(agent_idx=0)
print(agent0.inventory)
print(agent0.endogenous)


# Agents
agent0  = env.get_agent(agent_idx=0)   # Mobile agents are numerically indexed
agent1  = env.get_agent(agent_idx=1)
planner = env.get_agent(agent_idx='p') # The planner agent always uses index 'p'

agent0.state
agent1.state
planner.state


# Components
# = how agents interact with the world
# This is where all the logic is that updates the world and 
# agent objects each step
env_config['components']
env._components

build = env.get_component("Build")
isinstance(build, foundation.components.get("Build"))


from foundation.base.base_component import BaseComponent, component_registry

@component_registry.add
class EmptyComponent(BaseComponent):
    name = "Empty"
    required_entities = []

    def get_n_agent_actions(self, agent_cls_name):
        """Returns the actions that agents with type agent_cls_name can take through this component."""
        pass

    def get_additional_state_fields(self, agent_cls_name):
        """Returns a dictionary to be be added to the state dictionary of agents with type agent_cls_name."""
        pass

    def component_step(self):
        """Implements the (passive and active) dynamics that this Component adds to the environment."""
        pass

    def generate_observations(self):
        """Yields observations."""
        pass

    def generate_masks(self):
        """Specifies which of the Component actions are valid given the current state."""
        pass



agent0.action_dim
planner.action_dim




## EXERCISE
## Create buy new widget from virtual store component
# remeber components are what actually do the updating to agents and world.maps


# Step 1: add a resource 'Widget'
from ai_economist.foundation.entities.resources import Resource, resource_registry

@resource_registry.add
class Widget(Resource):
    name = "Widget"
    color = [1, 1, 1]
    collectible = False # <--- Goes in agent inventory, but not in the world


# Step 2: Add the component
# This component interacts with two resources: coin and widgets
@component_registry.add
class BuyWidgetFromVirtualStore(BaseComponent):
    name = "BuyWidgetFromVirtualStore"
    required_entities = ["Coin", "Widget"]  # <--- We can now look up "Widget" in the resource registry
    agent_subclasses = ["BasicMobileAgent"]

    def __init__(
        self,
        *base_component_args,
        widget_refresh_rate=0.1,
        **base_component_kwargs
    ):
        super().__init__(*base_component_args, **base_component_kwargs)
        self.widget_refresh_rate = widget_refresh_rate
        self.available_widget_units = 0
        self.widget_price = 5

    def get_additional_state_fields(self, agent_cls_name):
        return {}

    def additional_reset_steps(self):
        self.available_wood_units = 0

    def get_n_actions(self, agent_cls_name):
        # This component adds 1 binary action that mobile agents can take: buy widget (or not).
        if agent_cls_name == "BasicMobileAgent":
            return 1  # Buy or not.
    
        return None

    def generate_masks(self, completions=0):
        masks = {}
        # Mobile agents' buy action is masked if they cannot build with their
        # current coin or if no widgets are available.
        for agent in self.world.agents:
            masks[agent.idx] = np.array([
                agent.state["inventory"]["Coin"] >= self.widget_price and self.available_widget_units > 0
            ])
    
        return masks
    
    
    def component_step(self):
        # Maybe add a Widget to store's inventory.
        if random.random() < self.widget_refresh_rate: 
            self.available_widget_units += 1
    
        # Agents can buy 1 unit of Wood, in random order.
        for agent in self.world.get_random_order_agents():
    
            action = agent.get_component_action(self.name)
    
            if action == 0: # NO-OP. Agent is not interacting with this component.
                continue
    
            if action == 1: # Agent wants to buy. Execute a purchase if possible.
                if self.available_widget_units > 0 and agent.state["inventory"]["Coin"] >= self.widget_price: 
                    # Remove the purchase price from the agent's inventory
                    agent.state["inventory"]["Coin"] -= self.widget_price
                    # Add a Widget to the agent's inventory
                    agent.state["inventory"]["Widget"] += 1
                    # Remove the Widget from the market
                    self.available_widget_units -= 1
    
            else: # We only declared 1 action for this agent type, so action > 1 is an error.
                raise ValueError
    
    def generate_observations(self):
        obs_dict = dict()
        for agent in self.world.agents:
            obs_dict[agent.idx] = {
                "widget_refresh_rate": self.widget_refresh_rate,
                "available_widget_units": self.available_widget_units,
                "widget_price": self.widget_price
            }
    
        return obs_dict    
        
    








