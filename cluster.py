import pandas as pd
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import string
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np

def document_vector(df):
    ''' 
    input df produced by the process function (pulled from db version)
    returns a df with 3 columns: reddit post title, list of keyword extracted from title, and document vector corresponding to title
    '''
    list_of_keywords = df['keywords'].apply(lambda x: x.split(','))
    # remove punctuations
    title_text = [x.translate(str.maketrans('', '', string.punctuation)) for x in df['title'] if True]
    # lowercase all characters
    title_text_lower = [x.lower() for x in title_text]
    
    # distributed memory
    model_dm = Doc2Vec(dm=1, vector_size=25, min_count=2, epochs=30)
    tagged_data = [TaggedDocument(words=word_tokenize(doc.lower()),
                              tags=[str(i)]) for i, doc in enumerate(title_text_lower)]
    model_dm.build_vocab(tagged_data)
    model_dm.train(tagged_data,
            total_examples=model_dm.corpus_count,
            epochs=model_dm.epochs)
    
    document_vectors = [model_dm.infer_vector(word_tokenize(doc.lower())) for doc in title_text_lower]
    
    text_vec_df = pd.DataFrame({'title': df['title'], 
                            'keywords':list_of_keywords, 'vectors': document_vectors})
    return text_vec_df


def cluster_and_identify_keywords(vector_df):
    '''
    Cluster the messages based on the vector extracted from the text and identify keywords for each cluster.
    vector_df (DataFrame): A DataFrame with 3 columns: reddit post title, list of keywords extracted from title, and document vector corresponding to title.
    DataFrame: A DataFrame with 5 columns: reddit post title, list of keywords extracted from title, document vector corresponding to title, cluster label, and keywords associated with each cluster.
    '''
    tfidf_vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(vector_df['keywords'].apply(lambda x: ' '.join(x)))
    
    kmeans = KMeans(n_clusters=10)
    kmeans.fit(vector_df['vectors'].to_list())  # Ensure 'vectors' is a list of arrays
    vector_df['cluster'] = kmeans.labels_
    
    cluster_keywords = {}
    feature_names = tfidf_vectorizer.get_feature_names_out()
    for cluster_label in range(kmeans.n_clusters):
        cluster_indices = vector_df[vector_df['cluster'] == cluster_label].index
        cluster_tfidf = tfidf_matrix[cluster_indices]
        cluster_keywords[cluster_label] = [feature_names[i] for i in cluster_tfidf.sum(axis=0).argsort()[-5:][::-1]]
    vector_df['cluster_keywords'] = vector_df['cluster'].map(cluster_keywords)
    return vector_df


def draw_cluster(clustered_df):
    vectors_array = np.array(clustered_df['vectors'].to_list())

    tsne = TSNE(n_components=2, random_state=42)
    vectors_2d = tsne.fit_transform(vectors_array)

    plt.figure(figsize=(10, 8))
    for cluster_label in range(clustered_df['cluster'].nunique()):
        plt.scatter(vectors_2d[clustered_df['cluster'] == cluster_label, 0], 
                    vectors_2d[clustered_df['cluster'] == cluster_label, 1], 
                    label=f'Cluster {cluster_label}')
    plt.title('t-SNE Visualization of Clusters')
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.legend()
    plt.show()
    