import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import inv

def generator():
    t = np.arange(1, 101)
    S = np.genfromtxt("../datasets/kf.csv")
    A = np.array([[1, 1, 0.5], [0, 1, 1], [0, 0, 1]])
    B = np.array([0.5, 1, 1])
    H = np.array([[1, 0, 0]])
    return t, S, A, B, H


def main():
    t = np.arange(1, 101)
    S = np.genfromtxt("../datasets/kf.csv")
    A = np.array([[1, 1, 0.5], [0, 1, 1], [0, 0, 1]])
    B = np.array([0.5, 1, 1])
    H = np.array([[1, 0, 0]])
    q1 = 10 / 100
    q2 = 1 / 100
    sigma_w = 10
    Q1 = np.outer(B, B) * q1 ** 2
    Q2 = np.outer(B, B) * q2 ** 2
    R = np.array([[sigma_w ** 2]])
    s_est = np.array([0, 0, 0])
    M_est = np.zeros((3, 3))
    s_est_z = np.zeros((3, 100))
    K_z = np.zeros((3, 100))
    M_est_z = np.zeros((3, 100))

    p_e1 = np.zeros(100)
    p_e2 = np.zeros(100)
    v_est1 = np.zeros(100)
    v_est2 = np.zeros(100)
    a_est1 = np.zeros(100)
    a_est2 = np.zeros(100)

    Kov_i = np.zeros((3, 100))

    for i in range(len(S)):
        if (i >= 0 and i <= 29) or (i >= 70 and i <= 99):
            s_pred = A @ s_est
            M_pred = A @ M_est @ A.T + Q1

            K = M_pred @ H.T @ inv(H @ M_pred @ H.T + R)
            s_est = s_pred + K @ (S[i] - H @ s_pred)
            M_est = (np.eye(3) - K @ H) @ M_pred

            s_est_z[:, i] = s_est
            K_z[:, i] = K.flatten()
            M_est_z[:, i] = np.diag(M_est)
            p_e1[i] = s_est[0] + 2 * np.sqrt(M_est[0, 0])
            p_e2[i] = s_est[0] - 2 * np.sqrt(M_est[0, 0])
            v_est1[i] = s_est[1] + 2 * np.sqrt(M_est[1, 1])
            v_est2[i] = s_est[1] - 2 * np.sqrt(M_est[1, 1])
            a_est1[i] = s_est[2] + 2 * np.sqrt(M_est[2, 2])
            a_est2[i] = s_est[2] - 2 * np.sqrt(M_est[2, 2])
            Kov_i[0, i] = (H @ np.diag(M_pred[:, 0]) @ np.transpose(H) + R).item()
            Kov_i[1, i] = (H @ np.diag(M_pred[:, 1]) @ np.transpose(H) + R).item()
            Kov_i[2, i] = (H @ np.diag(M_pred[:, 2]) @ np.transpose(H) + R).item()

        elif 40 <= i <= 49:
            s_pred = A @ s_est
            M_pred = A @ M_est @ A.T + Q2

            K = np.zeros((3, 1))
            s_est = s_pred
            M_est = M_pred

            s_est_z[:, i] = s_est
            K_z[:, i] = K.flatten()
            M_est_z[:, i] = np.diag(M_est)
            p_e1[i] = s_est[0] + 2 * np.sqrt(M_est[0, 0])
            p_e2[i] = s_est[0] - 2 * np.sqrt(M_est[0, 0])
            v_est1[i] = s_est[1] + 2 * np.sqrt(M_est[1, 1])
            v_est2[i] = s_est[1] - 2 * np.sqrt(M_est[1, 1])
            a_est1[i] = s_est[2] + 2 * np.sqrt(M_est[2, 2])
            a_est2[i] = s_est[2] - 2 * np.sqrt(M_est[2, 2])
            Kov_i[0, i] = (H @ np.diag(M_pred[:, 0]) @ np.transpose(H) + R).item()
            Kov_i[1, i] = (H @ np.diag(M_pred[:, 1]) @ np.transpose(H) + R).item()
            Kov_i[2, i] = (H @ np.diag(M_pred[:, 2]) @ np.transpose(H) + R).item()

        else:
            s_pred = A @ s_est
            M_pred = A @ M_est @ A.T + Q2

            K = M_pred @ H.T @ inv(H @ M_pred @ H.T + R)
            s_est = s_pred + K @ (S[i] - H @ s_pred)
            M_est = (np.eye(3) - K @ H) @ M_pred

            s_est_z[:, i] = s_est
            K_z[:, i] = K.flatten()
            M_est_z[:, i] = np.diag(M_est)
            p_e1[i] = s_est[0] + 2 * np.sqrt(M_est[0, 0])
            p_e2[i] = s_est[0] - 2 * np.sqrt(M_est[0, 0])
            v_est1[i] = s_est[1] + 2 * np.sqrt(M_est[1, 1])
            v_est2[i] = s_est[1] - 2 * np.sqrt(M_est[1, 1])
            a_est1[i] = s_est[2] + 2 * np.sqrt(M_est[2, 2])
            a_est2[i] = s_est[2] - 2 * np.sqrt(M_est[2, 2])
            Kov_i[0, i] = (H @ np.diag(M_pred[:, 0]) @ np.transpose(H) + R).item()
            Kov_i[1, i] = (H @ np.diag(M_pred[:, 1]) @ np.transpose(H) + R).item()
            Kov_i[2, i] = (H @ np.diag(M_pred[:, 2]) @ np.transpose(H) + R).item()

    plt.figure(1)

    plt.fill_between(t, p_e2, p_e1, color='r', alpha=0.5, edgecolor='none')

    plt.plot(t, S.T, 'g', linewidth=1.5)

    plt.plot(t, s_est_z[0, :], 'b', linewidth=1.5)
    plt.title('Izmerena i estimirana pozicija')
    plt.legend(['2σ int', 'izmerena', 'estimirana'])
    plt.show()

    plt.figure(2)
    plt.fill_between(t, v_est2, v_est1, color='r', alpha=0.5, edgecolor='none')
    plt.plot(t, s_est_z[1, :], linewidth=1.5)
    plt.title('Estimirana brzina')
    plt.legend(['2σ int', 'brzina'])
    plt.show()

    plt.figure(3)
    plt.fill_between(t, a_est2, a_est1, color='r', alpha=0.5, edgecolor='none')
    plt.plot(t, s_est_z[2, :], linewidth=1.5)
    plt.title('Estimirano ubrzanje')
    plt.legend(['2σ int', 'ubrzanje'])
    plt.show()

    plt.figure(4)
    plt.plot(t, K_z[0, :], linewidth=1)
    plt.plot(t, K_z[1, :], linewidth=1)
    plt.plot(t, K_z[2, :], linewidth=1)
    plt.title('Kalmanovo pojacanje')
    plt.legend(['pozicija', 'brzina', 'ubrzanje'])
    plt.show()

    plt.figure(5)
    plt.plot(t, Kov_i[0, :], linewidth=1.5)
    plt.plot(t, Kov_i[1, :], linewidth=1.5)
    plt.plot(t, Kov_i[2, :], linewidth=1.5)
    plt.title('Autokorelaciona funkcija sekvence inovacija')
    plt.legend(['pozicija', 'brzina', 'ubrzanje'])
    plt.show()

if __name__ == '__main__':
    main()

