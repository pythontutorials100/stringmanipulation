# this code works, provides desired results in apt format

import os
import requests
import stardog
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
import dash_daq as daq
import itertools

# Initialize a global part index counter
part_index_counter = itertools.count(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Stardog connection details
session = requests.Session()
session.verify = False  # Skip SSL verification for Stardog (Use with caution)
conn_details = {
    'endpoint': 'https://sd-dbb95fdb.stardog.cloud:5820',
    'username': os.getenv('STARDOG_USERNAME'),
    'password': os.getenv('STARDOG_PASSWORD'),
    'session': session
}
database_name = 'myDB'

# Define qualities and their corresponding user-friendly questions
qualities_info = {
    "Top Group": {
        "Program_Specific_Marking_Requirement_Quality": "Is there a program-specific marking requirement?",
        "Marking_Requirement_Quality": "Is there a marking requirement?",
        "Serial_Number_Requirement_Quality": "Is a serial number required?"
    },
    "Left Group": {
        "Engraving_Allowance_Quality": "Does the part require engraving allowance?",
        "Future_Engraving_Allowance_Quality": "Is future engraving allowance needed?",
        "MachinedQuality": "Is the part machined?",
        "AdditiveManufacturedQuality": "Is the part additively manufactured?",
        "CastManufacturedQuality": "Is the part cast manufactured?"
    },
    "Right Group": {
        "ForgedManufacturedQuality": "Is the part forged?",
        "WeldedManufacturedQuality": "Is the part welded?",
        "SheetMetalManufacturedQuality": "Is the part made from sheet metal?",
        "Laser_Process_Involvement_Quality": "Is laser process involvement required?",
        "Laser_Accessibility_Quality": "Is laser accessibility required?",
        "CNC_Machining_Accessibility_Quality": "Is CNC machining accessibility required?"
    }
}

# Initialize Dash app with Bootstrap CSS
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Function to generate a table for a group of qualities
def generate_quality_table(group_name, qualities):
    table_rows = []
    for quality, question in qualities.items():
        row = html.Tr([
            html.Td(
                html.Span([
                    html.Strong(f"{quality}: "),
                    question
                ], style={'font-size': '12px'})  # Adjusted font size
            ),
            html.Td(
                daq.ToggleSwitch(
                    id={'type': 'quality-input', 'index': quality},
                    value=False,
                    size=40  # Adjusted size for a smaller toggle switch
                ),
                style={'text-align': 'center'}
            )
        ], id={'type': 'table-row', 'index': quality})
        table_rows.append(row)
    table = dbc.Table(
        children=[
            html.Thead(html.Tr([
                html.Th("Quality Name and Question", style={'font-size': '13px'}),
                html.Th("Select", style={'font-size': '13px', 'text-align': 'center'})
            ])),
            html.Tbody(table_rows)
        ],
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'width': '100%', 'margin-bottom': '0px'}  # Reduced margin-bottom
    )
    return html.Div([
        html.H5(group_name, style={'text-align': 'center', 'font-size': '14px', 'margin-bottom': '5px'}),
        table
    ], style={'margin-bottom': '10px'})  # Reduced space between tables

# Layout
app.layout = dbc.Container([
    html.H1("Define a New Part and Find Matching Specifications", style={'text-align': 'center', 'font-size': '20px'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label("Enter Part Number or Name:", style={'font-size': '14px'}),
            dcc.Input(
                id="part-name-input",
                type="text",
                placeholder="Enter Part Number (e.g., PN-2001)",
                value="",
                style={'width': '100%', 'font-size': '14px'}
            )
        ], md={'size': 6, 'offset': 3})
    ]),
    html.Br(),
    html.H2("Set Qualities:", style={'text-align': 'center', 'font-size': '16px'}),
    # Top Group Table
    dbc.Row([
        dbc.Col(
            generate_quality_table("Marking Requirements", qualities_info["Top Group"]),
            md={'size': 6, 'offset': 3},
            style={'margin-bottom': '10px'}  # Reduced space
        )
    ]),
    # Left and Right Group Tables Side by Side
    dbc.Row([
        dbc.Col(
            generate_quality_table("Manufacturing Methods", qualities_info["Left Group"]),
            md=6,
            style={'margin-bottom': '10px'}  # Reduced space
        ),
        dbc.Col(
            generate_quality_table("Other Qualities", qualities_info["Right Group"]),
            md=6,
            style={'margin-bottom': '10px'}  # Reduced space
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Button("Submit", id="submit-button", color="primary", style={'width': '100%', 'font-size': '14px'}),
            md={'size': 4, 'offset': 4}
        )
    ]),
    html.Br(),
    html.Div(id="result-output")
], fluid=True, style={'font-size': '12px'})  # Adjusted default font size

# Callback to update row styles based on toggle switch values
@app.callback(
    Output({'type': 'table-row', 'index': ALL}, 'style'),
    Input({'type': 'quality-input', 'index': ALL}, 'value')
)
def update_row_styles(toggle_values):
    styles = []
    for value in toggle_values:
        if value:
            styles.append({'backgroundColor': '#d0e1f9'})  # Light blue
        else:
            styles.append({})
    return styles



def generate_rdf_data(part_name, quality_dict, part_index):
    # URIs for the part, part number, and Information Bearing Entity (IBE)
    part_uri = f":part_{part_index}"
    part_number_uri = f":ice_part_number_{part_index}"
    ibe_part_number_uri = f":ibe_part_number_{part_index}"

    # Generate the qualities list
    qualities_list = [f":{quality}_{part_index}.{i+1}" for i, quality in enumerate(quality_dict.keys())]

    # Build the Part Item triple
    if qualities_list:
        # There are qualities
        rdf_data = f"""
        # Part Item
        {part_uri} a :Part_item ;
                    :bearer_of {', '.join(qualities_list)} .
        """
    else:
        # No qualities
        rdf_data = f"""
        # Part Item
        {part_uri} a :Part_item .
        """

    # Continue building RDF data
    rdf_data += f"""
        # Part Number
        {part_number_uri} a :Part_Number ;
                           :designates {part_uri} ;
                           :generically_depends_on {ibe_part_number_uri} .

        {ibe_part_number_uri} a :Information_Bearing_Entity ;
                               :has_text_value "{part_name}"^^xsd:string .
    """

    # Add each quality with unique URIs
    for i, (quality, value) in enumerate(quality_dict.items(), start=1):
        # Unique URIs for Quality, Descriptive Information Content Entity (ICE), and Information Bearing Entity (IBE)
        quality_instance = f":{quality}_{part_index}.{i}"
        ice_quality_uri = f":ice_{quality}_{part_index}.{i}"
        ibe_quality_uri = f":ibe_{quality}_{part_index}.{i}"

        rdf_data += f"""
        # Quality Instance
        {quality_instance} a :Quality .

        # Descriptive Information Content Entity for Quality
        {ice_quality_uri} a :Descriptive_Information_Content_Entity ;
                           :describes {quality_instance} ;
                           :generically_depends_on {ibe_quality_uri} .

        # Information Bearing Entity for Quality
        {ibe_quality_uri} a :Information_Bearing_Entity ;
                           :has_boolean_value {str(value).lower()} .
        """

    # Debugging: Print the generated RDF data
    print("Generated RDF Data:")
    print(rdf_data)

    return rdf_data, part_index

# Function to insert RDF data into Stardog
def insert_rdf_data(rdf_data):
    try:
        # Build the SPARQL Update query
        query = f"""
        PREFIX : <http://api.stardog.com/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            {rdf_data}
        }}
        """
        print("Executing SPARQL Update:\n", query)
        with stardog.Connection(database_name, **conn_details) as conn:
            conn.update(query)
        return True
    except Exception as e:
        print(f"Error inserting data: {e}")
        return False

# Function to execute SPARQL queries
def execute_query(query):
    try:
        print("Executing SPARQL query:\n", query)  # Debug: Print the query
        with stardog.Connection(database_name, **conn_details) as conn:
            results = conn.select(query)
        return results['results']['bindings']
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

# Function to get matching specifications for a given part name
def get_matching_specifications(part_name):
    query = f"""
    PREFIX : <http://api.stardog.com/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?partNumber ?specification ?processDescription
    WHERE {{
      # Retrieve the Part Number and Part Item
      ?ibe_part_number a :Information_Bearing_Entity ;
                       :has_text_value "{part_name}"^^xsd:string .
      ?ice_part_number a :Part_Number ;
                       :generically_depends_on ?ibe_part_number ;
                       :designates ?part .

      # Retrieve the Part's Qualities and Values
      ?part :bearer_of ?partQuality .
      ?icePartQuality :describes ?partQuality ;
                      :generically_depends_on ?ibePartQuality .
      ?ibePartQuality :has_boolean_value ?partValue .
      BIND(STRAFTER(STR(?partQuality), "http://api.stardog.com/") AS ?fullPartQualityName)
      BIND(REPLACE(?fullPartQualityName, "^(.*)_.*$", "$1") AS ?qualityName)

      # Retrieve Specifications and their Qualities
      ?specification a :Directive_Information_Content_Entity ;
                     :has_part ?specQualitySpec ;
                     :is_about ?plan .
      ?plan :prescribes ?process .
      ?ice_process a :Designative_Information_Content_Entity ;
                   :designates ?process ;
                   :generically_depends_on ?ibe_process .
      ?ibe_process a :Information_Bearing_Entity ;
                   :has_text_value ?processDescription .
      ?specQualitySpec :generically_depends_on ?ibeSpecQuality .
      ?ibeSpecQuality :has_boolean_value ?specValue .
      BIND(STRAFTER(STR(?specQualitySpec), "http://api.stardog.com/") AS ?fullSpecQualityName)
      BIND(REPLACE(?fullSpecQualityName, "^ice_(.*)_spec.*$", "$1") AS ?qualityNameSpec)

      # Compare Qualities and Values
      FILTER(?qualityName = ?qualityNameSpec)
      BIND(IF(?partValue = ?specValue, 1, 0) AS ?match)
    }}
    GROUP BY ?partNumber ?specification ?processDescription
    HAVING (
        SUM(?match) = COUNT(DISTINCT ?specQualitySpec) &&
        COUNT(DISTINCT ?specQualitySpec) > 0
    )
    """
    return execute_query(query)

# Callback to execute query and display results
@app.callback(
    Output("result-output", "children"),
    Input("submit-button", "n_clicks"),
    State("part-name-input", "value"),
    State({'type': 'quality-input', 'index': ALL}, 'value'),
    State({'type': 'quality-input', 'index': ALL}, 'id')
)
def update_output(n_clicks, part_name, quality_values, quality_ids):
    if not n_clicks:
        return "Enter a part name and set qualities, then click submit to see results."
    if not part_name:
        return "Please enter a valid part name."

    # Create a mapping from IDs to values
    quality_dict = {}
    for id_dict, value in zip(quality_ids, quality_values):
        # id_dict should be {'type': 'quality-input', 'index': quality_name}
        quality_name = id_dict.get('index')
        if quality_name is not None:
            quality_dict[quality_name] = value
        else:
            print("Warning: Found id_dict without 'index':", id_dict)

    # Debugging: Print the quality_dict
    print("Quality Dict:", quality_dict)

    # Generate a unique part index
    part_index = str(uuid.uuid4())

    # Generate RDF data
    rdf_data, _ = generate_rdf_data(part_name, quality_dict, part_index)

    # Insert RDF data into Stardog
    if not insert_rdf_data(rdf_data):
        return html.Div([
            html.H3("An error occurred while inserting data into the database.")
        ])

    # Execute matching query
    results = get_matching_specifications(part_name)
    if results is None:
        return html.Div([
            html.H3("An error occurred while executing the query. Please check the server logs for details.")
        ])
    if not results:
        return html.Div([
            html.H3(f"No matching specifications found for part: {part_name}")
        ])

    # Display results
    df = pd.DataFrame([
        {
            "Specification": result["specification"]["value"],
            "Process Description": result["processDescription"]["value"]
        }
        for result in results
    ])

    return html.Div([
        html.H3(f"Matching Specifications for {part_name}:"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'lightgrey',
                'fontWeight': 'bold'
            }
        )
    ])


# Run app
if __name__ == "__main__":
    app.run_server(debug=True)


