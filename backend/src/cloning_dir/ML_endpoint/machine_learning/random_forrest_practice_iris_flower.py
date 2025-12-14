# Loading library with iris dataset

from sklearn.datasets import load_iris

# Loading Random forest classifier

from sklearn.ensemble import RandomForestClassifier

# Loading other libraries

import pandas as pd
import numpy as np

# Setting random seed

np.random.seed(0)


# Creating object with iris data

iris = load_iris()

# Creating pd dataframe with that data

df = pd.DataFrame(iris.data, columns=iris.feature_names)

df['species'] = pd.Categorical.from_codes(iris.target, iris.target_names)

df['is_train'] = np.random.uniform(0,1,len(df)) <= 0.75



train, test = df[df['is_train'] == True], df[df['is_train']==False]

print(train.columns)

print("Number of training samples: ", len(train))
print("Number of test samples: ", len(test))

features = df.columns[:4]

# Creating rezults, factorize transfers data from categorical value to numbers that we'll use for training


y = pd.factorize(train['species'])[0]


# Creating random forest classifier

clf = RandomForestClassifier(n_jobs=2, random_state=0)


# Training classifier

clf.fit(train[features], y)

# Testing classifier

predictions = clf.predict(test[features])

print(predictions)

# Extracting of probabilities of each class of first ten samples

class_probabilities = clf.predict_proba(test[features])[:10]

print(class_probabilities)


# Assign names to predicted values

preds = iris.target_names[clf.predict(test[features])]

print(preds[:5])

# Creating a confussion matrix

cm = pd.crosstab(test['species'],preds,rownames=['Actual species'],colnames = ['Predicted states'])

print(cm)

