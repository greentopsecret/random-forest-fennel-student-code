import json

import plotly
import plotly.express as px


def plot_population(country="Germany"):
    """
    Generate a Plotly figure and convert it to a JSON string.
    Uses sample data from gapminder as an example.
    """

    df = px.data.gapminder()  # pandas DataFrame
    df_filtered = df[df["country"] == country]
    data_figure = px.bar(
        df_filtered, x="year", y="pop", title=f"Population of {country}"
    )  # Plotly "Figure" Object

    data_json = json.dumps(data_figure, cls=plotly.utils.PlotlyJSONEncoder)

    return data_json
