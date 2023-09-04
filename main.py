import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


def transition_delay(t: int, *args):
    for a in args:
        a.update_layout(transition_duration=t)


data = pd.read_csv("automobile_sales.csv")

app = dash.Dash(__name__)
server = app.server
app.title = "Dashboard"

year_list = [i for i in range(1980, 2024, 1)]

app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard",
            style={"text-align": "center"}),
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id="dropdown-statistics",
            options=[
                {"label": "Yearly Statistics", "value": "Yearly Statistics"},
                {"label": "Recession Period Statistics", "value": "Recession Period Statistics"}
            ],
            value="Select Statistics",
            placeholder="Select a report type",
        )
    ], style={"margin": "10px 10px"}),
    html.Div(dcc.Dropdown(
        id="select-year",
        options=[{'label': i, 'value': i} for i in year_list],
        value="",
        placeholder="Select Year"
    ), style={"margin": "10px 10px"}),
    html.Div([html.Div(
        id="output-container",
        className="chart-grid",
        style={"display": "flex"}
    )])
])


@app.callback(Output("select-year", "disabled"), Input("dropdown-statistics", "value"))
def update_dropdown(value):
    if value == "Yearly Statistics":
        return False
    return True


@app.callback(Output("output-container", "children"),
              [Input("dropdown-statistics", "value"), Input("select-year", "value")])
def update_plots(stat, year):
    if stat == "Recession Period Statistics":
        recession_df = data[data.Recession == 1]

        yearly_rec = recession_df.groupby("Year")["Automobile_Sales"].mean().reset_index()
        c1 = dcc.Graph(figure=px.line(yearly_rec, x="Year", y="Automobile_Sales",
                                      title="Automobile sales fluctuate over Recession Period (year wise)"))
        vtype_rec = recession_df.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        c2 = dcc.Graph(figure=px.bar(vtype_rec, x="Vehicle_Type", y="Automobile_Sales",
                                     title="Average number of vehicles sold by vehicle type"))
        exp_rec = recession_df.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        c3 = dcc.Graph(figure=px.pie(exp_rec, "Vehicle_Type", "Advertising_Expenditure",
                                     title="Total expenditure share by vehicle type during recessions"))
        f_rec = recession_df.groupby(["unemployment_rate", "Vehicle_Type"], as_index=False)["Automobile_Sales"].sum()
        Veh_Types = recession_df.Vehicle_Type.unique()
        fig = go.Figure()
        for v in Veh_Types:
            fig.add_trace(go.Bar(x=f_rec[f_rec.Vehicle_Type == v]["unemployment_rate"],
                                 y=f_rec[f_rec.Vehicle_Type == v]["Automobile_Sales"], name=v))
        fig.update_layout(title="Effect of unemployment rate on vehicle type and sales",
                          xaxis_title="unemployment_rate", yaxis_title="Automobile_Sales")
        c4 = dcc.Graph(figure=fig)

        return [
            html.Div(className="chart-item", children=[html.Div(children=c1), html.Div(children=c2)]),
            html.Div(className="chart-item", children=[html.Div(children=c3), html.Div(children=c4)])
        ]
    elif str(year).isnumeric() and stat == "Yearly Statistics":
        year_data = data[data.Year == int(year)]

        yearly_sales = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        f1 = px.line(yearly_sales, x="Year", y="Automobile_Sales",
                     title="Automobile sales (year wise)")

        monthly_sales = year_data.groupby("Month")["Automobile_Sales"].mean().reset_index()
        f2 = px.line(monthly_sales, x="Month", y="Automobile_Sales",
                     title=f"Automobile sales (Year {year} months)")

        vtypes_sales = year_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        f3 = px.bar(vtypes_sales, x="Vehicle_Type", y="Automobile_Sales",
                    title=f"Average Vehicles Sold by Vehicle Type in the year {year}")

        exp_rec = year_data.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        f4 = px.pie(exp_rec, "Vehicle_Type", "Advertising_Expenditure",
                    title=f"Total expenditure share by vehicle type in year {year}")

        transition_delay(1000, f1, f2, f3, f4)

        c1 = dcc.Graph(figure=f1)
        c2 = dcc.Graph(figure=f2)
        c3 = dcc.Graph(figure=f3)
        c4 = dcc.Graph(figure=f4)

        return [
            html.Div(className="chart-item", children=[html.Div(children=c1), html.Div(children=c2)]),
            html.Div(className="chart-item", children=[html.Div(children=c3), html.Div(children=c4)])
        ]


if __name__ == "__main__":
    app.run()
