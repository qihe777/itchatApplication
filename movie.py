import time
import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
import warnings

warnings.simplefilter('ignore')


class recommend:
    def __init__(self):
        # 加载全部数据元数据，生成dataframe
        md = pd.read_csv('data/movie/movies_metadata.csv')
        # fillna将类型这一行空的使用列表填充，literal_eval将文件数据转化成python对象
        md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(
            lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        # 整理电影年份格式，只显示年
        md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
            lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
        # 基于内容的推荐，读取小的电影数据集
        links_small = pd.read_csv('data/movie/links_small.csv')
        links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
        # 删掉这三行有数据缺失的行数
        md = md.drop([19730, 29503, 35587])
        md['id'] = md['id'].astype('int')
        # cast全体演员，crew技术人员团队
        credits = pd.read_csv('data/movie/credits.csv')
        # 关键字
        keywords = pd.read_csv('data/movie/keywords.csv')
        md = md.merge(credits, on='id')
        md = md.merge(keywords, on='id')
        smd = md[md['id'].isin(links_small)]
        smd['cast'] = smd['cast'].apply(literal_eval)
        smd['crew'] = smd['crew'].apply(literal_eval)
        smd['keywords'] = smd['keywords'].apply(literal_eval)
        smd['cast_size'] = smd['cast'].apply(lambda x: len(x))
        smd['crew_size'] = smd['crew'].apply(lambda x: len(x))

        def get_director(x):
            for i in x:
                if i['job'] == 'Director':
                    return i['name']
            return np.nan

        smd['director'] = smd['crew'].apply(get_director)

        # 获取电影的前三名演员
        smd['cast'] = smd['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        smd['cast'] = smd['cast'].apply(lambda x: x[:3] if len(x) >= 3 else x)
        # 把关键字提取出来，删除关键字的id
        smd['keywords'] = smd['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        # 修改名字格式：小写，去除空格
        smd['cast'] = smd['cast'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
        smd['director'] = smd['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
        # 导演添加三次，增加权重
        smd['director'] = smd['director'].apply(lambda x: [x, x, x])

        s = smd.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'keyword'
        s = s.value_counts()
        # 只保留出现超过一次的关键词
        s = s[s > 1]

        # 拼接电影关键词
        def filter_keywords(x):
            words = []
            for i in x:
                if i in s:
                    words.append(i)
            return words
        # 找到关键词词干
        stemmer = SnowballStemmer('english')
        smd['keywords'] = smd['keywords'].apply(filter_keywords)
        smd['keywords'] = smd['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])
        smd['keywords'] = smd['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
        # 合并全部的因变量
        smd['soup'] = smd['keywords'] + smd['cast'] + smd['director'] + smd['genres']
        smd['soup'] = smd['soup'].apply(lambda x: ' '.join(x))
        # 关键词  词频矩阵
        count = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
        # 生成矩阵，是稀疏矩阵
        count_matrix = count.fit_transform(smd['soup'])
        # 计算余弦相似度
        self.cosine_sim = cosine_similarity(count_matrix, count_matrix)
        # 对象数据清洗以后通过reset_index重新设置连续的行索引index
        self.smd = smd.reset_index()
        self.indices = pd.Series(self.smd.index, index=self.smd['title'])

    def improved_recommendations(self, title):
        idx = self.indices[title]
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # 取出来前25个，删掉自己
        sim_scores = sim_scores[1:26]
        # 选取电影id，或者说是索引
        movie_indices = [i[0] for i in sim_scores]
        # iloc函数：通过行号来取行数据（如取第二行的数据）
        movies = self.smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year']]
        # 通过评分重新排序，选取前10个
        vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
        vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
        C = vote_averages.mean()
        m = vote_counts.quantile(0.60)

        def weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (m + v) * C)

        qualified = movies[
            (movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
        qualified['vote_count'] = qualified['vote_count'].astype('int')
        qualified['vote_average'] = qualified['vote_average'].astype('int')
        qualified['wr'] = qualified.apply(weighted_rating, axis=1)
        qualified = qualified.sort_values('wr', ascending=False).head(10)
        return qualified


if __name__ == "__main__":
    x1 = int(time.time())
    x = recommend()
    x2 = int(time.time())
    print(x2 - x1)
    i = 1
    movie = x.improved_recommendations('Inception')
    print(movie)
    for title, score, year in zip(movie['title'], movie['vote_average'], movie['year']):
        print('%d:%s,%s,%s' % (i, title, score, year))
        i=i+1
