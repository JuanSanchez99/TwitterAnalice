import twitter
import spacy
import unidecode


def remove_accents(text):
    return unidecode.unidecode(text)


def get_searches():
    api = twitter.Api(consumer_key='40gfaTfJDWXqBriBlNmezyUKG',
                      consumer_secret='1vtddPlnNX6FtVCXtczwoCAUALseEldS99dnI2suanyjIGBKyY',
                      access_token_key='1277317769579593730-bqYImqZNencT6xukGGpugjCcSupcHj',
                      access_token_secret='ppIBsZ9TXeX8XNhNdLLb4CiOlogVuOfRqAYqBq4u2UzTQ')

    searches_list = api.GetSearch(term='covid', count=100, lang='es')

    return map(lambda x: remove_accents(x.text.lower()), searches_list)


def perform_nlp(searches_list):
    nlp = spacy.load('es_core_news_sm')

    texts = tuple(searches_list)

    for text in texts:
        doc = nlp(text)
        print("----------------tweet-----------")
        print(text)
        print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
        print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

        print("(token:)")

        # generated tokens
        for token in doc:
            print(token.text, end=",")

        for entity in doc.ents:

            print(entity.text, entity.label_)

        print("************************************")


if __name__ == '__main__':
    searches = get_searches()

    perform_nlp(searches)




