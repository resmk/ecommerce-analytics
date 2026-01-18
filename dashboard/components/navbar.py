from dash import html, dcc


def navbar():
    link_style = {"marginRight": "12px", "textDecoration": "none", "fontWeight": "600"}

    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "14px 16px",
            "border": "1px solid #e5e7eb",
            "borderRadius": "12px",
            "background": "white",
            "marginBottom": "16px",
        },
        children=[
            html.Div("E-Commerce Analytics", style={"fontWeight": "800"}),
            html.Div(
                children=[
                    dcc.Link("Overview", href="/", style=link_style),
                    dcc.Link("Customers", href="/customers", style=link_style),
                ]
            ),
        ],
    )
