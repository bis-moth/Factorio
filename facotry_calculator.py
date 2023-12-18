import json
import yaml
import argparse
import math

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



def sort_dict_alphabetically(dictionary):
    sorted_dict = dict(sorted(dictionary.items(), key=lambda item: (not item[0].isdigit(), item[0])))
    return sorted_dict



def merge_dictionaries(dict1, dict2):
    merged_dict = {}

    # Iterate over keys in dict1
    for key, value in dict1.items():
        # Sum values for identical keys
        merged_dict[key] = merged_dict.get(key, 0) + value

    # Iterate over keys in dict2
    for key, value in dict2.items():
        # Sum values for identical keys
        merged_dict[key] = merged_dict.get(key, 0) + value

    return merged_dict



def is_raw(item):
    if item in items:
        return(False)
    else:
        return(True)



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
def list_raw():
    LIST_OF_RAW_MATERIALS_WITH_DUPLICATES = []
    for item in items:
        for ingredient in get_ingredients(item):
            if is_raw(ingredient): 
                LIST_OF_RAW_MATERIALS_WITH_DUPLICATES.append(ingredient)
    LIST_OF_RAW_MATERIALS = list(set(LIST_OF_RAW_MATERIALS_WITH_DUPLICATES))
    print(LIST_OF_RAW_MATERIALS)



def get_crafting_time(item):

    try:
        if 'energy' in items[item]: # check that the item lists the 'energy'
            return(items[item]['energy'])
        else:
            return(1)

    except: # if no energy is listed
        print(f"No 'energy' key found in the JSON data for {item}.")
        return(1)



def get_output_quantity(item):
    """
    Extract the nuber of output items produced by a specified item's recipe

    Parameters:
    - item (string): The name of the item of interest.

    Returns:
    - output_quantity (int): the quantity of itmes produced by the item's recipe  
    """
    if is_raw(item):
        return(1)
    else:
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
    - 
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



def convert_rate_to_factories(item, rate):
    return rate*get_crafting_time(item)*get_output_quantity(item)



def convert_factories_to_rate(item, factories):
    return factories/get_crafting_time(item)/get_output_quantity(item)



def ratio(item, output_factories=None, output_rate=None):
    # Only allow one of the two optional inputs to be specified
    if bool(output_factories) and bool(output_rate):
        raise ValueError("Provide only 'output_factories' or 'output_rate', not both.")
    
    if is_raw(item):
        if bool(output_factories):
            return({item: output_factories})
        elif bool(output_rate):
            return({item: output_rate})
        else:
            return({item: 1})
    
    else:
        # Determine the number of output factories and output rate
        if not bool(output_factories) and not bool(output_rate): 
            output_factories = 1
            output_rate = convert_factories_to_rate(item, output_factories)
        elif not bool(output_rate): 
            output_rate = convert_factories_to_rate(item, output_factories)
        else:
            output_factories = convert_rate_to_factories(item, output_factories)
        
        # Determine the number of input factories required for each item in the recipe
        recipe = get_recipe(item)
        input_factories_required = {}
        for ingredient in recipe:
            input_factories_required[ingredient] = recipe[ingredient]*output_rate*get_crafting_time(ingredient)/get_output_quantity(ingredient)
        return(input_factories_required)



def calculate_facotry(item, output_factories=None, output_rate=None):
    if not output_factories:
        output_factories = convert_rate_to_factories(item, output_rate)
    factory = {item: output_factories}

        
    if not is_raw(item):
        current_item_ratio = ratio(item, output_factories)
        for ingredient in current_item_ratio:
            factory = merge_dictionaries(factory, calculate_facotry(ingredient, current_item_ratio[ingredient]))
    
    return(factory)
    


def main():
    parser = argparse.ArgumentParser(description="Example script with functions and required inputs.")
    parser.add_argument("function_name", choices=["raw", "raw_materials", "ratio", "factory", "calcualte_factory", "recipe", "get_recipe", "parameter"], help="Name of the function to execute.")
    parser.add_argument("--item", type=str, help="Required argument for all functions")
    parser.add_argument("--output_factories", type=float, help="Optional argument 2 for calculator functions.  Cannot be used in conjuction with --output_rate.")
    parser.add_argument("--output_rate", type=float, help="Alternative argument 2 for calculator functions.  Cannot be used in conjuction with --output_factories.")
    parser.add_argument("--parameter", type=float, help="Optional argument for 'get_parameter' function to retrieve only the specified parameter data for the specified item.")
    parser.add_argument("--decimals", type=int, default=3, help="Optional argument to specify the number of decimal places to use when displaying calculator outputs.")

    args = parser.parse_args()

    if args.function_name == "ratio":
        item_ratio = ratio(args.item, args.output_factories, args.output_rate)
        for item in item_ratio: print(f"{item}: {item_ratio[item]}")
    
    elif args.function_name in ["factory", "calcualte_factory"]:
        print("WIP")
        factory = calculate_facotry(args.item, args.output_factories, args.output_rate)
        factory = sort_dict_alphabetically(factory)
        print("RAW MATERIALS:")
        for item in factory: 
            if is_raw(item):
                print(f"{item}")

        print("INTERMEDIATE MATERIALS:")
        for item in factory: 
            if not is_raw(item):
                print(f"{item}: {round(factory[item],args.decimals)}")
    
    elif args.function_name in ["recipe", "get_recipe"]:
        recipe = get_recipe(args.item)
        for ingredient in recipe: print(f"{ingredient}: {recipe[ingredient]}") 
    
    elif args.function_name in ["paramter", "get_parameter"]:
        print(get_item_parameter(args.item, args.parameter))
    
    elif args.function_name in ["raw", "raw_materials"]:
        list_raw()



if __name__ == "__main__":
    main()