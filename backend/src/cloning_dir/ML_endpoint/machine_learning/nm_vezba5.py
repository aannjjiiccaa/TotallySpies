import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from sklearn import datasets
from keras.utils import to_categorical

data = datasets.load_breast_cancer()


ulaz = data.data
izlaz = data.target
print(ulaz.shape)
print(izlaz.shape)

ep = 100
bs = 32

from sklearn.model_selection import train_test_split

ulaz_trening, ulaz_test, izlaz_trening, izlaz_test = train_test_split(ulaz,izlaz,train_size=0.8,shuffle=True,random_state=14)

from keras.models import Sequential
from keras.layers import Dense

def make_model(n_in,n_out):
    model = Sequential()
    model.add(Dense(10,activation='relu',input_dim=n_in))
    model.add(Dense(5,activation='relu'))
    model.add(Dense(n_out,activation='sigmoid'))

    model.compile(optimizer='adam',metrics=['accuracy'],loss='binary_crossentropy')

    return model

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler().fit(ulaz_trening)
ulaz_trening_norm = scaler.transform(ulaz_trening)
ulaz_test_norm = scaler.transform(ulaz_test)

from keras.callbacks import EarlyStopping


model = make_model(ulaz.shape[1],1)
stop_early = EarlyStopping(monitor='val_accuracy',patience=5,restore_best_weights=True)
model.fit(ulaz_trening_norm,izlaz_trening,
          epochs=ep,batch_size=bs,
          validation_data=(ulaz_test_norm,izlaz_test),
          callbacks=stop_early,verbose=1)

print(f"Tacnost modela je {100*model.evaluate(ulaz_test_norm,izlaz_test,verbose=0)[1] }%")

from sklearn.model_selection import KFold

kf = KFold(n_splits=5,shuffle=True,random_state=20)

fold_no = 0
max_acc = 0
acc_all = []

for trening, val in kf.split(ulaz_trening_norm,izlaz_trening):
    ut, it = ulaz_trening_norm[trening,:],izlaz_trening[trening]
    uv,iv = ulaz_trening_norm[val,:],izlaz_trening[val]
    stop_early = EarlyStopping(monitor='val_accuracy',patience=5,restore_best_weights=True)
    history = model.fit(ut,it,epochs=ep,batch_size=bs,callbacks=[stop_early],verbose=1)

    acc = model.evaluate(uv,iv,verbose=1)[1]
    acc_all.append(acc)

    print(f"Tacnost u {fold_no}. fold-u je {acc*100}%")

    if acc>max_acc:
        max_acc = acc
        best_model = model

    fold_no +=1

    print(f"Prosecna tacnost modela je : {np.mean(acc_all)*100}%")

from sklearn.metrics import accuracy_score

pred = best_model.predict(ulaz_test_norm,verbose=1)
pred = np.round(pred)
print(f"Tacnost najboljeg modela na test skupu je: {accuracy_score(izlaz_test,pred)*100}%")