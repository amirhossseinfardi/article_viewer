def parse_user_input(user_search):
    user_search_list = user_search.split('-')
    return user_search_list[0].strip()


def sql_multi_search(user_search, sql_search_place, jn):
    user_search_list = user_search.split('-')

    sql1 = '''
    AND
    paper_id IN (
        SELECT paper_id
        FROM {temp_paper_list}
        WHERE {temp_paper_search} LIKE '%{user_search_temp}%'
         )
    '''.format(temp_paper_list='paper_list_' + jn.replace(" ", "_"),
               temp_paper_search=sql_search_place,
               user_search_temp=user_search_list[1].strip())
    return sql1
