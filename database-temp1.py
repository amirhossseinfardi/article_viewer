# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_table
import os
import numpy as np
import io
import base64
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
from analysis_country import createGraph
from analysis_author import createGraphAuthor
from analysis_keyword import createWordcloud

conn = sqlite3.connect('temp.db', check_same_thread=False)
cursor = conn.cursor()

# get year list
sql_year = '''
SELECT year
from year_list
'''
df_years = pd.read_sql_query(sql_year, conn)

# get country list for dropdown menu
sql_country = '''
SELECT country_name
from country_list
'''
df_country_dropdown = pd.read_sql_query(sql_country, conn)
country_dropdown_list = []
temp_dic = {
    'label': 'All Country',
    'value': '*'
}
country_dropdown_list.append(temp_dic)
for i, rows in df_country_dropdown.iterrows():
    temp_dic = {
        'label': rows.country_name,
        'value': rows.country_name
    }
    country_dropdown_list.append(temp_dic)

# get number of paper
# sqlite read data counting
countPaper = 0
sql_jn = """
    SELECT journal_name
    FROM journal_list
    """
table = cursor.execute(sql_jn).fetchall()
for row in table:
    jn = str(row[0])
    print(jn)
    sql_count = """SELECT COUNT (*) FROM {}""".format('paper_list_' + jn.replace(" ", "_"))
    cursor.execute(sql_count)
    rowcount = cursor.fetchone()[0]
    print(rowcount)
    countPaper = countPaper + rowcount
couting_output = 'Total number of paper in database is: ' + str(countPaper)
# finished read number of paper

# def generate_table(dataframe, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])
df_key = pd.DataFrame()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        html.H4(children='Search in SamenPayesh database'),
        dcc.Input(id='input-1-state', type='text', value='CFD'),
        html.Div([
            dcc.Dropdown(
                id='country_dropdown_menu',
                options=country_dropdown_list,
                value=[],
                multi=True
            )
        ]),
        html.Button(id='submit-button-state', n_clicks=0, children='Search', style={'background-color': '#44c767'}),
        html.H5(children=couting_output),
        html.H5(children='Paper Dates', style={'margin-top': '30px'}),
        html.Div([
            dcc.RangeSlider(
                id='year-slider',
                min=int(df_years['year'].min()),
                max=int(df_years['year'].max()),
                step=1,
                value=[2017, 2020],
                allowCross=False,
                marks={str(year): str(year) for year in df_years['year'].unique()}
            ),
            html.Div(id='output-container-range-slider')
        ]),
        html.H5(id='result_count', style={'margin-top': '20px'}),
        html.Div(
            html.Div([
                html.Div([
                    # html.Div(id='output-table')
                    dash_table.DataTable(
                        id='output-table',
                        # data=df_sql_doi.to_dict('records'),
                        # columns=[{'id': c, 'name': c} for c in df_sql_doi.columns],
                        page_size=10,
                        style_cell={'textAlign': 'left', 'font-family': 'sans-serif', 'whiteSpace': 'normal',
                                    'height': 'auto'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'paper_doi'},
                             'width': '20%'}
                            # {'if': {'column_id': 'paper_doi'},
                            #  'overflow': 'hidden',
                            #  'textOverflow': 'ellipsis',
                            #  'maxWidth': 0}
                        ],
                        row_selectable="multi",
                        selected_rows=[]
                    )

                ], className="eight columns",
                    style={'border': '2px solid #73AD21'}),

                html.Div([
                    html.Div(id='output-name', style={'font-weight': 'bold'}),
                    html.Hr(style={'margin': '2px'}),
                    html.Div(id='abstract-output-author', style={'font-style': 'italic'}),
                    html.Hr(style={'margin': '2px'}),

                    html.Div(id='output-date'),
                    html.Hr(style={'margin': '2px'}),
                    html.Div(id='abstract-output-country'),
                    html.Hr(style={'margin': '2px'}),
                    html.Div(
                        id='output-abstract'
                        , style={'text-align': 'justify', 'text-justify': 'inter-word'}
                    ),
                    html.Hr(style={'margin': '2px'}),
                    html.Div(
                        id='output-doi'
                        # , style={'border': '2px solid #b78846'}
                    ),
                    html.Hr(style={'margin': '2px'}),
                    html.A(id='link-paper', children=[
                        html.Button('Get Paper', id='get-paper', n_clicks=0, style={'background-color': '#44c767'}),
                    ],
                           # href='www.google.com',
                           target="_blank",
                           # download=''
                           )
                ]
                    , className="four columns"),
            ],
                style={'margin-top': '30px'}),
            className='row'),

        # html.Div(id='output-density',
        #          style={'width': '500px', 'margin': 'auto', 'margin-top': '80px', 'textAlign': 'center',
        #                 'border': '2px solid #73AD21'}),
        html.Div([
            dash_table.DataTable(
                id='datatable-temp',
                # data=df_key.to_dict('records'),
                # columns=[{'id': c, 'name': c} for c in df_key.columns],
                page_size=10,
                row_selectable="multi",
                selected_rows=[],
                style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )

        ], style={'margin-top': '30px'}),
        html.Button(id='keyword-button-state', n_clicks=0, children='Show Article',
                    style={'background-color': '#44c767'}),
        html.Div(id='keyword-list',
                 style={'margin': 'auto', 'margin-top': '80px', 'border': '2px solid #73AD21'}),
        html.Div(id='output-density-article',
                 style={'margin': 'auto', 'margin-top': '80px', 'border': '2px solid #73AD21'}),
        html.Div([
            html.Div(id='output-author',
                     className='six columns',
                     style={'width': '50%', 'float': 'left', 'border': '2px solid #73AD21'}),

            html.Div(id='output-country',
                     className='six columns',
                     style={'margin-left': '10%', 'border': '2px solid #73AD21'})

        ], style={'width': '100%', 'display': 'flex', 'margin-top': '30px'}),

        html.Div([
            html.Button('Show Country Relation', id='output-country-relation', n_clicks=0
                        , className='six columns'
                        , style={'width': '50%', 'float': 'left'}
                        ),
            html.Button('Show Author Relation', id='output-author-relation', n_clicks=0
                        , className='six columns'
                        , style={'margin-left': '10%'}
                        ),
            html.Button('Show Wordcloud', id='output-wordcloud-relation', n_clicks=0
                        , className='six columns'
                        , style={'margin-left': '10%'}
                        )

        ], style={'width': '100%', 'display': 'flex', 'margin-top': '30px'}),

        html.Div([
            html.Img(id='output-relation-graph'
                     )
            # , html.Button('Show Author Relation', id='output-author-relation', n_clicks=0
            #             , className='six columns'
            #             , style={'margin-left': '10%'}
            #             )

        ], style={'width': '100%', 'display': 'flex', 'margin-top': '30px'})

    ])


# @app.callback(Output('output-count', 'children'))
# def showCounting():
#     # sqlite read data counting
#     countPaper = 0
#     sql_jn = """
#         SELECT journal_name
#         FROM journal_list
#         """
#     for row in cursor.execute(sql_jn):
#         jn = str(row[0])
#         sql_count = """SELECT COUNT (*) FROM {}""".format('paper_list_' + jn.replace(" ", "_"))
#         cursor.execute(sql_count)
#         rowcount = cursor.fetchone()[0]
#         countPaper = countPaper + rowcount
#     output = 'Total number of paper in database is: ' + str(countPaper)
#     return output


@app.callback([Output('output-table', 'data'),
               Output('output-table', 'columns'),
               Output('output-table', 'selected_rows'),
               Output('datatable-temp', 'data'),
               Output('datatable-temp', 'columns'),
               # Output('keyword-list', 'children'),
               Output('output-country', 'children'),
               Output('result_count', 'children')
               ],
              [Input('submit-button-state', 'n_clicks')],
              [State('input-1-state', 'value'),
               State('year-slider', 'value'),
               State('country_dropdown_menu', 'value')]
              )
def generate_table(n_clicks, input1, user_year, selected_country_dropdown, max_rows=10):
    # sqlite read
    year_list = list(range(user_year[0], user_year[1] + 1, 1))
    if len(year_list) == 1:
        year_list.append(year_list[0])

    # if not selected_country_dropdown or selected_country_dropdown[0] == '*':
    #     selected_country_dropdown_list = '*'
    #     sql_selected_country_dropdown = ''
    # elif len(selected_country_dropdown) == 1:
    #     selected_country_dropdown_list = selected_country_dropdown[0]
    #     sql_selected_country_dropdown = '''
    #     AND
    #     country_id IN ( SELECT country_id
    #     FROM country_list
    #     WHERE country_name = '{temp_country}'
    #     )
    #     '''.format(temp_country=selected_country_dropdown[0])
    #     print('len is zero')
    # else:
    #     selected_country_dropdown_list = selected_country_dropdown
    #     sql_selected_country_dropdown = '''
    #     AND
    #     country_id IN ( SELECT country_id
    #     FROM country_list
    #     WHERE country_name IN {temp_country}
    #     )
    #     '''.format(temp_country=str(tuple(selected_country_dropdown_list)))
    # sql_selected_country_dropdown = str(tuple(selected_country_dropdown_list))

    keylist = []
    country_list = []
    df_key = pd.DataFrame(columns=['keyword'])
    df_countr = pd.DataFrame(columns=['country_name'])
    df_sql_doi = pd.DataFrame()
    df_full_sql_doi = pd.DataFrame()
    # get journal name available in database
    sql_jn = """
    SELECT journal_name
    FROM journal_list
    """
    for row in cursor.execute(sql_jn):
        jn = str(row[0])
        print(jn)

        # prepare sqlite
        if not selected_country_dropdown or selected_country_dropdown[0] == '*':
            selected_country_dropdown_list = '*'
            sql_selected_country_dropdown = ''
        elif len(selected_country_dropdown) == 1:
            selected_country_dropdown_list = selected_country_dropdown[0]
            sql_selected_country_dropdown = '''
            AND
            paper_id IN (SELECT paper_id
            FROM {temp_paper_country_list}
            WHERE country_id IN ( SELECT country_id
            FROM country_list
            WHERE country_name = '{temp_country}'
            ))
            '''.format(temp_country=selected_country_dropdown[0],
                       temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
            print('len is zero')
        else:
            selected_country_dropdown_list = selected_country_dropdown
            sql_selected_country_dropdown = '''
            AND
            paper_id IN (SELECT paper_id
            FROM {temp_paper_country_list}
            WHERE country_id IN ( SELECT country_id
            FROM country_list
            WHERE country_name IN {temp_country}
            ))
            '''.format(temp_country=str(tuple(selected_country_dropdown_list)),
                       temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
            # sql_selected_country_dropdown = str(tuple(selected_country_dropdown_list))

        # select id of each keyword based on different journal name
        sql_final = """
         SELECT keyword_id
         FROM {temp_jn}
         WHERE paper_id IN (SELECT paper_id
         FROM {temp_paper_list}
         WHERE paper_abstract LIKE '%{user_search_temp}%'
         )
         AND
         paper_id IN (SELECT paper_id
         FROM {temp_paper_list}
         WHERE paper_year IN ( SELECT year_id
         FROM year_list
         WHERE year IN {temp_year}
         ))
         {temp_country}
         ;""".format(temp_jn='paper_keyword_' + jn.replace(" ", "_"),
                     temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                     user_search_temp=input1,
                     temp_year=str(tuple(year_list)),
                     temp_country=sql_selected_country_dropdown)

        df2 = pd.read_sql_query(sql_final, conn)
        # get keyword name of each id. loop for select duplicate keyword
        for kkk in df2['keyword_id']:
            # get keyword
            sql_keyword = '''
            SELECT keyword
            FROM keyword_list
            WHERE keyword_id = {}'''.format(str(kkk))
            df_keyword = pd.read_sql_query(sql_keyword, conn)
            keylist.append(df_keyword.iloc[0]['keyword'])

        # get name and doi of article
        sql_doi = """
        SELECT paper_doi, paper_name, paper_abstract
        FROM {temp_paper_list}
        WHERE paper_id IN (SELECT paper_id
        FROM {temp_paper_list}
        WHERE paper_abstract LIKE '%{user_search_temp}%'
        )
        AND
         paper_id IN (SELECT paper_id
         FROM {temp_paper_list}
         WHERE paper_year IN ( SELECT year_id
         FROM year_list
         WHERE year IN {temp_year}
         ))
         {temp_country}
        ;""".format(
            temp_paper_list='paper_list_' + jn.replace(" ", "_"),
            user_search_temp=input1,
            temp_year=str(tuple(year_list)),
            temp_country=sql_selected_country_dropdown
        )
        df_full_sql_doi = df_full_sql_doi.append(pd.read_sql_query(sql_doi, conn))

        # get country first ID and then get name through the loop
        sql_country = """
                 SELECT country_id
                 FROM {temp_jn}
                 WHERE paper_id IN (SELECT paper_id
                 FROM {temp_paper_list}
                 WHERE paper_abstract LIKE '%{user_search_temp}%'
                 )
                 AND
                 paper_id IN (SELECT paper_id
                 FROM {temp_paper_list}
                 WHERE paper_year IN ( SELECT year_id
                 FROM year_list
                 WHERE year IN {temp_year}
                 ))
                 {temp_country}
                 ;""".format(temp_jn='paper_country_' + jn.replace(" ", "_"),
                             temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                             user_search_temp=input1,
                             temp_year=str(tuple(year_list)),
                             temp_country=sql_selected_country_dropdown)
        print(sql_country)
        df4 = pd.read_sql_query(sql_country, conn)
        for nnn in df4['country_id']:
            # get country name
            sql_country = '''
                                SELECT country_name
                                FROM country_list
                                WHERE country_id = {}'''.format(str(nnn))
            df_country = pd.read_sql_query(sql_country, conn)
            country_list.append(df_country.iloc[0]['country_name'])

    # end of sql. start of cleaning data
    df_key['keyword'] = keylist
    try:
        df_key['keyword'] = df_key['keyword'].str.lower()
    except:
        pass
    # df_key['keyword'] = df_key['keyword'].drop_duplicates()
    df_key = df_key.keyword.value_counts().rename_axis('keyword').reset_index(name='counts')
    global df_key_share
    df_key_share = df_key
    print('*************************')
    print(df_key_share)
    # merge same country
    dict_country = {'the Netherlands': 'Netherlands',
                    'The Netherlands': 'Netherlands',
                    'Aero Engine (Group) Corporation of China': 'China',
                    'PR China': 'China',
                    'United States': 'USA',
                    'United Kingdom': 'UK',
                    "People's Republic of China": 'China',
                    'Republic of Singapore': 'Singapore',
                    'United States of America': 'USA',
                    'P.R. China': 'China',
                    }

    df_countr['country_name'] = country_list
    df_countr['country_name'] = df_countr['country_name'].replace(dict_country)
    df_countr = df_countr.country_name.value_counts().rename_axis('country_name').reset_index(name='counts')
    # df_key = df_key.columns['keyword', 'count']
    # print(df_sql_doi)
    # output1 = html.Table([
    #     html.Thead(
    #         html.Tr([html.Th(col) for col in df_sql_doi.columns])
    #     ),
    #     html.Tbody([
    #         html.Tr([
    #             html.Td(df_sql_doi.iloc[i][col]) for col in df_sql_doi.columns
    #         ]) for i in range(min(len(df_sql_doi), max_rows))
    #     ])
    # ])
    # output2 = html.Table([
    #     html.Thead(
    #         html.Tr([html.Th(col) for col in df_key.columns])
    #     ),
    #     html.Tbody([
    #         html.Tr([
    #             html.Td(df_key.iloc[i][col]) for col in df_key.columns
    #         ]) for i in range(min(len(df_key), max_rows))
    #     ])
    # ], style={'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '50px'})

    # temporary disabled

    # output2 = dash_table.DataTable(
    #     id='datatable-temp',
    #     data=df_key.to_dict('records'),
    #     columns=[{'id': c, 'name': c} for c in df_key.columns],
    #     page_size=10,
    #     row_selectable="single",
    #     selected_rows=[],
    #     style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
    #     style_header={
    #         'backgroundColor': 'rgb(230, 230, 230)',
    #         'fontWeight': 'bold'
    #     }
    # )
    output2_data = df_key.to_dict('records')
    output2_column = [{'id': c, 'name': c} for c in df_key.columns]
    # output1 = dash_table.DataTable(
    #     data=df_sql_doi.to_dict('records'),
    #     columns=[{'id': c, 'name': c} for c in df_sql_doi.columns],
    #     page_size=10,
    #     style_cell={'textAlign': 'left', 'font-family': 'sans-serif', 'whiteSpace': 'normal', 'height': 'auto'},
    #     style_header={
    #         'backgroundColor': 'rgb(230, 230, 230)',
    #         'fontWeight': 'bold'
    #     },
    #     style_cell_conditional=[
    #         {'if': {'column_id': 'paper_doi'},
    #          'width': '20%'}
    #         # {'if': {'column_id': 'paper_doi'},
    #         #  'overflow': 'hidden',
    #         #  'textOverflow': 'ellipsis',
    #         #  'maxWidth': 0}
    #     ]
    # )
    global df_sql_share
    df_full_sql_doi = df_full_sql_doi.reset_index(drop=True)
    df_sql_share = df_full_sql_doi
    df_sql_doi = df_full_sql_doi.drop(['paper_doi', 'paper_abstract'], 1)
    output1_data = df_sql_doi.to_dict('records')
    output1_column = [{'id': c, 'name': c} for c in df_sql_doi.columns]
    output5 = 'result number is : ' + str(len(df_sql_doi.index))
    output4 = dash_table.DataTable(
        data=df_countr.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df_countr.columns],
        page_size=10,
        style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    return output1_data, output1_column, [], output2_data, output2_column, output4, output5


@app.callback([Output('output-density-article', 'children'),
               Output('keyword-list', 'children')
               ],
              [Input('datatable-temp', 'derived_virtual_row_ids'),
               Input('keyword-button-state', 'n_clicks'),
               Input('datatable-temp', 'derived_virtual_selected_rows')],
              [State('year-slider', 'value'),
               # State('output-density-article', 'selected_row_ids'),
               State('input-1-state', 'value')])
def generate_table(xxx, n_clicks, selected_row_ids, user_year, input1):
    # selected_id_set = set(selected_row_ids or [])
    print(selected_row_ids)
    df_sql_article = pd.DataFrame()
    df_sql_keyword = pd.DataFrame()
    if selected_row_ids is None or len(selected_row_ids) == 0:
        # dff = df
        output = ' nothing is selected '
        output1 = ' no keyword selected '
        print('i am in none')
        # pandas Series works enough like a list for this to be OK
        # row_ids = df['id']
    else:
        print(' i am in the else', selected_row_ids[0])
        print(df_key_share)
        selected_search = df_key_share.loc[selected_row_ids[0]]['keyword']
        print(selected_search)
        print(type(selected_search))
        # dff = df.loc[selected_id_set]
        # sqlite read
        year_list = list(range(user_year[0], user_year[1] + 1, 1))
        if len(year_list) == 1:
            year_list.append(year_list[0])

        sql_jn = """
            SELECT journal_name
            FROM journal_list
            """
        for row in cursor.execute(sql_jn):
            jn = str(row[0])
            # select id of each paper based on different journal name
            sql_final = """
            SELECT paper_doi, paper_name
            FROM {temp_paper_list}
            WHERE paper_id IN (SELECT paper_id
            FROM {temp_paper_list}
            WHERE paper_abstract LIKE '%{user_search_temp}%'
            )
            AND
             paper_id IN (SELECT paper_id
             FROM {temp_jn}
             WHERE keyword_id IN ( SELECT keyword_id
             FROM keyword_list
             WHERE keyword LIKE '%{selected_search_temp}%'
             ))
            AND
             paper_id IN (SELECT paper_id
             FROM {temp_paper_list}
             WHERE paper_year IN ( SELECT year_id
             FROM year_list
             WHERE year IN {temp_year}
             ))
                 ;""".format(temp_jn='paper_keyword_' + jn.replace(" ", "_"),
                             temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                             user_search_temp=input1,
                             temp_year=str(tuple(year_list)),
                             selected_search_temp=selected_search)
            df_sql_article = df_sql_article.append(pd.read_sql_query(sql_final, conn))

            # get list of keyword i searched
            keyword_sql = """
                    SELECT keyword
                    FROM keyword_list
                    WHERE 
                    keyword_id IN (
                        SELECT keyword_id
                        FROM {temp_paper_keyword}
                        WHERE paper_id IN (
                            SELECT paper_id
                            FROM {temp_paper_list}
                            WHERE paper_abstract LIKE '%{user_search_temp}%'
                                           )
                                    )
                    AND
                    keyword_id IN (
                        SELECT keyword_id
                        FROM keyword_list
                        WHERE keyword LIKE '%{selected_search_temp}%'
                                        )
                    ;""".format(
                selected_search_temp=selected_search,
                temp_paper_keyword='paper_keyword_' + jn.replace(" ", "_"),
                user_search_temp=input1,
                temp_paper_list='paper_list_' + jn.replace(" ", "_")
            )
            kljfkl = '''
                            AND
                 keyword_id IN (
                        SELECT keyword_id
                        FROM keyword_list
                        WHERE keyword LIKE '%{selected_search_temp}%'
                                        )
                    '''
            df_sql_keyword = df_sql_keyword.append(pd.read_sql_query(keyword_sql, conn))

        print(df_sql_article)
        df_sql_article = df_sql_article.reset_index(drop=True)
        output = dash_table.DataTable(
            data=df_sql_article.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_sql_article.columns],
            page_size=10,
            style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

        df_list_keyword = df_sql_keyword['keyword'].tolist()
        keyword_string = ', '.join(df_list_keyword)
        output1 = keyword_string
    return output, output1


# update author table that variable by keyword selection


@app.callback(Output('output-author', 'children'),
              [Input('datatable-temp', 'derived_virtual_row_ids'),
               Input('keyword-button-state', 'n_clicks'),
               Input('datatable-temp', 'derived_virtual_selected_rows')],
              [State('year-slider', 'value'),
               State('input-1-state', 'value'),
               State('country_dropdown_menu', 'value')])
def generate_table_author(xxx, n_clicks, selected_row_ids, user_year, input1, selected_country_dropdown):
    # update year list -----------------
    year_list = list(range(user_year[0], user_year[1] + 1, 1))
    if len(year_list) == 1:
        year_list.append(year_list[0])
    # year updated ----------------

    # define variable for author -------------
    author_list = []
    df_auth = pd.DataFrame(columns=['author_name'])
    # defined -------------------

    print('selected row from author', selected_row_ids)
    # show all author based on search. no keyword selected --------
    if selected_row_ids is None or len(selected_row_ids) == 0:
        # get all author based on search
        # get journal name available in database
        sql_jn = """
            SELECT journal_name
            FROM journal_list
            """
        for row in cursor.execute(sql_jn):
            jn = str(row[0])

            # prepare sqlite
            if not selected_country_dropdown or selected_country_dropdown[0] == '*':
                selected_country_dropdown_list = '*'
                sql_selected_country_dropdown = ''
            elif len(selected_country_dropdown) == 1:
                selected_country_dropdown_list = selected_country_dropdown[0]
                sql_selected_country_dropdown = '''
                        AND
                        paper_id IN (SELECT paper_id
                        FROM {temp_paper_country_list}
                        WHERE country_id IN ( SELECT country_id
                        FROM country_list
                        WHERE country_name = '{temp_country}'
                        ))
                        '''.format(temp_country=selected_country_dropdown[0],
                                   temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
                print('len is zero')
            else:
                selected_country_dropdown_list = selected_country_dropdown
                sql_selected_country_dropdown = '''
                        AND
                        paper_id IN (SELECT paper_id
                        FROM {temp_paper_country_list}
                        WHERE country_id IN ( SELECT country_id
                        FROM country_list
                        WHERE country_name IN {temp_country}
                        ))
                        '''.format(temp_country=str(tuple(selected_country_dropdown_list)),
                                   temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
                # sql_selected_country_dropdown = str(tuple(selected_country_dropdown_list))

            # select id of each author based on different journal name
            sql_author = """
                     SELECT author_id
                     FROM {temp_jn}
                     WHERE paper_id IN (SELECT paper_id
                     FROM {temp_paper_list}
                     WHERE paper_abstract LIKE '%{user_search_temp}%'
                     )
                     AND
                     paper_id IN (SELECT paper_id
                     FROM {temp_paper_list}
                     WHERE paper_year IN ( SELECT year_id
                     FROM year_list
                     WHERE year IN {temp_year}
                     ))
                     {temp_country}
                     ;""".format(temp_jn='paper_author_' + jn.replace(" ", "_"),
                                 temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                                 user_search_temp=input1,
                                 temp_year=str(tuple(year_list)),
                                 temp_country=sql_selected_country_dropdown)
            df3 = pd.read_sql_query(sql_author, conn)
            # loop through author ID cause i need duplicated one
            for mmm in df3['author_id']:
                # get author name
                sql_author = '''
                                    SELECT author_name
                                    FROM author_list
                                    WHERE author_id = {}'''.format(str(mmm))
                df_author = pd.read_sql_query(sql_author, conn)
                author_list.append(df_author.iloc[0]['author_name'])

        # add author to dataframe and then counting
        df_auth['author_name'] = author_list
        df_auth = df_auth.author_name.value_counts().rename_axis('author_name').reset_index(name='counts')

        # send table to HTML
        output = dash_table.DataTable(
            data=df_auth.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_auth.columns],
            page_size=10,
            style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

    else:
        # update author table based on search and also keyword selection
        print(' i am in the else author', selected_row_ids[0])
        selected_search = df_key_share.loc[selected_row_ids[0]]['keyword']
        print(selected_search)
        # update year list ----------
        year_list = list(range(user_year[0], user_year[1] + 1, 1))
        if len(year_list) == 1:
            year_list.append(year_list[0])
        # year updated
        # get author
        sql_jn = """
            SELECT journal_name
            FROM journal_list
            """
        for row in cursor.execute(sql_jn):
            jn = str(row[0])

            # prepare sqlite
            if not selected_country_dropdown or selected_country_dropdown[0] == '*':
                selected_country_dropdown_list = '*'
                sql_selected_country_dropdown = ''
            elif len(selected_country_dropdown) == 1:
                selected_country_dropdown_list = selected_country_dropdown[0]
                sql_selected_country_dropdown = '''
                                    AND
                                    paper_id IN (SELECT paper_id
                                    FROM {temp_paper_country_list}
                                    WHERE country_id IN ( SELECT country_id
                                    FROM country_list
                                    WHERE country_name = '{temp_country}'
                                    ))
                                    '''.format(temp_country=selected_country_dropdown[0],
                                               temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
                print('len is zero')
            else:
                selected_country_dropdown_list = selected_country_dropdown
                sql_selected_country_dropdown = '''
                                    AND
                                    paper_id IN (SELECT paper_id
                                    FROM {temp_paper_country_list}
                                    WHERE country_id IN ( SELECT country_id
                                    FROM country_list
                                    WHERE country_name IN {temp_country}
                                    ))
                                    '''.format(temp_country=str(tuple(selected_country_dropdown_list)),
                                               temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
                # sql_selected_country_dropdown = str(tuple(selected_country_dropdown_list))
            # select id of each author based on different journal name
            sql_author = """
                     SELECT author_id
                     FROM {temp_jn}
                     WHERE paper_id IN (SELECT paper_id
                     FROM {temp_paper_list}
                     WHERE paper_abstract LIKE '%{user_search_temp}%'
                     )
                     AND
                     paper_id IN (SELECT paper_id
                     FROM {temp_key_jn}
                     WHERE keyword_id IN ( SELECT keyword_id
                     FROM keyword_list
                     WHERE keyword LIKE '%{selected_search_temp}%'
                     ))
                     AND
                     paper_id IN (SELECT paper_id
                     FROM {temp_paper_list}
                     WHERE paper_year IN ( SELECT year_id
                     FROM year_list
                     WHERE year IN {temp_year}
                     ))
                     {temp_country}
                     ;""".format(temp_jn='paper_author_' + jn.replace(" ", "_"),
                                 temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                                 user_search_temp=input1,
                                 temp_year=str(tuple(year_list)),
                                 temp_key_jn='paper_keyword_' + jn.replace(" ", "_"),
                                 selected_search_temp=selected_search,
                                 temp_country=sql_selected_country_dropdown)
            df3 = pd.read_sql_query(sql_author, conn)

            # loop through author ID cause we need all author
            for mmm in df3['author_id']:
                # get author
                sql_author = '''
                                    SELECT author_name
                                    FROM author_list
                                    WHERE author_id = {}'''.format(str(mmm))
                df_author = pd.read_sql_query(sql_author, conn)
                author_list.append(df_author.iloc[0]['author_name'])

        # author to dataframe and counting
        df_auth['author_name'] = author_list
        df_auth = df_auth.author_name.value_counts().rename_axis('author_name').reset_index(name='counts')

        # send table to HTML
        output = dash_table.DataTable(
            data=df_auth.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_auth.columns],
            page_size=10,
            style_cell={'textAlign': 'left', 'font-family': 'sans-serif'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

    return output


# show paper detail after selecting
@app.callback([Output('output-abstract', 'children'),
               Output('output-doi', 'children'),
               Output('output-name', 'children'),
               Output('abstract-output-author', 'children'),
               Output('output-date', 'children'),
               Output('abstract-output-country', 'children'),
               Output('link-paper', 'href')
               ],
              [Input('output-table', 'derived_virtual_row_ids'),
               Input('output-table', 'derived_virtual_selected_rows')],
              )
def showAbstract(xxx, selected_row_ids):
    if selected_row_ids is None or len(selected_row_ids) == 0:
        output1 = ' Nothing selected.\n ' \
                  'select paper to show abstract'
        output2 = 'Nothing selected'
        output3 = 'Nothing selected'
        output4 = 'Nothing selected'
        output5 = 'Nothing selected'
        output6 = 'Nothing selected'
        output7 = ''
    else:
        df = df_sql_share
        abstract = df.loc[selected_row_ids[0]]['paper_abstract']
        print(abstract)
        doi = df.loc[selected_row_ids[0]]['paper_doi']
        paper_name = df.loc[selected_row_ids[0]]['paper_name']
        global share_name
        share_name = paper_name
        author_list = []
        sql_jn = """
            SELECT journal_name
            FROM journal_list
            """
        for row in cursor.execute(sql_jn):
            jn = str(row[0])
            sql_id = '''
            SELECT paper_id
            FROM {temp_paper_list}
            WHERE paper_name LIKE '%{name_temp}%'
            '''.format(
                temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                name_temp=paper_name
            )
            x_check = pd.read_sql_query(sql_id, conn)
            if not x_check.empty:
                print(x_check)
                paper_id = x_check.iat[0, 0]
                journal_name = jn.replace(" ", "_")
        sql_author = '''
        SELECT author_list.author_name
        FROM author_list
        INNER JOIN {temp_list} ON
        {temp_list}.author_id = author_list.author_id
        WHERE {temp_list}.paper_id = {temp_id}
        '''.format(
            temp_id=paper_id,
            temp_list='paper_author_' + journal_name
        )
        sql_country = '''
        SELECT country_list.country_name
        FROM country_list
        WHERE country_id in (
        SELECT country_id
        FROM {temp_list}
        WHERE {temp_list}.paper_id = {temp_id}
        )
        '''.format(
            temp_id=paper_id,
            temp_list='paper_country_' + journal_name
        )
        sql_year = '''
        SELECT year
        FROM year_list
        WHERE year_id = (
        SELECT paper_year
        FROM {temp_list}
        WHERE paper_id = {temp_id}
        )
        '''.format(temp_list='paper_list_' + journal_name,
                   temp_id=paper_id)
        #
        # generate download paper link
        try:
            file_list = []
            root = r'C:\Users\M.Yaghoobi\PycharmProjects\Project\Dashboard\article_viewer\tems'
            for path, subdirs, files in os.walk(root):
                for name in files:
                    if paper_name in name:
                        file_list.append(os.path.join(path, name))
                        print(os.path.join(path, name))
            print('--------------')
            output7 = file_list[0]
        except:
            output7 = ''
        # show abstract
        output1 = dcc.Textarea(
            id='textarea-state-abstract',
            value=abstract,
            style={'width': '100%', 'height': 400}
        )
        # show doi
        output2 = dcc.Textarea(
            id='textarea-state-doi',
            value=doi,
            style={'width': '100%', 'height': 20}
        )
        # paper name
        output3 = paper_name
        # get author list
        output4 = ', '.join(pd.read_sql_query(sql_author, conn)['author_name'].tolist())
        # get year of paper
        output5 = pd.read_sql_query(sql_year, conn).iat[0, 0]
        # paper country
        output6 = ', '.join(pd.read_sql_query(sql_country, conn)['country_name'].tolist())
    return output1, output2, output3, output4, output5, output6, output7


@app.callback(
    Output('output-relation-graph', 'src'),
    [Input('output-country-relation', 'n_clicks'),
     Input('output-author-relation', 'n_clicks'),
     Input('output-wordcloud-relation', 'n_clicks')],
    [State('year-slider', 'value'),
     State('input-1-state', 'value')]
)
def showRelation(n_click, n1_click, n2_click, user_year, input1):
    user_click = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    callback_states = dash.callback_context.states.values()
    callback_inputs = dash.callback_context.inputs.values()
    if user_click == 'output-country-relation':
        # create some matplotlib graph
        c = createGraph(user_year, input1)
        buf = io.BytesIO()  # in-memory files
        plt.savefig(buf, format="png")  # save to the above file object
        data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
        plt.close()
        return "data:image/png;base64,{}".format(data)
    elif user_click == 'output-author-relation':
        # create some matplotlib graph
        c = createGraphAuthor(user_year, input1)
        buf = io.BytesIO()  # in-memory files
        plt.savefig(buf, format="png")  # save to the above file object
        data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
        plt.close()
        return "data:image/png;base64,{}".format(data)
    elif user_click == 'output-wordcloud-relation':
        print('++++++++++++++++++')
        keyword_wordcloud = df_key_share
        pllt = createWordcloud(keyword_wordcloud)
        buf = io.BytesIO()  # in-memory files
        pllt.savefig(buf, format="png")  # save to the above file object
        data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
        pllt.close()
        return "data:image/png;base64,{}".format(data)
    else:
        return 'no'


# @app.callback(
#     Output('output-relation-graph', 'src'),
#     [Input('output-author-relation', 'n_clicks')],
#     [State('year-slider', 'value'),
#      State('input-1-state', 'value')]
# )
# def showCountryRelation(n_click, user_year, input1):
#     # create some matplotlib graph
#     c = createGraphAuthor(user_year, input1)
#     buf = io.BytesIO()  # in-memory files
#     plt.savefig(buf, format="png")  # save to the above file object
#     data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
#     plt.close()
#     return "data:image/png;base64,{}".format(data)


if __name__ == '__main__':
    os.system(r"C:\Users\M.Yaghoobi\PycharmProjects\Project\Dashboard\article_viewer\Run.bat")
    app.run_server(debug=True)
