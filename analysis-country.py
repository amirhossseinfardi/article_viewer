from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations
import networkx as nx
from nxviz.plots import CircosPlot
import sqlite3
from functools import reduce


def createGraph():
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
         SELECT {paper_country_temp}.paper_id, country_list.country_name
         FROM {paper_country_temp}
         INNER JOIN country_list ON country_list.country_id = {paper_country_temp}.country_id
         ;""".format(paper_country_temp='paper_country_' + jn.replace(" ", "_"))

        df2 = pd.read_sql_query(sql_final, conn)
        gb = df2['country_name'].groupby([df2.paper_id]).apply(list).reset_index()
        df_author.append(gb['country_name'].tolist())
    print('---------------')
    flatten = [item for elem in df_author for item in elem]
    conn.commit()
    conn.close()

    record_list = []

    # part 2 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
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
    df['From'] = df['From'].replace(dict_country)
    df['To'] = df['To'].replace(dict_country)
    df = df[df['From'] != df['To']]
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
        figsize=(20, 20),
        node_color="publications",
        node_labels=True,
    )
    c.draw()
    plt.show()

    # find path
    # paths = list(
    #     nx.all_shortest_paths(G, source="Xing Wang", target="Wen Li")
    # )
    # for path in paths:
    #     print(path)
    return c
