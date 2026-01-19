import pandas as pd
import plotly.graph_objects as go
import requests
from dash import html, dcc, Input, Output

from dashboard.utils import api_get, API_BASE
from dashboard.components.navbar import navbar


# Safe empty figure (used when errors happen so Dash doesn't crash)
EMPTY_FIG = go.Figure()
EMPTY_FIG.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360)


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
            html.Div(
                "API-driven KPIs and trends",
                style={"opacity": 0.7, "marginBottom": "16px"},
            ),
            # Controls
            html.Div(
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "16px",
                },
                children=[
                    dcc.DatePickerRange(
                        id="date-range",
                        display_format="YYYY-MM-DD",
                        minimum_nights=0,
                    ),
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
                    dcc.Input(
                        id="jwt-token",
                        type="password",
                        placeholder="Paste JWT access token (for Orders)",
                        style={"width": "360px", "padding": "8px"},
                    ),
                    dcc.Interval(id="refresh", interval=60_000, n_intervals=0),
                ],
            ),
            # KPI Cards
            html.Div(
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "16px",
                },
                children=[
                    kpi_card("Total Revenue", "kpi-revenue"),
                    kpi_card("Total Orders", "kpi-orders"),
                    kpi_card("Unique Customers", "kpi-customers"),
                    kpi_card("Avg Order Value", "kpi-aov"),
                ],
            ),
            # Charts
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "12px",
                },
                children=[
                    html.Div(
                        style={
                            "padding": "12px",
                            "border": "1px solid #e5e7eb",
                            "borderRadius": "12px",
                            "background": "white",
                        },
                        children=[
                            html.H3("Revenue Trend", style={"marginTop": "0"}),
                            dcc.Graph(
                                id="revenue-trend",
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "padding": "12px",
                            "border": "1px solid #e5e7eb",
                            "borderRadius": "12px",
                            "background": "white",
                        },
                        children=[
                            html.H3("Top Products", style={"marginTop": "0"}),
                            dcc.Graph(
                                id="top-products",
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
            # Recent Orders Table (JWT)
            html.Div(
                style={
                    "marginTop": "12px",
                    "padding": "12px",
                    "border": "1px solid #e5e7eb",
                    "borderRadius": "12px",
                    "background": "white",
                },
                children=[
                    html.H3("Recent Orders (JWT required)", style={"marginTop": "0"}),
                    dcc.Graph(id="orders-table", config={"displayModeBar": False}),
                    html.Div(
                        id="orders-error",
                        style={"marginTop": "8px", "color": "#b91c1c"},
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
        Output("orders-table", "figure"),
        Output("orders-error", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("granularity", "value"),
        Input("jwt-token", "value"),
        Input("refresh", "n_intervals"),
    )
    def update_dashboard(start_date, end_date, granularity, jwt_token, n):
        try:
            params = {}
            if start_date:
                params["date_from"] = start_date
            if end_date:
                params["date_to"] = end_date

            # KPIs (if this fails, we catch it below)
            kpis = api_get("/kpis/", params=params)

            # Revenue trends
            trend_params = dict(params)
            trend_params["granularity"] = granularity
            trends = api_get("/revenue/trends/", params=trend_params)
            df_trend = pd.DataFrame(trends.get("points", []))

            if not df_trend.empty:
                df_trend["bucket"] = pd.to_datetime(df_trend["bucket"], errors="coerce")
                df_trend = df_trend.dropna(subset=["bucket"]).sort_values("bucket")

            fig_trend = go.Figure()
            if not df_trend.empty:
                fig_trend.add_trace(
                    go.Scatter(x=df_trend["bucket"], y=df_trend["revenue"], mode="lines+markers")
                )
            fig_trend.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=360,
                uirevision="revenue-trend",
            )

            # Top products
            top = api_get("/products/top-sellers/", params={**params, "metric": "revenue", "limit": 10})
            df_top = pd.DataFrame(top.get("items", []))

            fig_top = go.Figure()
            if not df_top.empty:
                fig_top.add_trace(go.Bar(x=df_top["product_id"], y=df_top["revenue"]))
            fig_top.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=360,
                uirevision="top-products",
            )

            status = f"API: {API_BASE} | Refresh tick: {n}"

            # Recent orders (JWT protected)
            orders_fig = go.Figure()
            orders_error = ""

            try:
                orders = api_get("/orders/", params={**params, "page_size": 15}, token=jwt_token)
                df_orders = pd.DataFrame(orders.get("results", []))

                if not df_orders.empty:
                    show_cols = ["order_id", "created_at", "order_amount", "quantity", "customer_id", "product_id"]
                    for c in show_cols:
                        if c not in df_orders.columns:
                            df_orders[c] = ""
                    df_orders = df_orders[show_cols]

                    orders_fig = go.Figure(
                        data=[
                            go.Table(
                                header=dict(values=list(df_orders.columns)),
                                cells=dict(values=[df_orders[col].astype(str).tolist() for col in df_orders.columns]),
                            )
                        ]
                    )
                    orders_fig.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=420,
                        uirevision="orders-table",
                    )

            except requests.HTTPError:
                orders_error = (
                    "Orders endpoint requires a valid JWT access token. "
                    "Get one from /api/docs → /api/v1/auth/token/."
                )
            except Exception as e:
                orders_error = f"Failed to load orders: {e}"

            return (
                f"€ {kpis['total_revenue']:.2f}",
                str(kpis["total_orders"]),
                str(kpis["unique_customers"]),
                f"€ {kpis['avg_order_value']:.2f}",
                fig_trend,
                fig_top,
                status,
                orders_fig,
                orders_error,
            )

        except Exception as e:
            # If any main API call fails, return safe placeholders so Dash never crashes
            return (
                "—",
                "—",
                "—",
                "—",
                EMPTY_FIG,
                EMPTY_FIG,
                f"ERROR: {e} | Check DASH_API_BASE_URL and backend server",
                EMPTY_FIG,
                "Dashboard failed to load. Fix API_BASE or backend, then refresh.",
            )
