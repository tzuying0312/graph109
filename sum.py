import pandas as pd
df = pd.read_csv('lib/file/益生菌.csv')
# df2 =  df.groupby(['rank_page','word'])[['word']].count()

# 線粗細
# count_word_df = df.groupby(['rank_page','word'])['count'].agg([('count_sum','sum'),('count_mean','mean')])
count_word_df = df.groupby(['rank_page','word']).agg(
             count_sum=('count', 'sum'),
             count_mean=('count', 'mean'),
             tfidf_mean=('tfidf', 'mean')
             )
count_word_df = count_word_df.reset_index()
rank_article_df = df.drop_duplicates(['article','rank_page'])
rank_article_df = rank_article_df.groupby(['rank_page'])[['article']].size().reset_index(name = 'rank_article')
count_word_df = pd.merge(count_word_df, rank_article_df, how='left', on=['rank_page'])
# count_word_df = count_word_df.groupby(['rank_page','word','count_sum','count_mean'])[['word']].size().reset_index(name = 'current_page_count')

# 點大小
rank_page_df = df.groupby(['rank_page','word'])[['word']].size().reset_index(name = 'count')
rank_page_df = rank_page_df.groupby(['word'])[['word']].size().reset_index(name = 'rank_page_count')
article_df = df.groupby(['word'])[['word']].size().reset_index(name = 'article_count')
merge_df = pd.merge(rank_page_df, article_df, how = 'left', on ='word')

# 其他
current_page_count_df = df.groupby(['rank_page','word'])[['word']].size().reset_index(name = 'current_page_count')

# merge
final_df = pd.merge(count_word_df, merge_df, how='left', on=['word'])
final_df = pd.merge(final_df, current_page_count_df, how='left', on=['word','rank_page'])

# node_size from 點大小
# final_df['node_size'] = (final_df['article_count']/final_df['rank_page_count'])*10

# first_appear
first_appear_dict = {}
final_df['first_appear'] = ''

for i ,word in enumerate(final_df['word']): 
    if word in first_appear_dict:
        final_df.loc[i,'first_appear'] = first_appear_dict[word]
    else:
        first_appear_dict.setdefault(word,final_df['rank_page'][i])
        final_df.loc[i,'first_appear'] = final_df['rank_page'][i]

# to csv
final_df.to_csv('../file/sum.csv',encoding="utf_8_sig",index=0)

# final_df = final_df[final_df['current_page_count']>1] 