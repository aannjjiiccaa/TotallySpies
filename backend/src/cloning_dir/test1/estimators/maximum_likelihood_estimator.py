import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .kalman_filtar import generator

def prvi_izvod(opserv,teta_k):
    prvi_izv = 0
    for i in range(len(opserv)):
        prvi_izv += 2*(opserv[i]-teta_k)/(1+(opserv[i]-teta_k)**2)

    return prvi_izv

def drugi_izvod(opserv,teta_k):
    drugi_izv = 0
    for i in range(len(opserv)):
        drugi_izv += 2*((opserv[i]-teta_k)**2-1)/((1+(opserv[i]-teta_k)**2)**2)

    return drugi_izv
def log_ver(opserv,teta_k):
    log_v = (-1)*len(opserv)*np.log(np.pi)
    for i in range(len(opserv)):
        log_v -= np.log(1+(opserv[i] - teta_k)**2)
    return log_v

def emv(opserv,pocetna_proc,tolerancija,br_iter):
    i = 0
    proc_preth = pocetna_proc
    proc_sled = pocetna_proc - prvi_izvod(opserv,pocetna_proc)/drugi_izvod(opserv,pocetna_proc)
    while(i<br_iter and abs(proc_sled-proc_preth) > tolerancija):
        proc_preth=proc_sled
        proc_sled = proc_preth - prvi_izvod(opserv,proc_preth)/drugi_izvod(opserv,proc_preth)
        i +=1
    return proc_sled


def main():
    df = pd.read_csv("../datasets/emv.csv")
    teta = np.linspace(-20, 20, 4000)
    i = 0

    l_v_1 = [0] * len(teta)
    l_v_2 = [0] * len(teta)
    l_v_3 = [0] * len(teta)
    p_i_1 = [0] * len(teta)
    p_i_2 = [0] * len(teta)
    p_i_3 = [0] * len(teta)
    d_i_1 = [0] * len(teta)
    d_i_2 = [0] * len(teta)
    d_i_3 = [0] * len(teta)
    for i in range(len(teta)):
        l_v_1[i] = log_ver(df.iloc[0].tolist(), teta[i])
        l_v_2[i] = log_ver(df.iloc[1].tolist(), teta[i])
        l_v_3[i] = log_ver(df.iloc[2].tolist(), teta[i])
        p_i_1[i] = prvi_izvod((df.iloc[0].tolist()), teta[i])
        p_i_2[i] = prvi_izvod((df.iloc[1].tolist()), teta[i])
        p_i_3[i] = prvi_izvod(df.iloc[2].tolist(), teta[i])
        d_i_1[i] = drugi_izvod(df.iloc[0].tolist(), teta[i])
        d_i_2[i] = drugi_izvod(df.iloc[1].tolist(), teta[i])
        d_i_3[i] = drugi_izvod(df.iloc[2].tolist(), teta[i])

    plt.figure(1)
    plt.subplot(3, 3, 1)
    plt.plot(teta, l_v_1)
    plt.title("log ver 1")
    plt.subplot(3, 3, 2)
    plt.plot(teta, l_v_2)
    plt.title("log ver 2")
    plt.subplot(3, 3, 3)
    plt.plot(teta, l_v_3)
    plt.title("log ver 3")
    plt.subplot(3, 3, 4)
    plt.plot(teta, p_i_1)
    plt.subplot(3, 3, 5)
    plt.plot(teta, p_i_2)
    plt.subplot(3, 3, 6)
    plt.plot(teta, p_i_3)
    plt.subplot(3, 3, 7)
    plt.plot(teta, d_i_1)
    plt.subplot(3, 3, 8)
    plt.plot(teta, d_i_2)
    plt.subplot(3, 3, 9)
    plt.plot(teta, d_i_3)
    plt.show()

    teta_k1 = [0] * 10
    teta_k2 = [0] * 10
    teta_k3 = [0] * 10

    i = 0
    proc_preth1 = -3
    proc_preth2 = 2
    proc_preth3 = 2
    proc_sled1 = proc_preth1 - prvi_izvod(df.iloc[17].tolist(), proc_preth1) / drugi_izvod(df.iloc[17].tolist(),
                                                                                           proc_preth1)
    proc_sled2 = proc_preth2 - prvi_izvod(df.iloc[5].tolist(), proc_preth2) / drugi_izvod(df.iloc[5].tolist(),
                                                                                          proc_preth2)
    proc_sled3 = proc_preth3 - prvi_izvod(df.iloc[6].tolist(), proc_preth3) / drugi_izvod(df.iloc[6].tolist(),
                                                                                          proc_preth3)

    while (i < 10 and abs(proc_sled1 - proc_preth1) > 0.1):
        teta_k1[i] = proc_preth1
        proc_preth1 = proc_sled1
        proc_sled1 = proc_preth1 - prvi_izvod(df.iloc[17].tolist(), proc_preth1) / drugi_izvod(df.iloc[17].tolist(),
                                                                                               proc_preth1)
        i += 1

    i = 0
    while (i < 10 and abs(proc_sled2 - proc_preth2) > 0.1):
        teta_k2[i] = proc_preth2
        proc_preth2 = proc_sled2
        proc_sled2 = proc_preth2 - prvi_izvod(df.iloc[5].tolist(), proc_preth2) / drugi_izvod(df.iloc[5].tolist(),
                                                                                              proc_preth2)
        i += 1

    i = 0

    while (i < 10 and abs(proc_sled3 - proc_preth3) > 0.1):
        teta_k3[i] = proc_preth3
        proc_preth3 = proc_sled3
        proc_sled3 = proc_preth3 - prvi_izvod(df.iloc[6].tolist(), proc_preth3) / drugi_izvod(df.iloc[6].tolist(),
                                                                                              proc_preth3)
        i += 1

    vekt = np.linspace(1, 10, 10)
    plt.figure(figsize=(15, 15))
    plt.title("promena procene po iteracijama")
    plt.subplot(3, 1, 1)
    plt.plot(vekt, teta_k1)
    plt.subplot(3, 1, 2)
    plt.plot(vekt, teta_k2)
    plt.subplot(3, 1, 3)
    plt.plot(vekt, teta_k3)
    plt.show()

    i = 0
    teta_est = list(range(1, 100))
    for i in range(99):
        poc = 0
        k = emv(df.iloc[i].tolist(), 2, 0.1, 10)
        while abs(k) > 10:
            k = emv(df.iloc[i].tolist(), poc, 0.1, 20)
            poc = poc + 0.1
        # m = emv(df.iloc[i].tolist(),0,0.1,10)
        # n = emv(df.iloc[i].tolist(),1,0.1,10)
        teta_est[i] = k

    for i in range(len(teta_est)):
        if abs(teta_est[i]) > 10:
            teta_est[i] = np.random.normal()

    plt.figure(2)
    plt.hist(teta_est)
    plt.title("Histogram svih 100 eksperimenata")
    plt.show()



