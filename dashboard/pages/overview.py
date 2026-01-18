import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from dashboard.utils import api_get, API_BASE
from dashboard.components.navbar import navbar


def kpi_card(title: str, value_id: str):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "14px", "opacity": 0.7}),
            html.Div(id=value_id, style={"fontSize": "28px", "fontWeight": "700"}),
        ],
        style={
            "padding": "16px",
            "border": "1px solid #e5e7eb",
            "borderRadius": "12px",
            "background": "white",
            "boxShadow": "0 1px 2px rgba(0,0,0,0.05)",
            "minWidth": "200px",
        },
    )


def layout():
    return html.Div(
        style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
        children=[
            navbar(),

            html.H1("Overview", style={"marginBottom": "8px"}),
            html.Div("API-driven KPIs and trends", style={"opacity": 0.7, "marginBottom": "16px"}),

            html.Div(
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
                children=[
                    dcc.DatePickerRange(id="date-range", display_format="YYYY-MM-DD", minimum_nights=0),
                    dcc.Dropdown(
                        id="granularity",
                        options=[
                            {"label": "Daily", "value": "daily"},
                            {"label": "Weekly", "value": "weekly"},
                            {"label": "Monthly", "value": "monthly"},
                        ],
                        value="daily",
                        clearable=False,
                        style={"width": "220px"},
                    ),
                    dcc.Interval(id="refresh", interval=60_000, n_intervals=0),
                ],
            ),

            html.Div(
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
                children=[
                    kpi_card("Total Revenue", "kpi-revenue"),
                    kpi_card("Total Orders", "kpi-orders"),
                    kpi_card("Unique Customers", "kpi-customers"),
                    kpi_card("Avg Order Value", "kpi-aov"),
                ],
            ),

            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"},
                children=[
                    html.Div(
                        style={"padding": "12px", "border": "1px solid #e5e7eb", "borderRadius": "12px", "background": "white"},
                        children=[html.H3("Revenue Trend", style={"marginTop": "0"}), dcc.Graph(id="revenue-trend", config={"displayModeBar": False})],
                    ),
                    html.Div(
                        style={"padding": "12px", "border": "1px solid #e5e7eb", "borderRadius": "12px", "background": "white"},
                        children=[html.H3("Top Products", style={"marginTop": "0"}), dcc.Graph(id="top-products", config={"displayModeBar": False})],
                    ),
                ],
            ),

            html.Div(id="status", style={"marginTop": "12px", "opacity": 0.7}),
        ],
    )


def register_callbacks(app):
    @app.callback(
        Output("kpi-revenue", "children"),
        Output("kpi-orders", "children"),
        Output("kpi-customers", "children"),
        Output("kpi-aov", "children"),
        Output("revenue-trend", "figure"),
        Output("top-products", "figure"),
        Output("status", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("granularity", "value"),
        Input("refresh", "n_intervals"),
    )
    def update_dashboard(start_date, end_date, granularity, n):
        params = {}
        if start_date:
            params["date_from"] = start_date
        if end_date:
            params["date_to"] = end_date

        kpis = api_get("/kpis/", params=params)

        trend_params = dict(params)
        trend_params["granularity"] = granularity
        trends = api_get("/revenue/trends/", params=trend_params)
        df_trend = pd.DataFrame(trends["points"])

        fig_trend = go.Figure()
        if not df_trend.empty:
            fig_trend.add_trace(go.Scatter(x=df_trend["bucket"], y=df_trend["revenue"], mode="lines+markers"))
        fig_trend.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)

        top = api_get("/products/top-sellers/", params={**params, "metric": "revenue", "limit": 10})
        df_top = pd.DataFrame(top["items"])

        fig_top = go.Figure()
        if not df_top.empty:
            fig_top.add_trace(go.Bar(x=df_top["product_id"], y=df_top["revenue"]))
        fig_top.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)

        status = f"API: {API_BASE} | Refresh tick: {n}"

        return (
            f"€ {kpis['total_revenue']:.2f}",
            str(kpis["total_orders"]),
            str(kpis["unique_customers"]),
            f"€ {kpis['avg_order_value']:.2f}",
            fig_trend,
            fig_top,
            status,
        )
