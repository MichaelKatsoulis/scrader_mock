import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.svm import SVC
from time import time

data = pd.read_csv('./comb8.csv', sep=',', encoding='utf-8')
data1 = data['Article']
data2 = data['Sentiment']

print 'Data read Successfully'

data = pd.concat([data1.reset_index(drop=True), data2], axis=1)
data.columns = ['Articles', 'Sentiment']
data.groupby(['Sentiment']).count().reset_index()
ntrain = len(data['Articles'])*0.8
ntrain = int(round(ntrain))
train_set = data[:ntrain]
train_set.groupby(['Sentiment']).count().reset_index()
data = data.sample(frac=1)

g = TfidfVectorizer(min_df=5, max_df=1000, ngram_range=(1, 6), stop_words=[
 "Amazon", "Uber", "Netflix", "Google", "Boeing","IBM","Aig","Apple","Ryanair","Motorolla",
 "Equifax", "Microsoft","Spotify", "Exxon", "Wells Fargo", "Toyota", "HSBC", "BP",
 "Volkswagen", "BnP Paribas", "Daimler", "Samsung", "AXA", "Vodafone", "Nestle", "Ford", "Metlife",
 "General Motors", "Intel", "Oracle", "Unilever", "Morgan Stanley", "Barclays", "Christian Dior", "3M",
 "Target", "Nintendo", "Tesla", "Panasonic", "ebay", "Kia", "Renault", "Apache", "Philips", "Monsanto",
 "Accenture", "Toshiba", "Baidu", "SKY", "JPMorgan", "JP-Morgan", "P&G", "VW", "BMW", "Benz", "Mercedes",
 "AT&T", "Renault", "Alibaba", "Citi", "Chevron", "Wal-mart", "Gazprom", "Verizon", "Santander","Siemens",
 "Novartis", "Goldman", "Metlife", "Hyundai", "Disney", "Prudencial", "Qualcomm", "Honeywell", "ABB",
 "Astrazeneca", "Carrefour", "Canon", "Canon", "Aetna"
], analyzer=u'word', max_features=5000)
X_train = g.fit_transform(data['Articles'][:ntrain]).toarray()
X_test = g.transform(data['Articles'][ntrain:]).toarray()
y_train = data['Sentiment'][:ntrain]
y_test = data['Sentiment'][ntrain:]


def train_classifier(clf, X_train, y_train):
    """ Fits a classifier to the training data. """

    # Start the clock, train the classifier, then stop the clock
    start = time()
    clf.fit(X_train, y_train)
    end = time()

    # Print the results
    print "Trained model in {:.4f} seconds".format(end - start)


def predict_labels(clf, features, target):
    """ Makes predictions using a fit classifier based on an F1 score. """

    # Start the clock, make predictions, then stop the clock
    start = time()
    y_pred = clf.predict(features)
    end = time()

    # Print and return results
    print "Made predictions in {:.4f} seconds.".format(end - start)
    return f1_score(target.values, y_pred, pos_label='NEG')


def train_predict(clf, X_train, y_train, X_test, y_test):
    """ Train and predict using a classifer based on F1 score. """

    # Indicate the classifier and the training set size
    print "Training a {} using a training set size of {}. . .".format(clf.__class__.__name__, len(X_train))

    # Train the classifier
    train_classifier(clf, X_train, y_train)

    # Print the results of prediction for both training and testing
    print "F1 score for training set: {:.4f}.".format(predict_labels(clf, X_train, y_train))
    print "F1 score for test set: {:.4f}.".format(predict_labels(clf, X_test, y_test))


clf = SVC(kernel='linear', probability=True)
train_predict(clf, X_train, y_train, X_test, y_test)
y_pred = clf.predict(X_test)
print y_pred
confusion = confusion_matrix(y_test, y_pred)
y_pred = clf.predict(X_test)
print y_pred
print clf.predict_proba(X_test)



