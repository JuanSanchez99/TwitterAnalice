import twitter
import spacy
from nltk.stem.snowball import SnowballStemmer
import unidecode
import pandas as pd
import re
from negspacy.negation import Negex


URL_PATTERN = r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\((' \
              r'[^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,' \
              r'<>?«»“”‘’])) '


def find_remove_links(text=''):
    while text.find('http') != -1:
        urlin = text.find('http')
        urlend = text.find(' ', urlin + 1)

        if urlend == -1:
            urlend = len(text)

        text = text.replace(text[urlin: urlend], '')
    return text


def remove_accents(text):
    return unidecode.unidecode(text)


def proc_str(text):
    low = text.lower()
    no_acc = remove_accents(low)
    remove_special = re.sub(r'[*\-{\}\[\]\\]', '', no_acc)
    remove_links = find_remove_links(remove_special)

    return remove_links


def get_searches():
    api = twitter.Api(consumer_key='40gfaTfJDWXqBriBlNmezyUKG',
                      consumer_secret='1vtddPlnNX6FtVCXtczwoCAUALseEldS99dnI2suanyjIGBKyY',
                      access_token_key='1277317769579593730-bqYImqZNencT6xukGGpugjCcSupcHj',
                      access_token_secret='ppIBsZ9TXeX8XNhNdLLb4CiOlogVuOfRqAYqBq4u2UzTQ')

    searches_list = api.GetSearch(term='covid', count=100, lang='en')

    searches_list = list(map(lambda x: x.AsDict(), searches_list))

    def get_location(x):
        if 'location' in x['user']:
            x['location'] = x['user']['location']
        return x

    searches_list = list(map(get_location, searches_list))

    df = pd.DataFrame.from_records(searches_list, index=['id'])

    df['location'].dropna()

    return df, map(lambda x: proc_str(x['text']), searches_list)


def perform_nlp(searches_list):
    nlp = spacy.load('en_core_web_sm')

    negex = Negex(nlp, ent_types=['PERSON', 'ORG', 'NORP', 'FAC', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'LAW',
                                  'TIME', 'PERCENT', 'QUANTITY', 'ORDINAL', 'CARDINAL'],
                  language='en')
    nlp.add_pipe(negex, last=True)

    texts = tuple(searches_list)

    stemmer = SnowballStemmer(language='english')

    for text in texts:
        doc = nlp(text)
        print("----------------tweet-----------")
        print(text)
        print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
        print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

        print("***(token:)***")

        # generated tokens
        for token in doc:
            print(token.text, end=" | ")
        print()

        print("***(Entities:)***")
        for entity in doc.ents:
            print(entity.text, entity.label_)

        print("***(Negation:)***")
        for e in doc.ents:
            print(e.text, e._.negex)

        print("***(Stemming)***")
        for token in doc:
            if token.text != stemmer.stem(token.text):
                print(token.text + ' --> ' + stemmer.stem(token.text))

        print("***(Lemmatization)***")
        for word in nlp(text):
            if word.text != stemmer.stem(word.lemma_):
                print(word.text, word.lemma_)

        print("************************************")


def draw_something(df):
    df.plot(x='location', y='favorite_count')

    df['created_at'] = pd.to_datetime(df['created_at'])

    print(df.groupby(df['created_at'].dt.strftime('%B')).count())


if __name__ == '__main__':
    df, searches = get_searches()

    draw_something(df)

    perform_nlp(searches)

    print(df)


