from google.cloud import firestore

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()


collection = u'examples'
document = u'test_profile'


doc_ref = db.collection(collection).document(document)
doc_ref.set({
    u'first': u'taro',
    u'last': u'tanaka',
    u'born': 2000
})



docs = db.collection(collection).stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
