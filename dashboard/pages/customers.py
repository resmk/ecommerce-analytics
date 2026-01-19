import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from dashboard.utils import api_get
from dashboard.components.navbar import navbar


def layout():
    return html.Div(
        style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
        children=[
            navbar(),

            html.H1("Customer Analytics", style={"marginBottom": "8px"}),
            html.Div("RFM segmentation", style={"opacity": 0.7, "marginBottom": "16px"}),

            html.Div(
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
                children=[
                    dcc.DatePickerRange(id="cust-date-range", display_format="YYYY-MM-DD", minimum_nights=0),
                    dcc.Interval(id="cust-refresh", interval=60_000, n_intervals=0),
                ],
            ),

            html.Div(
                style={"padding": "12px", "border": "1px solid #e5e7eb", "borderRadius": "12px", "background": "white"},
                children=[
                    html.H3("RFM Segments", style={"marginTop": "0"}),
                    dcc.Graph(id="rfm-pie", config={"displayModeBar": False}),
                ],
            ),

            html.Div(id="cust-status", style={"marginTop": "12px", "opacity": 0.7}),
        ],
    )


def register_callbacks(app):
    @app.callback(
        Output("rfm-pie", "figure"),
        Output("cust-status", "children"),
        Input("cust-date-range", "start_date"),
        Input("cust-date-range", "end_date"),
        Input("cust-refresh", "n_intervals"),
    )
    def update_customer_page(start_date, end_date, n):
        params = {}
        if start_date:
            params["date_from"] = start_date
        if end_date:
            params["date_to"] = end_date

        data = api_get("/customers/segments/", params=params)
        df = pd.DataFrame(data["segments"])

        fig = go.Figure()
        if not df.empty:
            fig.add_trace(go.Pie(labels=df["segment"], values=df["customers"], hole=0.45))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)

        status = f"Customers in range: {data.get('total_customers_in_range', 0)} | Refresh tick: {n}"
        return fig, status