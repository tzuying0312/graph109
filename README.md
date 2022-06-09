## 資料夾結構說明
```
.
├── Procfile # 部署 Heroku 檔案
├── README.md
├── crawler.py # (現在已經無法使用！) 爬取網站，產生益生菌.csv 檔案
├── flow.drawio # crawler.py 流程
├── lib
│   ├── corpus # 語料
│   ├── file # output 檔案和爬取 log
│   └── json # crawler.py 過程中儲存的資訊
├── main.py # 視覺化主程式(Flask)
├── requirements.txt # 部署 Heroku 檔案
├── runtime.txt # 部署 Heroku 檔案
├── static # 前端相關檔案
│   ├── default.css
│   ├── fonts
│   ├── fonts.css
│   ├── images
│   └── pic
├── sum.py # 統計節點及邊的資訊，產生 sum.csv(之後要丟進 Neo4j 的資料)
└── templates # 前端相關檔案
    ├── graph.html
    ├── information.html
    ├── read_me.html
    └── sub.html
```
## Usage
- [**Neo4j Sandbox**](https://neo4j.com/sandbox/)
    ```
    load csv with headers from "(https://raw.githubusercontent.com/tzuying0312/graph109/main/lib/file/sum.csv)" as row
    merge(x:word{name:row.word})
    merge(y:頁數{name:row.rank_page})
    merge(x)-[r:in]->(y)
    set r.出現次數=toFloat(row.count_sum)
    set r.平均tfidf值=toFloat(row.tfidf_mean)
    set x.rank_page=toInteger(row.first_appear)
    set x.頁數數量=toFloat(row.rank_page_count)
    set x.篇數數量=toFloat(row.article_count)
    set y.rank_page=toInteger(row.rank_page)
    set y.篇數數量=toInteger(row.rank_article)
    ```
- 在  templates/graph.html 中的 server_url 與 server_password 改成 Sandbox 的 Bolt URL 與 Password 
``` js
    var config = {
        container_id: "viz",
        server_url: "bolt://52.207.134.182:7687", // Bolt URL
        server_user: "neo4j",
        server_password: "utilization-patches-strut", // Bolt Password
        ...
```
- 運行 `python main.py` 並開啟 http://127.0.0.1:5000/graph
