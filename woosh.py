# -*- coding: utf-8 -*-
import os
from whoosh.analysis import Tokenizer, Token
from whoosh.qparser import QueryParser
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
import json
import constants

class MyTokenizer(Tokenizer):
    def __call__(self, text, **kargs):
        token = Token()
        for (start_pos,w) in enumerate(text):
            token.original = token.text = w
            token.pos = start_pos
            token.startchar = start_pos
            token.endchar = start_pos + len(w)
            yield token

def create_search_index(kb):
    # # 创建schema, stored为True表示能够被检索
    schema = Schema(content=TEXT(stored=True, analyzer=MyTokenizer()))
    # # 文件
    categories = open(kb["kb_path"] + kb["kb"],"r",encoding ="utf-8")
    lines = categories.readlines()
    contents = []
    duplicate = {}
    for l in lines:
        subcat,sup = l.strip("\n").split("->")
        # subcat = subcat.strip()
        # if subcat not in duplicate.keys():
        #     contents.append(subcat)
        # duplicate[subcat]=1

        sup = sup.strip()
        if sup not in duplicate.keys():
            contents.append(sup)
        duplicate[sup]=1
        
    # # 存储schema信息至indexdir目录
    indexdir = kb["kb_index_path"] + kb["kb_index_prefix"]
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)

    # # 按照schema定义信息，增加需要建立索引的文档
    writer = ix.writer()
    for i in range(1, len(contents)):
        writer.add_document(content=contents[i])
    writer.commit()


def search(kb,query):
    # 创建一个检索器
    indexdir = kb["kb_index_path"] + kb["kb_index_prefix"]
    ix = open_dir(indexdir)
    searcher = ix.searcher()
    query = QueryParser("content", ix.schema).parse(query)
    results = searcher.search(query,limit=15)
    result_data = {"content":[]}
    print('一共发现%d份文档。' % len(results))
    for result in results:
        result_data["content"].append(result["content"])
        print(json.dumps(result.fields(), ensure_ascii=False))
    return result_data

 
if __name__ == '__main__':
    kb = constants.kb_base["wiki"]
    create_search_index(kb)


