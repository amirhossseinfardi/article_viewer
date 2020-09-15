from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations
import networkx as nx
from nxviz.plots import CircosPlot
import sqlite3
from functools import reduce


def createGraphAuthor(year_list, input1):
    # read data from database
    conn = sqlite3.connect('temp.db')
    cursor = conn.cursor()

    df_author = []
    sql_jn = """
    SELECT journal_name
    FROM journal_list
    """
    for row in cursor.execute(sql_jn):
        jn = str(row[0])
        print(jn)

        sql_final = """
         SELECT {paper_author_temp}.paper_id, author_list.author_name
         FROM {paper_author_temp}
         INNER JOIN author_list ON author_list.author_id = {paper_author_temp}.author_id
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
         ;""".format(paper_author_temp='paper_author_' + jn.replace(" ", "_"),
                     temp_paper_list='paper_list_' + jn.replace(" ", "_"),
                     user_search_temp=input1,
                     temp_year=str(tuple(year_list))
                     )

        df2 = pd.read_sql_query(sql_final, conn)
        gb = df2['author_name'].groupby([df2.paper_id]).apply(list).reset_index()
        df_author.append(gb['author_name'].tolist())
    print('---------------')
    flatten = [item for elem in df_author for item in elem]
    conn.commit()
    conn.close()

    record_list = []

    # part 2 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    sns.set_style("white")

    authors_flat = [
        author
        for authors in flatten
        for author in authors
    ]

    # Part 3 $$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Extract author connections article_authors
    authors = flatten
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(type(authors))
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%')
    author_connections = list(
        map(lambda x: list(combinations(x[::-1], 2)), authors)
    )
    flat_connections = [item for sublist in author_connections for item in sublist]
    print(len(flat_connections))
    # Create a dataframe with the connections
    df = pd.DataFrame(flat_connections, columns=["From", "To"])
    print(df)
    # df.to_excel('1.xlsx')
    df_graph = df.groupby(["From", "To"]).size().reset_index()
    print(df_graph)
    # df_graph.to_excel('2.xlsx')
    df_graph.columns = ["From", "To", "Count"]
    print(df_graph)

    G = nx.from_pandas_edgelist(
        df_graph, source="From", target="To", edge_attr="Count"
    )

    # Limit to TOP 50 authors
    top50authors = pd.DataFrame.from_records(
        Counter(authors_flat).most_common(50), columns=["Name", "Count"]
    )

    top50_nodes = (n for n in list(G.nodes()) if n in list(top50authors["Name"]))

    G_50 = G.subgraph(top50_nodes)

    for n in G_50.nodes():
        G_50.node[n]["publications"] = int(
            top50authors[top50authors["Name"] == n]["Count"]
        )

    c = CircosPlot(
        G_50,
        dpi=600,
        node_grouping="publications",
        edge_width="Count",
        figsize=(20, 20),
        node_color="publications",
        node_labels=True,
    )
    m = c.draw()

    return m
