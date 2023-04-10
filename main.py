#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import json
import pickle
import hashlib
import pandas as pd
from datetime import datetime
from flask import Flask, Response

import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update

from styles import *
from camera import VideoCamera
from user import User, Degustation


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
               
server = Flask(__name__)
@server.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


with open('pred.txt', 'w') as f: f.writelines(['Nothing'])
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

info = dbc.Alert(id='info', color="success", is_open=False, duration=3000, dismissable=True,style={'marginTop': '10px', 'height':'60px'})
alert = dbc.Alert(id='alert', color="danger", is_open=False, duration=3000, dismissable=True,style={'marginTop': '10px', 'height':'60px'})


login_block = html.Div([html.Div(dcc.Input(id='user', debounce=True, style={'height': '34px', 'borderRadius': '5px', 'marginRight':'10px'}), style={'display': 'inline-block'}),
                        html.Div(dcc.Input(id='pass', type='password', debounce=True, style={'height': '34px', 'borderRadius': '5px', 'marginRight':'10px'}), style={'display': 'inline-block'}),
                        html.Div(html.Button('Log in', id='login_btn', style=log_btn_style), style={'display': 'inline-block'}),
                        html.Div(html.Button('Register', id='register_btn', style=log_btn_style), style={'display': 'inline-block'}),
                       ], style={'paddingRight': '10px', 'textAlign': 'right', 'marginBottom':'10px'})
modal = html.Div(dbc.Modal([dbc.ModalHeader(html.H1(children="Account creation", style={'font-size':'30px', 'textAlign': 'center'})),
                            dbc.ModalBody([html.Div(dcc.Input(id='account_user', placeholder="username", debounce=True, style=account_input_style)),
                                           html.Div(dcc.Input(id='account_pass1', placeholder="password", debounce=True, style=account_input_style)),
                                           html.Div(dcc.Input(id='account_pass2', placeholder="confirm password", debounce=True, style=account_input_style)),
                                           html.Div(html.Button("Save", id="save", style=log_btn_style), style={'textAlign': 'right'})
                                          ], style={'display': 'block'})],
                        id="modal", backdrop=False, style={}))

modal_beer = html.Div(dbc.Modal([dbc.ModalHeader(html.H1(children="New beer degustation", style={'font-size':'30px', 'textAlign': 'center'})),
                                 dbc.ModalBody([html.Div(dcc.Input(id='title', placeholder="event title", debounce=True, style=account_input_style)),
                                                #html.Div(dcc.Input(id='location', placeholder="location", debounce=True, style=account_input_style)),
                                                html.Div(dcc.RadioItems(['1/5', '2/5', '3/5', '4/5', '5/5'], id='rating', inline=True, labelStyle = {'margin-right':'30px'}, style={'marginBottom':'10px'})),
                                                html.Div(dcc.Input(id='lat', type='number', placeholder='000.000', debounce=True, style=account_input_style)),
                                                html.Div(dcc.Input(id='lon', type='number', placeholder='000.000', debounce=True, style=account_input_style)),
                                                html.Div(dcc.Input(id='rem', placeholder="remarks", debounce=True, style=account_input_style)),
                                                html.Div(dcc.Checklist(['Cap added to collection'], id='collection_check', labelStyle = {'margin-left':'0px'})),
                                                html.Div(html.Button("Save", id="save_beer", style=log_btn_style), style={'textAlign': 'right'})
                                          ], style={'display': 'block'})],
                        id="modal_beer", backdrop=False, style={}))

subtitle = html.P(children="Scan / select a beer cap", style={'textAlign': 'center'})
stream_block = html.Div([html.Img(src="/video_feed", id='stream', style={'width': '100%', 'borderRadius': '5px'})])
beers = pd.read_csv('beers.csv', header=0, sep=';')
select_block = dcc.Dropdown(sorted(beers['name'].values), id='caps_select', placeholder="Select a beer", style=input_style)
btn_add = html.Button("Add to my Caps'ules", id='add_btn', style=btn_style)
left_pannel = dbc.Card([stream_block, select_block, btn_add], body=True)


cards = dbc.Card(
    [dbc.CardHeader(
        dbc.Tabs(
            [dbc.Tab(label="General Info", tab_id="tab-info", id="tab-info"),
             dbc.Tab(label="My Caps'ules", tab_id="tab-logbook", id="tab-logbook", disabled=True),
             dbc.Tab(label="Recommandations", tab_id="tab-reco", id="tab-reco", disabled=True),
             dbc.Tab(label="Share", tab_id="tab-share", id="tab-share", disabled=True)],
            id="card-right-tabs",
            active_tab="tab-info")),
    dbc.CardBody(children=html.Div([html.P(children='Scan/Select a beer cap ...', 
                                           style=background_text_style)], 
                                    id="card-right-content"))]
)

right_pannel = dbc.Card([cards], body = True)


app.layout = dbc.Container(fluid = True,
           children = [html.H1(children="Digital Caps'ule Memories", style=title_style),
                       info,
                       alert,
                       login_block, 
                       modal,
                       modal_beer,
                       dbc.Row([dbc.Col(children=left_pannel, width = 5),
                                dbc.Col(children=right_pannel, width = 7)]),
                       dcc.Interval(id='inter', interval=1000),
                       dcc.Store(id='user_info', data=json.dumps({'user':None})),
                       dcc.Store(id='last_pred', data=json.dumps({'pred-'+datetime.now().strftime("%H:%M:%S"):'Nothing'})),
                       dcc.Store(data={"df":beers.to_dict("records")}, id='beer_dataset'),
                       html.Footer(children=[html.Hr(), html.P('Team #18 - Pythonistas', style={'paddingRight':'20px'})],
                                   style=footer_style),
                       ])


@app.callback(
    Output("modal", "is_open"),
    Output("info", "is_open"),
    Output("info", "children"),
    Output("alert", "is_open"),
    Output("alert", "children"),
    Output("user_info", "data"),
    Output("tab-logbook", "disabled"),
    Output("tab-reco", "disabled"),
    Output("tab-share", "disabled"),
    Output("modal_beer", "is_open"),
    Input("register_btn", "n_clicks"), 
    Input("save", "n_clicks"),
    Input("login_btn", "n_clicks"),
    Input("add_btn", "n_clicks"),
    Input("save_beer", "n_clicks"),
    State("account_user", "value"),
    State("account_pass1", "value"),
    State("account_pass2", "value"),
    State("user", "value"),
    State("pass", "value"),
    State("caps_select", "value"), 
    State("user_info", "data"),
    State("card-right-tabs", "active_tab"),
    State("title", "value"),
    State("lat", "value"),
    State("lon", "value"),
    State("beer_dataset", "data"),
    prevent_initial_callbacks=True
)
def create_account(n_reg, n_save, n_login, n_add, n_save_beer, pseudo, pass1, pass2, pseudo_log, pass_log, beer_selected, user_info, active_tab, title, lat, lon, beer_csv):
    changed_id = ctx.triggered_id

    if changed_id == 'save':
        csv = pd.read_csv('users.csv', header=0)
        if pass1 == pass2 and pseudo not in csv['pseudo'].values:
            hashed_pass = hashlib.sha256(pass1.encode()).hexdigest()
            csv = pd.concat([csv, pd.DataFrame.from_dict({'pseudo':[pseudo], 'password':[hashed_pass], 'lastlog':[datetime.now()]})], ignore_index=True)
            csv.to_csv('users.csv', index=False)
            user_cls = User(pseudo)
            with open('data/'+pseudo, 'wb') as outp:
                pickle.dump(user_cls, outp, pickle.HIGHEST_PROTOCOL)
            info_txt = html.P('Account successfully created')
            return(False, True, info_txt, no_update, no_update, no_update, no_update, no_update, no_update, no_update)
        else:
            print('Passwords does not match or username already used')
            return(no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update)
    
    elif changed_id == 'register_btn':
        return (True, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update)

    elif changed_id == 'login_btn':
        csv = pd.read_csv('users.csv', header=0)
        if pseudo_log in csv['pseudo'].values:
            hashed_passw = csv.loc[csv['pseudo']==pseudo_log, 'password']
            if hashlib.sha256(pass_log.encode()).hexdigest() == hashed_passw.iloc[0]:
                print("Password is correct!")
                info_txt = html.P('Successfully logged as : '+pseudo_log)
                csv.loc[csv["pseudo"]==pseudo_log, "lastlog"] = datetime.now()
                csv.to_csv("users.csv", index=False)
                return(no_update, True, info_txt, no_update, no_update, json.dumps({'user':pseudo_log}), False, False, False, no_update)
            else:
                print("Password not matching")
                info_txt = html.P(f'Wrong user/password combination')
                return(no_update, no_update, no_update, True, info_txt, no_update, no_update, no_update, no_update, no_update)
        else:
            print(f'User {pseudo_log} not found')
            info_txt = html.P(f'User "{pseudo_log}" not found')
            return(no_update, no_update, no_update, True, info_txt, no_update, no_update, no_update, no_update, no_update)

    elif changed_id == 'add_btn' and active_tab == 'tab-info':
        user = json.loads(user_info)['user']
        if beer_selected is not None and user is not None:
            return (no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, True)
        else:
            info_txt = html.P(f'Please log-in and select/scan a cap ...')
            return (no_update, no_update, no_update, True, info_txt, no_update, no_update, no_update, no_update, no_update)

    elif changed_id == 'save_beer':
        user = json.loads(user_info)['user']
        with open('data/'+pseudo_log, 'rb') as f:
            user_data = pickle.load(f)

        df = pd.DataFrame(beer_csv["df"])
        beer_info = df.loc[df['name']==beer_selected]
        if lat!='' and lon!='': new = Degustation(title, beer_selected, beer_info['style'].item(), loc=str(lat)+','+str(lon))
        else: new = Degustation(title, beer_selected, beer_info['style'].item())
        print(new)
        user_data.new_drink(new)
        with open('data/'+pseudo_log, 'wb') as outp:
                pickle.dump(user_data, outp, pickle.HIGHEST_PROTOCOL)

        info_txt = html.P(f'Adding to my history ...')
        return (no_update, True, info_txt, no_update, no_update, no_update, no_update, no_update, no_update, False)

    else:
        return (no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update)


@app.callback(
    Output('last_pred', 'data'),
    Output('caps_select', 'value'),
    Input("inter", "n_intervals"),
    Input("caps_select", "value"), 
    State('last_pred', 'data'),
    prevent_initial_callbacks=True
)
def update_last_pred(n, new_select, last_pred):
    changed_id = ctx.triggered_id
    dico = json.loads(last_pred)

    if changed_id == 'inter':
        ex_pred = [i[1] for i in sorted(dico.items()) if i[0].startswith('pred-')][-1]
        with open('pred.txt') as f:
            pred = f.readline()
            pred = pred.strip().capitalize()

        if pred != ex_pred and pred != 'Unknown':
            dico['pred-'+datetime.now().strftime("%H:%M:%S")] = pred
            return(json.dumps(dico), pred)
        else:
            return(no_update, no_update)

    if changed_id == 'caps_select':
        dico['select-'+datetime.now().strftime("%H:%M:%S")] = new_select
        return(json.dumps(dico), no_update)
        
    else:
        return(no_update, no_update)


@app.callback(
    Output("card-right-tabs", "active_tab"),
    Output('card-right-content', 'children'),
    Input("card-right-tabs", "active_tab"),
    Input("last_pred", "data"), 
    State("beer_dataset", "data"),
    State("user_info", "data"),
    prevent_initial_callbacks=True
)
def update_right_panel(active_tab, last_pred, beer_csv, user_info):
    changed_id = ctx.triggered_id

    if changed_id==last_pred or active_tab=='tab-info':
        df = pd.DataFrame(beer_csv["df"])
        if last_pred is not None:
            dico = json.loads(last_pred)
            last_in = [i[1] for i in sorted(dico.items(), key=lambda x: x[0].split('-')[1])][-1]
            if last_in != 'Nothing':
                infos = df.loc[df['name']==last_in]
                child = html.Div([html.P(f"Name : {infos['name'].item()}"),
                                html.P(f"Vol : {infos['abv'].item()}"),
                                html.P(f"IBU : {infos['ibu'].item()}"),
                                html.P(f"Style : {infos['style'].item()}"),
                                html.P(f"Brewery : {infos['brewery'].item()}"),
                                html.P(f"Country : {infos['country'].item()}"),
                                html.P(f"Degustation : {infos['degustation'].item()}"),
                ])
                return('tab-info', child)
            else: 
                child = [html.P(children='Scan/Select a beer cap ...', style=background_text_style)]
                return('tab-info', child)

    elif active_tab=='tab-logbook':
        df = pd.DataFrame(beer_csv["df"])
        my_df = pd.DataFrame(columns=['Lat', 'Lon', 'Date', 'Beer', 'Title', 'Type', 'Remarks'])
        with open('data/'+json.loads(user_info)['user'], 'rb') as f:
            user_data = pickle.load(f)
        
        print(user_data)
        child_list = []
        for degu in user_data.get_beers():
            if degu.loc is not None:
                tmp = pd.DataFrame([[float(degu.loc.split(',')[0]), float(degu.loc.split(',')[1]), degu.time, degu.beer, degu.title, degu.style, degu.comments]], columns=my_df.columns)
                my_df = pd.concat([my_df, tmp], ignore_index=True)
            infos = df.loc[df['name']==degu.beer]
            child_list.append(html.Div([html.P(f'{str(degu.time).split(".")[0]}', style={'display': 'inline-block', 'float': 'left', 'marginTop' : '12px', 'marginLeft' : '6px'}),
                                        html.P(f'{degu.title} - {degu.beer}', style={'display': 'inline-block','marginTop' : '12px'}),
                                        html.Img(src=infos['Img'].item(), style={'display': 'inline-block', 'float': 'right', 'width':'52px', 'height':'52px', 'borderRadius': '5px'})
                                        ], style=history_style))

        if my_df.shape[0]>0:
            fig = px.scatter_mapbox(my_df, lat="Lat", lon="Lon", hover_name="Date", hover_data=["Beer", "Type", "Remarks"], color="Type", zoom=3, height=300)
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right",x=1))
            map = html.Div([dcc.Graph(figure=fig, id='my-graph')], style={'borderRadius': '5px'})
            child_list.append(map)
        child_list.append(html.Div([html.P(user_data.stats(True), style={'display': 'inline-block'}),
                                    html.P(user_data.stats(), style={'display': 'inline-block', 'float': 'right'})]))
        return(no_update, child_list)

    elif active_tab=='tab-reco':
        child = html.Div()
        return(no_update, child)

    elif active_tab=='tab-share':
        with open('data/'+json.loads(user_info)['user'], 'rb') as f:
            user_data = pickle.load(f)
        child = html.Div([html.Img(src=user_data.generate_banner(), style={'borderRadius': '5px', 'width':'100%'}),
                          html.Button("Copy to clipboard", style=btn_style)])
        return(no_update, child)

    return(no_update, no_update)




if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
