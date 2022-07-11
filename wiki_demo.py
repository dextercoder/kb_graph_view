import streamlit as st
import numpy as np
import pandas as pd
from kb_search import *
import streamlit.components.v1 as components

from woosh import search, MyTokenizer
import constants

import sys  
sys.path.append('.')

# from fuzzywuzzy import process
# def fuzzy_search(data, query):
#     cats = data.category.to_list()
#     a = process.extract(query, cats, limit=10)
#     a = pd.DataFrame(a, columns=["名称", "相似度"])
#     return a

kb_selectbox = st.sidebar.selectbox(
    "please choose the knownledege base ",
    ("","wiki", "baike", "bigcilin")
)

num_radio = st.sidebar.radio(
        "Choose frequency show",
        ("","30","50","100","200","300","500")
)

if kb_selectbox and num_radio:
    ## frequcency
    kb = constants.kb_base[kb_selectbox]
    categories = open(kb["kb_path"] + kb["kb"],"r",encoding ="utf-8")
    lines = categories.readlines()
    categories_stat = {}
    for l in lines:
        subcat,sup = l.split("->")
        # if subcat in categories_stat.keys():
        #     categories_stat[subcat] = categories_stat[subcat] + 1
        # else:
        #     categories_stat[subcat] = 0
        
        if sup in categories_stat.keys():
            categories_stat[sup] = categories_stat[sup] + 1
        else:
            categories_stat[sup] = 0

    stats = sorted(categories_stat.items(),key=lambda x: x[1],reverse=True)
    cat = []
    num = []
    for (k,v) in stats[0:int(num_radio)]:
        cat.append(k)
        num.append(v)
    data = pd.DataFrame({
        "category": cat,
        "number":num
    })
    st.table(data)
    
    
    # vis.js initial
    script_fb = open("VIS/dist/vis.js","r",encoding="utf-8")
    scripts = script_fb.readlines()
    scripts = ''.join(scripts)

    css_fb = open("VIS/dist/vis.css","r",encoding="utf-8")
    css = css_fb.readlines()
    css = ''.join(css)

    script_import = '''<script type="text/javascript">'''+ scripts + '''</script>'''
    css_import = '''<script type="text/javascript">''' + css + '''</script>'''
    meta = '''<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'''

    # kb initial
    word = st.text_input("Your interest entity")
    handler = SemanticBaike(kb)
    # a = fuzzy_search(data, word)

    if word != "":
        # search
        results = search(kb, word)
        opts = [""]+results["content"]
        pick_word = st.radio("pick one",opts)
        
        # graph
        if pick_word != "":
            handler.path = []
            body = handler.walk_concept_chain(pick_word)
            head = '''<head>''' + script_import + css_import + '''</head>''' 

            st.write("wiki graph : "+pick_word)
            html = '<html> ' + head + body + '</html>'
            components.html(html ,width = 800, height=800)
            
            with open("word_concept.txt", "r", encoding="utf-8") as file:
                btn = st.download_button(
                        label="Download file",
                        data=file,
                        file_name=word+".txt"
                    )
