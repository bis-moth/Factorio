import json
import yaml
import argparse
import sys

raw_material_identifier = ""

# Opening JSON file
recipe_file = open('recipe.json')
# returns JSON object as a dictionary
items = json.load(recipe_file)


# Specify the path to your YAML file
yaml_file_path = 'config.yaml'
# Load YAML config data
with open(yaml_file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)
# Extract the value associated with the key 'raw_material_identifier'
raw_material_identifier = yaml_data['raw_material_identifier']

def has_recipe(item):
    if item in items:
        return(True)
    else:
        return(False)


def get_ingredients(item):
    list_of_ingredients = []

    if 'ingredients' in items[item]: # check that the item lists the 'ingredients'
        ingredients = items[item]['ingredients'] # extract the ingredients data
        
        # add all the ingredients and the amount required for each to the recipie dictionary
        for ingredient in ingredients: 
            list_of_ingredients.append(ingredient['name'])

    else: # if no ingredients are listed
        print(f"No 'ingredients' key found in the JSON data for {item}.")

    return(list_of_ingredients)


# Generate a list of all raw materials
LIST_OF_RAW_MATERIALS = []
for item in items:
    for ingredient in get_ingredients(item):
        if not has_recipe(ingredient): 
            LIST_OF_RAW_MATERIALS.append(ingredient)
LIST_OF_RAW_MATERIALS = list(set(LIST_OF_RAW_MATERIALS))



def get_crafting_time(item):
    try:
        if 'energy' in items[item]: # check that the item lists the 'energy'
            return(items[item]['energy'])
        else:
            return(0.5)

    except: # if no energy is listed
        print(f"No 'energy' key found in the JSON data for {item}.")
        return(0.5)


def get_output_quantity(item):
    """
    Extract the nuber of output items produced by a specified item's recipe

    Parameters:
    - item (string): The name of the item of interest.

    Returns:
    - int: the quantity of output itmes produced by the item's recipe  
    """
    output_quantity = get_item_parameter(item, 'main_product')['amount']
    return(output_quantity)

def get_recipe(item):
    """
    Extract the recipe for a specified item

    Parameters:
    - item (string): The name of the item of interest.

    Returns:
    - dict: A dictionary containing the required items and their required quantities.
        {ingredient(string):amount(int), ...}
    """

    # initialize the recipie as a dictionary and extract the ingredients data
    recipe = {} 
    ingredients = get_item_parameter(item, 'ingredients') 
    
    # add all the ingredients and the amount required for each to the recipie dictionary
    for ingredient in ingredients: 
        recipe.update({ingredient['name']:ingredient['amount']})

    return(recipe)



def get_item_parameter(item, parameter):
    """
    Extract a parameter for a specified item

    Parameters:
    - item (string): The name of the item for which you wish to know the recipe.
    - parameter (string): The name of the parameter you whish to extract.  This must be present at the 2nd level in the "recipe.json" file.

    Returns:
    - dict: A dictionary containing the required items and their required quantities.
        {ingredient(string):amount(int), ...}
    """
    data = None
    # Check that the item and parameter exist
    if item in items: 
        try:
            if parameter in items[item]:
                data = items[item][parameter]
        except: 
            print(f"No '{parameter}' key found in JSON data for {item}.")
    else:
        print(f"No item '{item}' found in JSON data.")
        
    return(data)



def ratio(item, output_factories=None, output_rate=None):
    # Only allow one of the two optional inputs to be specified
    if bool(output_factories) and bool(output_rate):
        raise ValueError("Provide only 'output_factories' or 'output_rate', not both.")
    
    # Determine the number of output factories required if not already specified
    if not bool(output_factories): output_factories = 1
    if not bool(output_rate): 
        output_rate = output_factories/get_crafting_time(item)/get_output_quantity(item)
    
    # Calculate the number of factories required for each item in the recipe
    recipe = get_recipe(item)
    input_factories_required = [[item, recipe[item]*output_rate*get_crafting_time(item)/get_output_quantity(item)] for item in recipe]
    return([item, output_factories], input_factories_required)
    



if __name__ == "__main__":
    def main():
        parser = argparse.ArgumentParser(description="Example script with functions and required inputs.")
        parser.add_argument("function_name", choices=["ratio", "recipe", "get_recipe"], help="Name of the function to execute.")
        parser.add_argument("--item", type=str, help="Required argument for all functions")
        parser.add_argument("--output_factories", type=float, help="Optional argument 2 for calculator functions.  Cannot be used in conjuction with --output_rate.")
        parser.add_argument("--output_rate", type=float, help="Alternative argument 2 for calculator functions.  Cannot be used in conjuction with --output_factories.")
        parser.add_argument("--parameter", type=float, help="Optional argument for 'get_parameter' function to retrieve only the specified parameter data for the specified item.")

        args = parser.parse_args()

        if args.function_name == "ratio":
            item_ratio = ratio(args.item, args.output_factories, args.output_rate)
            for element in item_ratio: print(element)
        elif args.function_name == "recipe" or "get_recipe":
            recipe = get_recipe(args.item)
            for ingredient in recipe: print(f"{ingredient}: {recipe[ingredient]}") 
        elif args.function_name == "paramter" or "get_parameter":
            print(get_item_parameter(args.item, args.parameter))

if __name__ == "__main__":
    main()