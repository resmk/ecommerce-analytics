from dash import Dash, dcc, html, Input, Output

from dashboard.pages import overview, customers

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "E-Commerce Analytics Dashboard"


app.layout = html.Div(
    style={"fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Arial", "background": "#f5f6fa", "minHeight": "100vh"},
    children=[
        dcc.Location(id="url"),
        html.Div(id="page-content"),
    ],
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def route(pathname):
    if pathname == "/customers":
        return customers.layout()
    return overview.layout()


# Register callbacks for each page
overview.register_callbacks(app)
customers.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)



