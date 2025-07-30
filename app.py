import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from weasyprint import HTML
import base64
import io

# ==============================================================================
# APP INITIALIZATION
# ==============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# ==============================================================================
# APPLICATION LAYOUT - WITH "RUN SIMULATION" BUTTON
# ==============================================================================
app.layout = dbc.Container(fluid=True, children=[
    dcc.Store(id='calculation-results-store'),
    
    html.Div(
        dbc.Container(
            html.H2("EV Charging + Solar Feasibility Dashboard", className="my-3 text-primary")
        ), className="bg-light p-3 mb-4 rounded-3"
    ),

    dbc.Row([
        # --- LEFT COLUMN: CONTROL PANEL (INPUTS) ---
        dbc.Col(width=12, lg=4, children=[
            dbc.Card(body=True, children=[
                html.H4("Input Parameters", className="card-title mb-4"),
                dbc.Accordion(always_open=True, children=[
                    # --- Accordion items for inputs (code unchanged, truncated for brevity) ---
                    dbc.AccordionItem(title="1. Project Setup", children=[
                        dbc.Row([
                            dbc.Col(html.Label("Project Name", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.Input(id="project-name", value="My Charging Hub"), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        html.Div([
                            html.Label("Simulation Years", className="form-label"),
                            dcc.Slider(id="simulation-years", min=5, max=25, step=1, value=20, marks=None, tooltip={"placement": "bottom", "always_visible": True})
                        ], className="mb-3 mt-4"),
                    ]),
                    dbc.AccordionItem(title="2. Energy System", children=[
                        dbc.Row([
                            dbc.Col(html.Label("PV System Size", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="pv-size", type="number", value=150), dbc.InputGroupText("kWp")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Battery Storage Size", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="battery-size", type="number", value=200), dbc.InputGroupText("kWh")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Annual EV Demand", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="ev-demand", type="number", value=300000), dbc.InputGroupText("kWh/yr")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                    ]),
                    dbc.AccordionItem(title="3. Financial Assumptions", children=[
                        dbc.Row([
                            dbc.Col(html.Label("PV System Cost", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="pv-cost", type="number", value=900), dbc.InputGroupText("€/kWp")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Battery Cost", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="battery-cost", type="number", value=450), dbc.InputGroupText("€/kWh")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Infrastructure Cost", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="infra-cost", type="number", value=100000), dbc.InputGroupText("€")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("O&M Cost", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="om-cost-pct", type="number", value=1.5, step=0.1), dbc.InputGroupText("%/yr")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Grid Electricity Price", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="grid-price", type="number", value=0.18, step=0.01), dbc.InputGroupText("€/kWh")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Feed-in Tariff", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="feed-in-tariff", type="number", value=0.07, step=0.01), dbc.InputGroupText("€/kWh")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Annual Inflation Rate", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="inflation-pct", type="number", value=2.0, step=0.1), dbc.InputGroupText("%")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                    ]),
                     dbc.AccordionItem(title="4. Taxes, Loans & Incentives", children=[
                        dbc.Row([
                            dbc.Col(html.Label("Loan Coverage", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="loan-coverage-pct", type="number", value=70, min=0, max=100), dbc.InputGroupText("%")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Loan Interest Rate", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="interest-rate-pct", type="number", value=4.5, step=0.1), dbc.InputGroupText("%")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Depreciation Rate", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="depreciation-pct", type="number", value=8.0, step=0.1), dbc.InputGroupText("%")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Corporate Tax Rate", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="tax-rate-pct", type="number", value=25), dbc.InputGroupText("%")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("Grid CO₂ Intensity", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="grid-co2-intensity", type="number", value=0.401, step=0.01), dbc.InputGroupText("kg/kWh")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                        dbc.Row([
                            dbc.Col(html.Label("CO₂ Price", className="col-form-label"), width=12, sm=5),
                            dbc.Col(dbc.InputGroup([dbc.Input(id="co2-price", type="number", value=35), dbc.InputGroupText("€/ton")]), width=12, sm=7)
                        ], className="mb-3 align-items-center"),
                    ]),
                ]),
                # --- ACTION BUTTONS ---
                dbc.Row([
                    dbc.Col(dbc.Button("Run Simulation", id="btn-run-simulation", color="success", className="w-100"), width=6),
                    dbc.Col(dbc.Button("Download PDF Report", id="btn-pdf-export", color="primary", className="w-100"), width=6),
                ], className="mt-4"),
                dcc.Download(id="download-pdf"),
            ])
        ]),

        # --- RIGHT COLUMN: DASHBOARD (OUTPUTS) ---
        dbc.Col(width=12, lg=8, children=[
            dbc.Row([
                dbc.Col(dbc.Card(id="kpi-npv-card", body=True, className="text-center")),
                dbc.Col(dbc.Card(id="kpi-irr-card", body=True, className="text-center")),
                dbc.Col(dbc.Card(id="kpi-payback-card", body=True, className="text-center")),
                dbc.Col(dbc.Card(id="kpi-co2-card", body=True, className="text-center")),
            ]),
            dbc.Tabs([
                dbc.Tab(dcc.Graph(id="cash-flow-chart"), label="Financial Performance"),
                dbc.Tab(dcc.Graph(id="co2-chart"), label="CO₂ Impact"),
                dbc.Tab(html.Div(id="financial-data-table", className="mt-4"), label="Data Table"),
            ], className="mt-4")
        ]),
    ])
])

# ==============================================================================
# CALLBACKS
# ==============================================================================

# --- MASTER CALLBACK: Run all calculations triggered by BUTTON CLICK ---
@app.callback(
    Output('calculation-results-store', 'data'),
    # TRIGGER:
    Input('btn-run-simulation', 'n_clicks'),
    # GATHER ALL INPUTS AS STATE:
    [State(component_id, 'value') for component_id in [
        'project-name', 'simulation-years', 'pv-size', 'battery-size', 'ev-demand',
        'pv-cost', 'battery-cost', 'infra-cost', 'om-cost-pct', 'grid-price',
        'feed-in-tariff', 'inflation-pct', 'loan-coverage-pct', 'interest-rate-pct',
        'depreciation-pct', 'tax-rate-pct', 'grid-co2-intensity', 'co2-price']],
    prevent_initial_call=True
)
def run_all_calculations(n_clicks, *args):
    # This function now only runs when the "Run Simulation" button is clicked.
    if n_clicks is None or any(v is None for v in args):
        raise dash.exceptions.PreventUpdate

    # --- Calculation logic (unchanged) ---
    inputs = {'project_name': args[0], 'sim_years': args[1], 'pv_size': args[2], 'battery_size': args[3],
        'ev_demand': args[4], 'pv_cost': args[5], 'battery_cost': args[6], 'infra_cost': args[7], 'om_pct': args[8] / 100,
        'grid_price': args[9], 'feed_in_tariff': args[10], 'inflation': args[11] / 100, 'loan_coverage': args[12] / 100,
        'interest_rate': args[13] / 100, 'depreciation_rate': args[14] / 100, 'tax_rate': args[15] / 100,
        'grid_co2_kg': args[16], 'co2_price': args[17]}
    AVG_GEN_PER_KWP, PV_DEGRADATION, SELF_CONSUMPTION_RATIO = 1100, 0.005, 0.4
    years = np.arange(1, inputs['sim_years'] + 1)
    pv_generation = inputs['pv_size'] * AVG_GEN_PER_KWP * (1 - PV_DEGRADATION) ** (years - 1)
    self_consumed_energy = pv_generation * SELF_CONSUMPTION_RATIO
    grid_import = np.maximum(0, inputs['ev_demand'] - self_consumed_energy)
    grid_export = pv_generation - self_consumed_energy
    capex_total = (inputs['pv_size'] * inputs['pv_cost']) + (inputs['battery_size'] * inputs['battery_cost']) + inputs['infra_cost']
    inflation_factor = (1 + inputs['inflation']) ** (years - 1)
    opex_om = (capex_total * inputs['om_pct']) * inflation_factor
    opex_grid_cost = grid_import * inputs['grid_price'] * inflation_factor
    total_opex = opex_om + opex_grid_cost
    revenue_feed_in = grid_export * inputs['feed_in_tariff'] * inflation_factor
    co2_saved_tons = (self_consumed_energy * inputs['grid_co2_kg']) / 1000
    revenue_co2 = co2_saved_tons * inputs['co2_price'] * inflation_factor
    total_revenue = revenue_feed_in + revenue_co2
    annual_depreciation = capex_total * inputs['depreciation_rate']
    loan_amount = capex_total * inputs['loan_coverage']
    interest_payment = loan_amount * inputs['interest_rate']
    ebitda = total_revenue - total_opex
    ebit = ebitda - annual_depreciation
    ebt = ebit - interest_payment
    tax_on_ebt = np.maximum(0, ebt * inputs['tax_rate'])
    net_income = ebt - tax_on_ebt
    free_cash_flow = np.insert(ebit * (1 - inputs['tax_rate']) + annual_depreciation, 0, -capex_total)
    npv = npf.npv(inputs['interest_rate'], free_cash_flow)
    irr = npf.irr(free_cash_flow) * 100
    try: payback_year = np.where(np.cumsum(free_cash_flow) > 0)[0][0]
    except IndexError: payback_year = "N/A"
    df = pd.DataFrame({'Year': years, 'Revenue (€)': total_revenue, 'OPEX (€)': total_opex, 'EBITDA (€)': ebitda,
        'Depreciation (€)': annual_depreciation, 'Net Income (€)': net_income, 'Free Cash Flow (€)': free_cash_flow[1:]})
    co2_df = pd.DataFrame({'Year': years, 'Baseline Emissions (tons)': (inputs['ev_demand'] * inputs['grid_co2_kg']) / 1000,
        'Project Emissions (tons)': (grid_import * inputs['grid_co2_kg']) / 1000})
    co2_df['CO₂ Saved (tons)'] = co2_df['Baseline Emissions (tons)'] - co2_df['Project Emissions (tons)']
    return {'inputs': inputs, 'kpis': {'npv': f"€ {npv:,.0f}", 'irr': f"{irr:.2f} %", 'payback': f"Year {payback_year}",
        'co2_saved': f"{co2_df['CO₂ Saved (tons)'].sum():,.0f} tons"}, 'cash_flow_df': df.to_dict('records'),
        'co2_df': co2_df.to_dict('records'), 'free_cash_flow_data': free_cash_flow.tolist()}

# --- UI UPDATE CALLBACK: Populate dashboard from stored results ---
@app.callback(
    [Output('kpi-npv-card', 'children'), Output('kpi-irr-card', 'children'), Output('kpi-payback-card', 'children'),
     Output('kpi-co2-card', 'children'), Output('cash-flow-chart', 'figure'), Output('co2-chart', 'figure'),
     Output('financial-data-table', 'children')],
    Input('calculation-results-store', 'data')
)
def update_dashboard(data):
    if not data:
        # On initial load, display empty placeholders
        empty_card = [html.H4("---"), html.H5("Run Simulation")]
        empty_fig = go.Figure().update_layout(template="plotly_white", annotations=[dict(text="No data yet. Please run a simulation.", showarrow=False)])
        empty_table = html.Div("Simulation results will be shown here.", className="text-center text-muted mt-5")
        return empty_card, empty_card, empty_card, empty_card, empty_fig, empty_fig, empty_table

    kpis, cash_flow_df, co2_df = data['kpis'], pd.DataFrame(data['cash_flow_df']), pd.DataFrame(data['co2_df'])
    kpi_npv = [html.H4("NPV"), html.H5(kpis['npv'], className="text-success")]
    kpi_irr = [html.H4("IRR"), html.H5(kpis['irr'], className="text-success")]
    kpi_payback = [html.H4("Payback"), html.H5(kpis['payback'], className="text-primary")]
    kpi_co2 = [html.H4("CO₂ Saved"), html.H5(kpis['co2_saved'], className="text-info")]
    fig_cash_flow = go.Figure()
    fig_cash_flow.add_trace(go.Bar(x=cash_flow_df['Year'], y=cash_flow_df['Revenue (€)'], name='Revenue', marker_color='green'))
    fig_cash_flow.add_trace(go.Bar(x=cash_flow_df['Year'], y=cash_flow_df['OPEX (€)'], name='OPEX', marker_color='red'))
    fig_cash_flow.add_trace(go.Scatter(x=cash_flow_df['Year'], y=cash_flow_df['Free Cash Flow (€)'], name='Free Cash Flow', mode='lines+markers', line=dict(color='royalblue', width=3)))
    fig_cash_flow.update_layout(title_text="Annual Financial Performance", barmode='group', template="plotly_white")
    fig_co2 = px.bar(co2_df, x='Year', y=['Baseline Emissions (tons)', 'Project Emissions (tons)'],
                     title='Annual CO₂ Emissions: Baseline vs. Project',
                     labels={'value': 'CO₂ Emissions (tons)'}, template="plotly_white", barmode='group')
    table = dbc.Table.from_dataframe(cash_flow_df.round(0), striped=True, bordered=True, hover=True, responsive=True)
    return kpi_npv, kpi_irr, kpi_payback, kpi_co2, fig_cash_flow, fig_co2, table

# --- PDF EXPORT CALLBACK (unchanged, but now uses the stored data) ---
@app.callback(
    Output("download-pdf", "data"),
    Input("btn-pdf-export", "n_clicks"),
    [State('calculation-results-store', 'data'), State('cash-flow-chart', 'figure'), State('co2-chart', 'figure')],
    prevent_initial_call=True,
)
def generate_pdf_report(n_clicks, data, cash_flow_fig_data, co2_fig_data):
    if n_clicks is None or not data:
        # Prevent download if no simulation has been run
        return dash.no_update

    # --- PDF Generation logic (unchanged) ---
    inputs, kpis, cash_flow_df = data['inputs'], data['kpis'], pd.DataFrame(data['cash_flow_df'])
    df_display = cash_flow_df.copy()
    for col in df_display.columns:
        if '€' in col: df_display[col] = df_display[col].apply(lambda x: f'€ {x:,.0f}')
    table_html = df_display.to_html(index=False, classes='results-table', border=0)
    cash_flow_fig, co2_fig = go.Figure(cash_flow_fig_data), go.Figure(co2_fig_data)
    for fig in [cash_flow_fig, co2_fig]:
        fig.update_layout(margin=dict(l=60, r=40, t=80, b=60), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    cash_flow_img_bytes = cash_flow_fig.to_image(format="png", width=900, height=450, scale=2)
    co2_img_bytes = co2_fig.to_image(format="png", width=900, height=450, scale=2)
    cash_flow_img_b64 = base64.b64encode(cash_flow_img_bytes).decode('utf-8')
    co2_img_b64 = base64.b64encode(co2_img_bytes).decode('utf-8')
    logo_b64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwZDZlZmQiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBjbGFzcz0ibHVjaWRlIGx1Y2lkZS1wb3dlciI+PHBhdGggZD0iTTIgMTJoMjAiLz48cGF0aCBkPSJNOSAxOHYtMWEzIDMgMCAwIDEgMy0zaDRhMyAzIDAgMCAxIDMgM3YxIi8+PHBhdGggZD0iTTcgNnYxYTMgMyAwIDAgMCAzIDNoNGEzIDMgMCAwIDAgMy0zVjYiLz48L3N2Zz4="
    html_string = f"""
    <html>
        <head>
            <title>Feasibility Report</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
                body {{ font-family: 'Lato', sans-serif; margin: 0; padding: 0; font-size: 14px; color: #333; }}
                @page {{ margin: 1in; }}
                header {{ position: fixed; top: -0.6in; left: 0; right: 0; height: 50px; display: flex; align-items: center; border-bottom: 2px solid #0d6efd; padding: 0 0.5in; }}
                .logo {{ height: 40px; width: 40px; margin-right: 15px; }}
                .report-title {{ color: #0d6efd; font-size: 24px; font-weight: bold; }}
                h2 {{ color: #333; border-bottom: 1px solid #ccc; padding-bottom: 8px; margin-top: 40px; font-size: 20px; }}
                .kpi-container {{ display: flex; justify-content: space-between; text-align: center; margin: 30px 0; }}
                .kpi-box {{ padding: 15px; border-radius: 5px; width: 23%; background-color: #f8f9fa; border: 1px solid #dee2e6;}}
                .kpi-title {{ font-size: 0.9em; color: #6c757d; font-weight: bold; }}
                .kpi-value {{ font-size: 1.6em; font-weight: bold; color: #000; margin-top: 5px; }}
                .input-table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                .input-table td {{ border: 1px solid #ddd; padding: 10px; }}
                .input-table td:first-child {{ font-weight: bold; width: 25%; }}
                .results-table {{ border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 12px; }}
                .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                .results-table th {{ background-color: #f2f2f2; font-weight: bold; text-align: center; }}
                .results-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .chart {{ margin-top: 30px; text-align: center; page-break-inside: avoid; }}
                .chart img {{ max-width: 100%; }}
                footer {{ position: fixed; bottom: -0.6in; left: 0; right: 0; height: 30px; text-align: center; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <header>
                <img src="{logo_b64}" class="logo">
                <div class="report-title">Financial Feasibility Report</div>
            </header>
            <footer>Report for {inputs['project_name']} - Generated on {datetime.now().strftime('%Y-%m-%d')}</footer>
            <main>
                <h2>Executive Summary: Key Metrics</h2>
                <div class="kpi-container">
                    <div class="kpi-box"><div class="kpi-title">Net Present Value (NPV)</div><div class="kpi-value">{kpis['npv']}</div></div>
                    <div class="kpi-box"><div class="kpi-title">Internal Rate of Return (IRR)</div><div class="kpi-value">{kpis['irr']}</div></div>
                    <div class="kpi-box"><div class="kpi-title">Payback Period</div><div class="kpi-value">{kpis['payback']}</div></div>
                    <div class="kpi-box"><div class="kpi-title">Lifetime CO₂ Saved</div><div class="kpi-value">{kpis['co2_saved']}</div></div>
                </div>
                <h2>Input Assumptions</h2>
                <table class="input-table">
                    <tr><td>Project Name</td><td>{inputs['project_name']}</td><td>PV System Size</td><td>{inputs['pv_size']} kWp</td></tr>
                    <tr><td>Simulation Years</td><td>{inputs['sim_years']} years</td><td>Battery Size</td><td>{inputs['battery_size']} kWh</td></tr>
                    <tr><td>Annual EV Demand</td><td>{inputs['ev_demand']:,} kWh/yr</td><td>Infrastructure Cost</td><td>€ {inputs['infra_cost']:,}</td></tr>
                    <tr><td>PV System Cost</td><td>€ {inputs['pv_cost']:,}/kWp</td><td>Battery Cost</td><td>€ {inputs['battery_cost']:,}/kWh</td></tr>
                    <tr><td>Grid Electricity Price</td><td>{inputs['grid_price']} €/kWh</td><td>Feed-in Tariff</td><td>{inputs['feed_in_tariff']} €/kWh</td></tr>
                </table>
                <h2>Visualizations</h2>
                <div class="chart"><img src="data:image/png;base64,{cash_flow_img_b64}"></div>
                <div class="chart"><img src="data:image/png;base64,{co2_img_b64}"></div>
                <h2>Financial Data Table</h2>
                {table_html}
            </main>
        </body>
    </html>
    """
    pdf_bytes = HTML(string=html_string).write_pdf()
    return dcc.send_bytes(pdf_bytes, f"Feasibility_Report_{inputs['project_name']}.pdf")

# ==============================================================================
# RUN APPLICATION
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)