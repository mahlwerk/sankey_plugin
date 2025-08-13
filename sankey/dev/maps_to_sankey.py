# turning attribute columns from a qgis database into a sankey diagramm
# based on: https://plotly.com/python/sankey-diagram/

import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_csv('C:/Users/ba2fc6/Documents/python/sankey/map_data.csv')

df.head()

colour_scheme = {
    "Totalschaden alt": "rgb(255, 0, 0)", #red
    "Totalschaden neu": "rgb(255, 0, 0)",
    "schwerer Schaden neu": "rgb(0, 0, 255)", #blue
    "schwerer Schaden alt": "rgb(0, 0, 255)",
    "nicht kartiert": "rgb(200, 200, 200)",
    "total beschädigt":"rgb(255, 200, 70)", #yellow
    "Mauerteile, die einzustürzen drohen": "rgb(255, 200, 70)",
    "augebrannt, Außenmauerteile schwer beschädigt":"rgb(255, 200, 70)",
    "ausgebrannt, Außenmauerteile leicht beschädigt": "rgb(255, 200, 70)",
    "schwer beschädigt, aber Außenmauerteile noch gut erhalten": "rgb(255, 200, 70)",
    "schwer beschädigt": "rgb(255, 200, 70)",
    "unbeschädigt": "rgb(255, 200, 70)",
    "leicht oder mittel beschädigt": "rgb(255, 200, 70)"    
}

# add names of attributes (maps) that you mean to compare
map_1 = "Schad_X208"
map_2 = "Schad_2469"

# combine values from attributes(maps) with a ':' as delimiter
df["combo1"] = df[map_1] + ":" + df[map_2]

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# functions for sankey diagramm input
def create_label_list(col1, col2):
    categories_1 = list(dict.fromkeys(col1))
    categories_2 = list(dict.fromkeys(col2))
    label_list = []
    for value in categories_1:
        try:
            categories_2.index(value)
        except:
            value
        else:
            value = value + '_1'
        label_list.append(value)
    for value in categories_2:
        try:
            categories_1.index(value)
        except:
            value
        else:
            value = value + '_2'
        label_list.append(value)
    print(label_list)
    return label_list

def random_colour_generator():
    colour = []
    c = 0
    while c < 3:
        value = np.random.randint(0, 256, size = 1)
        colour.append(str(value[0]))
        print(value[0])
        c += 1
    numbers = ",".join(colour)
    rgb = "rgba(" + numbers + ",0.8)"
    return rgb

def create_colour_list(label_list):
    # get colours from colour dict, to reflect map legend
    colour_list = []
    for category in label_list:
        colour_list.append(random_colour_generator())
    return colour_list


def create_source_list(combo_dict, label_list):
    source_list = []
    for value in combo_dict:
        # get the first catgeory of the pair and find it's index in the label list
        category = value.split(":")[0]
        try:
            source_list.append(label_list.index(category))
        except:
            source_list.append(label_list.index(category + "_1"))

    return source_list

def create_target_list(combo_dict, label_list):
    target_list = []
    for value in combo_dict:
        # get the second catgeory of the pair and find it's index in the label list
        category = value.split(":")[1]
        try:
            target_list.append(label_list.index(category))
        except:
            target_list.append(label_list.index(category + "_2"))
    return target_list

def create_value_list(combo_dict):
    value_list = []
    for value in combo_dict:
        # get the value from the key-value pair
        value_list.append(combo_dict[value])
    return value_list
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# colour input

# get the label_list and from the colour scheme get the colour value for each label in the order of the label_list
def create_category_colour_list(colour_dict, label_list):
    category_colour_list =[]
    for category in label_list:
        try:
            category_colour_list.append(colour_dict[category])
        except:
            print(category)
            print("could not be found, trying to remove suffix")
            # delete the last two characters (_1/_2) and try again
            category_colour_list.append(colour_dict[category[:-2]])        
    return category_colour_list

# create a colour scheme with less opacity for links trough string manipulation "rgb(0,0,0)" => "rgba(0,0,0,0.5)"
def create_link_colour_scheme(colour_dict):
    link_colour_scheme = {}
    for key, value in colour_dict.items():
        split_text = value.split("(")
        rgba_text = split_text[0] + "a(" + split_text[1]
        strip_text = rgba_text.strip(")")
        opacity = strip_text + ",0.6)"
        link_colour_scheme[key] = opacity
    return link_colour_scheme

# get colours for links from colour scheme based on source_list entries
def create_link_colour_list(colour_dict, source_list, label_list):
    link_colour_list = []
    for source in source_list:
        category = label_list[source]
        try:
            link_colour_list.append(colour_dict[category])
        except:
            print(category)
            print("could not be found, trying to remove suffix")
            # delete the last two characters (_1/_2) and try again
            link_colour_list.append(colour_dict[category[:-2]])   # maybe first filter out suffixes from list to safe this?
    return link_colour_list
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# from this create a dict with a count for all combinations
combinations_dict = {}
for value in df["combo1"]:      #alternatively use list.count() ?
    if value in combinations_dict:
        combinations_dict[value] +=1
    else:
        combinations_dict[value] = 1

print(combinations_dict)
#value_relation(df["Schad_X208"], df["Schad_2469"])

label_list = create_label_list(df[map_1], df[map_2])
colour_list = create_colour_list(label_list)
categorisation_list = create_category_colour_list(colour_scheme, label_list)
source_list = create_source_list(combinations_dict, label_list)
target_list = create_target_list(combinations_dict, label_list) 
value_list = create_value_list(combinations_dict)
link_colour_scheme = create_link_colour_scheme(colour_scheme)
link_colours = create_link_colour_list(link_colour_scheme, source_list, label_list)


map_fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = label_list,
      color = categorisation_list
    ),
    link = dict(
      source = source_list, # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = target_list,
      value = value_list,
      color = link_colours
  ))])

map_fig.update_layout(title_text="Comparison X208 and 2469", font_size=10)
#map_fig.show()
# write to image: https://plotly.github.io/plotly.py-docs/generated/plotly.io.to_image.html
map_fig.write_image(file = "img_test.png", 
                    format = "png",
                    scale = 5.0)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# sankey example

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],
      color = ["blue", "blue", "red", "red", "yellow", "yellow"]
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

# fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
# fig.show()
