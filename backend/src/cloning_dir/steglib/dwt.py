import cv2
import numpy as np
import pywt
from steglib.base import StegAlgo

class DWTSteg(StegAlgo):
    def __init__(self):
        self.name = "DWT"

    def getCapacity(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        img_padded, _ = self.pad_to_even(img)
        cA, (cH, cV, cD) = pywt.dwt2(img_padded.astype(np.float32), 'haar', mode='periodization')
        capacity_bits = cH.size + cV.size + cD.size
        return capacity_bits//8

    def capacity(self, image_path, secret_message):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        img_padded, _ = self.pad_to_even(img)
        cA, (cH, cV, cD) = pywt.dwt2(img_padded.astype(np.float32), 'haar', mode='periodization')
        capacity_bits = cH.size + cV.size + cD.size
        message_bits = len(self.text_to_bits(secret_message))
        return capacity_bits >= (32 + message_bits)

    def pad_to_even(self, arr):
        h, w = arr.shape
        pad_h = 0 if h % 2 == 0 else 1
        pad_w = 0 if w % 2 == 0 else 1
        if pad_h == 0 and pad_w == 0:
            return arr, (0, 0)
        padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode='edge')
        return padded, (pad_h, pad_w)

    def unpad(self, arr, pad):
        pad_h, pad_w = pad
        if pad_h == 0 and pad_w == 0:
            return arr
        h = arr.shape[0] - pad_h
        w = arr.shape[1] - pad_w
        return arr[:h, :w]

    @StegAlgo.runtime
    def embed(self, image_path, secret_message, output_path=None):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read image")
        img_padded, pad = self.pad_to_even(img)
        img_f = img_padded.astype(np.float32)
        cA, (cH, cV, cD) = pywt.dwt2(img_f, 'haar', mode='periodization')

        flat_H = np.round(cH).astype(np.int64).ravel()
        flat_V = np.round(cV).astype(np.int64).ravel()
        flat_D = np.round(cD).astype(np.int64).ravel()
        flat = np.concatenate([flat_H, flat_V, flat_D])

        message_bits = self.text_to_bits(secret_message)
        full_bits = f'{len(message_bits):032b}' + message_bits

        if len(full_bits) > flat.size:
            raise ValueError("Message too large for image capacity.")

        for i, bit in enumerate(full_bits):
            flat[i] = (int(flat[i]) & ~1) | int(bit)
        h_len = flat_H.size
        v_len = flat_V.size
        d_len = flat_D.size
        flat_H2 = flat[0:h_len].reshape(cH.shape)
        flat_V2 = flat[h_len:h_len + v_len].reshape(cV.shape)
        flat_D2 = flat[h_len + v_len:].reshape(cD.shape)
        cH_mod = flat_H2.astype(np.float32)
        cV_mod = flat_V2.astype(np.float32)
        cD_mod = flat_D2.astype(np.float32)

        stego = pywt.idwt2((cA, (cH_mod, cV_mod, cD_mod)), 'haar', mode='periodization')
        stego = np.clip(stego, 0, 255)
        stego = self.unpad(stego, pad).astype(np.uint8)

        if output_path:
            cv2.imwrite(output_path, stego)

        return stego

    def extract(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read image")
        img_padded, pad = self.pad_to_even(img)
        img_f = img_padded.astype(np.float32)

        cA, (cH, cV, cD) = pywt.dwt2(img_f, 'haar', mode='periodization')

        flat_H = np.round(cH).astype(np.int64).ravel()
        flat_V = np.round(cV).astype(np.int64).ravel()
        flat_D = np.round(cD).astype(np.int64).ravel()
        flat = np.concatenate([flat_H, flat_V, flat_D])
        if flat.size < 32:
            raise ValueError("Image too small / no message.")
        length_bits = ''.join(str(int(flat[i]) & 1) for i in range(32))
        message_length = int(length_bits, 2)
        if 32 + message_length > flat.size:
            raise ValueError("Invalid or corrupted message length.")

        message_bits = ''.join(str(int(flat[i]) & 1) for i in range(32, 32 + message_length))
        return self.bits_to_text(message_bits)