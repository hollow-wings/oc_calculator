import matplotlib.pyplot as plt
import math

# Constants (global scope for better organization if used across functions)
IS_EBF = True
# TOTAL POWER MACHINE HAS AVAILABLE
MACHINE_POWER = 2048
RECIPE_TIME = 60
ENERGY_COST = 480
# MULTIBLOCK SPECIFIC ENERGY DISCOUNT
ENERGY_DISCOUNT = 0.9
# MULTIBLOCK SPECIFIC SPEED BOOST
SPEED_BOOST = 120
# MULTIBLOCK MAX PARALLELS (DEPENDING ON THE MULTI THIS MIGHT NEED TO ALSO BE CALCULATED INSTEAD OF A FLAT AMOUNT)
MAX_PARALLELS = 8
# CURRENT COIL HEAT CAPACITY 
COIL_HEAT = 9901
# MINIMUM EBF RECIPE HEAT REQUIREMENT
RECIPE_HEAT = 2054


def oc_calculator(batch_size):
    """
    Calculates the recipes per second based on the batch size and overclock parameters.

    Args:
        batch_size (int): The size of the batch.

    Returns:
        float: Recipes per second.
    """
    # Initialize variables
    number_of_overclocks = 0
    extra_perfect_ocs = 0
    final_parallels = 0
    perfect_oc = False
    effective_energy_discount = ENERGY_DISCOUNT

    # Batch size doesn't matter past machine parallels unless you are using batch mode
    if batch_size > MAX_PARALLELS:
        batch_size = MAX_PARALLELS

    # Calculate machine and recipe tiers
    recipe_tier = max(0, math.ceil(math.log(ENERGY_COST / 32) / math.log(4))) + 1
    machine_tier = max(0, math.ceil(math.log(MACHINE_POWER / 32) / math.log(4))) + 1
    maximum_overclocks = machine_tier - recipe_tier

    # EBF adjustments
    if IS_EBF:
        effective_coil_heat = COIL_HEAT + 100 * max(0, machine_tier - 2)
        effective_energy_discount *= 0.95 ** math.floor((effective_coil_heat - RECIPE_HEAT) / 900)
        extra_perfect_ocs = math.floor((effective_coil_heat - RECIPE_HEAT) / 1800)
        if extra_perfect_ocs >= maximum_overclocks:
            perfect_oc = True

    # Adjust batch size and parallels
    max_parallels = min(MAX_PARALLELS, batch_size)
    lowered_parallels = max_parallels

    # Calculate energy and recipe time
    real_energy_cost = ENERGY_COST * effective_energy_discount
    total_eu_per_tick = real_energy_cost * max_parallels
    new_recipe_time = RECIPE_TIME * (100 / (SPEED_BOOST + 100))
    print(new_recipe_time)

    # Check if energy is within machine power limits
    if total_eu_per_tick <= MACHINE_POWER:
        while total_eu_per_tick <= MACHINE_POWER:
            total_eu_per_tick *= 4
            if total_eu_per_tick <= MACHINE_POWER:
                number_of_overclocks += 1

        # Limit overclocks to maximum allowable
        number_of_overclocks = min(number_of_overclocks, maximum_overclocks)
        final_parallels = max_parallels
        final_recipe_time = new_recipe_time

        # Adjust recipe time based on overclocks
        for _ in range(number_of_overclocks):
            print(final_recipe_time)
            if perfect_oc or extra_perfect_ocs > 0:
                final_recipe_time = round(final_recipe_time / 4, 1)
                extra_perfect_ocs -= 1
            else:
                final_recipe_time = round(final_recipe_time / 2, 1)
    else:
        # Adjust parallels if energy exceeds machine power
        while total_eu_per_tick > MACHINE_POWER:
            lowered_parallels -= 1
            total_eu_per_tick -= real_energy_cost
        final_parallels = lowered_parallels
        final_recipe_time = new_recipe_time

    # Calculate and print the result
    recipes_per_second = final_parallels/final_recipe_time
    print(f"Batch size: {batch_size}, Recipes per second: {recipes_per_second:.2f}")
    return recipes_per_second


def oc_graph():
    """
    Generates and displays a graph showing recipes per second for relevant batch sizes.
    """
    # Generate data for the graph
    # Remember that batch size means amount of recipes you are running not amount of items you are running
    x_axis = list(range(1, MAX_PARALLELS+1))
    y_axis = [oc_calculator(batch_size) for batch_size in x_axis]
    if 1/max(y_axis) * y_axis.index(max(y_axis)) + 1 > 6.4:
        print(f"Optimal batch size to saturate batch mode: {y_axis.index(max(y_axis)) + 1}")
    else:
        print(f"Optimal batch size to saturate batch mode: {math.floor(6.4/(1/max(y_axis)))}")

    # Plot the graph
    plt.plot(x_axis, y_axis, marker='o')
    plt.xlabel('Batch Size')
    plt.ylabel('Recipes per Second')
    plt.title('GTNH Batch Size Calculator')
    plt.grid(True)
    plt.show()


# Execute the graph generation
if __name__ == "__main__":
    oc_graph()
