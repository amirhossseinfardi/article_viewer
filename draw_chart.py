import pandas as pd
import sqlite3
import plotly.express as px


def draw_keyword_data(user_search,
                      user_year,
                      user_country,
                      user_journal):
    conn = sqlite3.connect('temp.db')
    cursor = conn.cursor()
    sql_jn = """
        SELECT journal_name
        FROM journal_list
        """
    df_all_journal = pd.read_sql_query(sql_jn, conn)

    # select year
    year_list = list(range(user_year[0], user_year[1] + 1, 1))
    # if len(year_list) == 1:
    #     year_list.append(year_list[0])

    # ------------------  select journal
    if not user_journal or user_journal[0] == '*':
        selected_journal = [x for x in df_all_journal['journal_name'].tolist()]
        # print('---------->>>>>>>>>', selected_journal)
    else:
        selected_journal = user_journal
        # print(selected_journal)

    counter_list = []
    for my_year in year_list:
        counter = 0
        for row in selected_journal:
            jn = row

            # choose country
            if not user_country or user_country[0] == '*':
                selected_country_dropdown_list = '*'
                sql_selected_country_dropdown = ''
            elif len(user_country) == 1:
                selected_country_dropdown_list = user_country[0]
                sql_selected_country_dropdown = '''
                            AND
                            paper_id IN (SELECT paper_id
                            FROM {temp_paper_country_list}
                            WHERE country_id IN ( SELECT country_id
                            FROM country_list
                            WHERE country_name = '{temp_country}'
                            ))
                            '''.format(temp_country=user_country[0],
                                       temp_paper_country_list='paper_country_' + jn.replace(" ", "_"))
                print('len is zero')
            else:
                selected_country_dropdown_list = user_country
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

            sql_final = """
                         SELECT paper_id
                         FROM {temp_paper_list}
                         WHERE paper_abstract LIKE '%{user_search_temp}%'
                         
                         AND
                         paper_id IN (SELECT paper_id
                         FROM {temp_paper_list}
                         WHERE paper_year IN ( SELECT year_id
                         FROM year_list
                         WHERE year = {temp_year}
                         ))
                         {temp_country}
                         ;""".format(temp_jn='paper_keyword_' + jn.replace(" ", "_"),
                                     temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                                     user_search_temp=user_search,
                                     temp_year=str(my_year),
                                     temp_country=sql_selected_country_dropdown)

            df2 = pd.read_sql_query(sql_final, conn)
            counter = counter + len(df2.index)
        counter_list.append(counter)
    chart_df = pd.DataFrame(year_list, columns=['year'])
    chart_df['counter'] = counter_list
    fig = px.bar(chart_df, x="year", y="counter",
                 title='keyword : {}'.format(user_search))
    return fig, chart_df
