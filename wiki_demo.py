import streamlit as st
import numpy as np
import pandas as pd
from kb_search import *
import streamlit.components.v1 as components
import constants
import sys  
from woosh import search,MyTokenizer
sys.path.append('.')


def page_show(pages):
    hang = len(pages) // 8
    yu = 8*(hang+1) - len(pages) 
    pages = pages + ['']*yu
    data = np.array(pages).reshape(-1,8)
    return data
    
def get_cat_pages(path="kb/wiki_cat_hyper_10000000.txt"):
    cat_pages = dict()
    cp_fp = open(path,"r",encoding="utf-8")
    lines = cp_fp.readlines()
    for line in lines:
        cat,pages = line.strip("\n").split("->")
        cat_pages[cat] = pages
    return cat_pages
    
    
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

cat_pages = get_cat_pages(path="kb/wiki_cat_hyper_10000000.txt")


kb_selectbox = st.selectbox(
    "please choose the knownledege base ",
    ("","baike", "hudong","bigcilin","wiki")
)

num_radio = st.radio(
        "Choose frequency show",
        ("","20","30","50","100","200")
)

if kb_selectbox and num_radio:
    ## frequcency
    kb = constants.kb_base[kb_selectbox]
    categories = open(kb["kb_path"] + kb["kb"],"r",encoding ="utf-8")
    lines = categories.readlines()
    categories_stat = {}
    for l in lines:
        # sub->sup
        sub,sup = l.split("->")
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
    st.write("High Freq category:")
    st.table(data)
    

    # kb initial
    word = st.text_input("Input your interest category:")
    handler = SemanticBaike(kb)

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
            
        cat = st.text_input("Input your interest category from up graph:")
        if cat != "":
            if cat in cat_pages:
                pages = cat_pages[cat].split(",")
                data = page_show(pages)
                st.table(data)