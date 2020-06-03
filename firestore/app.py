# coding: utf-8
from google.cloud import firestore
from Docments import Profile
import os


def addDocument(
        client: firestore.Client,
        collection: str,
        document: str,
        content: str):
    """コレクションへドキュメントを登録する

    Arguments:
        client {firestore.Client} -- [description]
        collection {str} -- collection name
        document {str} -- document name
        content {str} -- jsonライクな定義
    """
    client.collection(collection).document(document).set(content)


def getDocument(client: firestore.Client,
                collection: str):
    """Collectioからドキュメント一覧を取得する

    Arguments:
        client {firestore.Client} -- [description]
        collection {str} -- [description]

    Returns:
        [type] -- [description]
    """
    return client.collection(collection).stream()


def deleteDocumet(
        client: firestore.Client,
        collection: str,
        document: str):
    """ドキュメントを削除する

    Arguments:
        client {firestore.Client} -- [description]
        collection {str} -- [description]
        document {str} -- [description]
    """
    client.collection(collection).document(document).delete()


if __name__ == "__main__":

    db = firestore.Client()
    collection = os.environ.get('COLLECTION')
    document = os.environ.get('DOCUMENT')

    profile = Profile(
        first_name='ねこ',
        last_name='動物大好き',
        age=20,
        favorite='猫'
    )

    addDocument(db, collection, document, profile.to_dict())

    docs = getDocument(db, collection)
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
