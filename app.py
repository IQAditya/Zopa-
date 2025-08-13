# app.py
import numpy as np
import plotly.graph_objs as go
from dash import Dash, html, dcc, Input, Output, callback_context

app = Dash(__name__)
app.title = "Redistribution on x + y = V"

X_MIN, X_MAX = 0.0, 470.0
Y_MIN, Y_MAX = 0.0, 470.0

def clamp(v, lo, hi): return max(lo, min(hi, v))
def delta_and_Veff(Px, Py, V):
    V_eff = max(V, Px + Py)
    d = V_eff - (Px + Py)
    return d, V_eff
def feasible_qx_bounds(Px, Py, V):
    d, _ = delta_and_Veff(Px, Py, V)
    qx_min = clamp(Px, X_MIN, X_MAX)
    qx_max = clamp(Px + d, X_MIN, X_MAX)
    if qx_max < qx_min: qx_max = qx_min
    return qx_min, qx_max

def build_figure(Px, Py, V, Qx, showP, showQ, showSlope):
    d, V_eff = delta_and_Veff(Px, Py, V)
    Qy = V_eff - Qx
    xs = np.linspace(X_MIN, X_MAX, 600)
    ys = V_eff - xs

    traces = []
    if showSlope:
        traces.append(go.Scatter(x=xs, y=ys, mode="lines", name="x + y = V",
                                 line=dict(color="#e11d48", width=3)))
    if showP:
        traces += [
            go.Scatter(x=[Px, Px], y=[Y_MIN, Py], mode="lines",
                       line=dict(color="#9ca3af", dash="dash"), showlegend=False),
            go.Scatter(x=[X_MIN, Px], y=[Py, Py], mode="lines",
                       line=dict(color="#9ca3af", dash="dash"), showlegend=False),
        ]
    if showQ:
        traces += [
            go.Scatter(x=[Qx, Qx], y=[Y_MIN, Qy], mode="lines",
                       line=dict(color="#60a5fa", dash="dash"), showlegend=False),
            go.Scatter(x=[X_MIN, Qx], y=[Qy, Qy], mode="lines",
                       line=dict(color="#60a5fa", dash="dash"), showlegend=False),
        ]

    traces.append(go.Scatter(x=[Px, Qx], y=[Py, Qy], mode="lines", name="PQ",
                             line=dict(color="#059669", dash="dash", width=3)))
    traces.append(go.Scatter(x=[Qx, Qx], y=[Py, Qy], mode="lines", name="Height h",
                             line=dict(color="#059669", dash="dot", width=2)))

    xA, yA = Px + d, Py
    xB, yB = Px, Py + d
    traces.append(go.Scatter(x=[xA], y=[yA], mode="markers", name="All extra → X",
                             marker=dict(symbol="square-open", color="#059669", size=11)))
    traces.append(go.Scatter(x=[xB], y=[yB], mode="markers", name="All extra → Y",
                             marker=dict(symbol="square-open", color="#7c3aed", size=11)))

    if showP:
        traces.append(go.Scatter(
            x=[Px], y=[Py], mode="markers+text", name="P(start)",
            marker=dict(color="#111827", size=11, line=dict(width=1, color="#111827")),
            text=[f"P = ({Px:.1f}, {Py:.1f})"], textposition="bottom right"
        ))
    if showQ:
        traces.append(go.Scatter(
            x=[Qx], y=[Qy], mode="markers+text", name="Q (allocation)",
            marker=dict(color="white", size=10, line=dict(width=2, color="#2563eb")),
            text=[f"Q = ({Qx:.1f}, {Qy:.1f})"], textposition="bottom right"
        ))

    fig = go.Figure(traces)
    fig.update_layout(
        margin=dict(l=40, r=20, t=40, b=40),
        height=700, plot_bgcolor="#ffffff", paper_bgcolor="#f8f9fb",
        legend=dict(bgcolor="white", bordercolor="#e5e7eb", borderwidth=1,
                    orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(size=13, color="#1f2937"),
        xaxis=dict(range=[X_MIN, X_MAX], gridcolor="#e5e7eb", zeroline=False, title="x"),
        yaxis=dict(range=[Y_MIN, Y_MAX], gridcolor="#e5e7eb", zeroline=False, title="y"),
        dragmode=False
    )
    return fig

def num_row(id_prefix, label, init, step=1):
    return html.Div([
        html.Div(label, className="label"),
        dcc.Input(id=f"{id_prefix}-input", type="number", value=init, step=step, className="num"),
        html.Button("＋", id=f"{id_prefix}-inc", n_clicks=0, className="btn plus"),
        html.Button("－", id=f"{id_prefix}-dec", n_clicks=0, className="btn minus"),
    ], className="row")

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([html.H1("Redistribution on x + y = V"),
                          html.P("Feasible segment from P with x + y = V", className="subtitle")],
                         className="topbar"),
            ], className="card"),
            html.Div([dcc.Graph(id="graph", config={"displayModeBar": False}, style={"height":"520px"})],
                     className="card"),
            html.Div([
                html.H3("Allocation (Q.x)"),
                dcc.Slider(id="qx-slider", min=0, max=400, step=0.1, value=140.0,
                           tooltip={"placement":"bottom", "always_visible":True}),
            ], className="card section"),
        ], className="left"),

        html.Div([
            html.Div([
                html.H3("Points & Values"),
                num_row("px", "P.x", 100.0),
                num_row("py", "P.y", 200.0),
                num_row("v",  "V (x+y)", 400.0),
                num_row("qx", "Q.x", 140.0),
                num_row("qy", "Q.y", 260.0),
            ], className="card section"),

            html.Div([
                html.H3("Visibility"),
                dcc.Checklist(
                    id="visibility",
                    options=[{"label":" Show P","value":"P"},
                             {"label":" Show Q","value":"Q"},
                             {"label":" Show Slope Line","value":"S"}],
                    value=["P","Q","S"],
                    style={"display":"flex","flexDirection":"column","gap":"6px"}
                )
            ], className="card section"),
        ], className="right")
    ], className="app")
])

@app.callback(
    Output("graph", "figure"),
    Output("qx-slider", "min"),
    Output("qx-slider", "max"),
    Output("qx-slider", "value"),
    Input("px-input", "value"),
    Input("py-input", "value"),
    Input("v-input",  "value"),
    Input("qx-input", "value"),
    Input("qy-input", "value"),
    Input("qx-slider", "value"),
    Input("px-inc", "n_clicks"),
    Input("px-dec", "n_clicks"),
    Input("py-inc", "n_clicks"),
    Input("py-dec", "n_clicks"),
    Input("v-inc",  "n_clicks"),
    Input("v-dec",  "n_clicks"),
    Input("qx-inc", "n_clicks"),
    Input("qx-dec", "n_clicks"),
    Input("qy-inc", "n_clicks"),
    Input("qy-dec", "n_clicks"),
    Input("visibility", "value"),
)
def update_plot(px, py, v, qx, qy, qx_slider,
                px_inc, px_dec, py_inc, py_dec, v_inc, v_dec, qx_inc, qx_dec, qy_inc, qy_dec,
                visibility):
    # Parse numbers with defaults
    Px = float(px or 100.0); Py = float(py or 200.0); V = float(v or 400.0)
    Qx = float(qx or 140.0); Qy = float(qy or (V - Qx))

    trig = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
    # Button increments
    if trig.startswith("px-inc"): Px += 1
    elif trig.startswith("px-dec"): Px -= 1
    elif trig.startswith("py-inc"): Py += 1
    elif trig.startswith("py-dec"): Py -= 1
    elif trig.startswith("v-inc"):  V += 1
    elif trig.startswith("v-dec"):  V -= 1
    elif trig.startswith("qx-inc"): Qx += 1
    elif trig.startswith("qx-dec"): Qx -= 1
    elif trig.startswith("qy-inc"): Qy += 1
    elif trig.startswith("qy-dec"): Qy -= 1
    elif trig.startswith("qx-slider"): Qx = float(qx_slider)

    # Keep P in bounds
    Px = clamp(Px, X_MIN, X_MAX); Py = clamp(Py, Y_MIN, Y_MAX)

    # Feasible Q.x interval
    qx_min, qx_max = feasible_qx_bounds(Px, Py, V)
    d, V_eff = delta_and_Veff(Px, Py, V)

    # If user typed (or bumped) Q.y, back-solve Qx
    if trig.startswith("qy-") or trig.startswith("qy-input"):
        Qx = V_eff - Qy

    # Clamp Qx and compute Qy on line
    Qx = clamp(Qx, qx_min, qx_max)
    Qy = V_eff - Qx

    showP = "P" in (visibility or [])
    showQ = "Q" in (visibility or [])
    showSlope = "S" in (visibility or [])
    fig = build_figure(Px, Py, V, Qx, showP, showQ, showSlope)
    return fig, qx_min, qx_max, Qx

if __name__ == "__main__":
    app.run_server(debug=True)
