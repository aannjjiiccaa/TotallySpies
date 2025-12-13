import cv2
import numpy as np
import pywt
from steglib.base import StegAlgo

class DWTRGBSteg(StegAlgo):
    def __init__(self):
        self.name = "DWT_RGB"

    def getCapacity(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return False

        capacity_bits = 0
        for c in range(img.shape[2]):
            channel = img[:, :, c]
            channel_padded, _ = self.pad_to_even(channel)
            cA, (cH, cV, cD) = pywt.dwt2(channel_padded.astype(np.float32),'haar', mode='periodization')
            capacity_bits += cH.size + cV.size + cD.size
        return capacity_bits // 8 

    def capacity(self, image_path, secret_message):
        total_capacity_bytes = self.getCapacity(image_path)
        message_bytes = len(secret_message.encode('utf-8'))
        return total_capacity_bytes >= (message_bytes + 4)

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

    def text_to_bits(self, text):
        if isinstance(text, str):
            bytes_data = text.encode('utf-8')
        else:
            bytes_data = text
        return ''.join(f'{byte:08b}' for byte in bytes_data)

    def bits_to_text(self, bits):
        bits = bits[:len(bits) - (len(bits) % 8)]
        bytes_list = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
        return bytes(bytes_list).decode('utf-8', errors='ignore')

    @StegAlgo.runtime
    def embed(self, image_path, secret_message, output_path=None):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")

        message_bits = self.text_to_bits(secret_message)
        message_length = len(message_bits)
        full_bits = f'{message_length:032b}' + message_bits
        
        stego_img = np.zeros_like(img)
        bit_position = 0
        total_bits = len(full_bits)

        for c in range(img.shape[2]):
            channel = img[:, :, c]
            channel_padded, pad = self.pad_to_even(channel)
            cA, (cH, cV, cD) = pywt.dwt2(channel_padded.astype(np.float32), 'haar', mode='periodization')
            flat_H = np.round(cH).astype(np.int64).ravel()
            flat_V = np.round(cV).astype(np.int64).ravel()
            flat_D = np.round(cD).astype(np.int64).ravel()
            flat = np.concatenate([flat_H, flat_V, flat_D])
            
            for i in range(len(flat)):
                if bit_position >= total_bits:
                    break
                bit = int(full_bits[bit_position])
                flat[i] = (flat[i] & ~1) | bit
                bit_position += 1
            h_len = flat_H.size
            v_len = flat_V.size
            d_len = flat_D.size
            
            flat_H2 = flat[0:h_len].reshape(cH.shape)
            flat_V2 = flat[h_len:h_len + v_len].reshape(cV.shape)
            flat_D2 = flat[h_len + v_len:h_len + v_len + d_len].reshape(cD.shape)
            
            cH_mod = flat_H2.astype(np.float32)
            cV_mod = flat_V2.astype(np.float32)
            cD_mod = flat_D2.astype(np.float32)

            stego_channel = pywt.idwt2((cA, (cH_mod, cV_mod, cD_mod)), 'haar', mode='periodization')
            stego_channel = np.clip(stego_channel, 0, 255)
            stego_img[:, :, c] = self.unpad(stego_channel, pad).astype(np.uint8)

        if output_path:
            cv2.imwrite(output_path, stego_img)

        return stego_img

    def extract(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")

        extracted_bits = []
        total_extracted_bits = 0
        message_length = None
        
        for c in range(img.shape[2]):
            channel = img[:, :, c]
            channel_padded, pad = self.pad_to_even(channel)
            cA, (cH, cV, cD) = pywt.dwt2(channel_padded.astype(np.float32),'haar', mode='periodization')

            flat_H = np.round(cH).astype(np.int64).ravel()
            flat_V = np.round(cV).astype(np.int64).ravel()
            flat_D = np.round(cD).astype(np.int64).ravel()
            flat = np.concatenate([flat_H, flat_V, flat_D])

            for i in range(len(flat)):
                if message_length is None and total_extracted_bits < 32:
                    extracted_bits.append(str(flat[i] & 1))
                    total_extracted_bits += 1
                    
                    if total_extracted_bits == 32:
                        length_bits = ''.join(extracted_bits[:32])
                        message_length = int(length_bits, 2)
                        total_needed_bits = 32 + message_length
                elif message_length is not None and total_extracted_bits < total_needed_bits:
                    extracted_bits.append(str(flat[i] & 1))
                    total_extracted_bits += 1
                else:
                    break
            
            if message_length is not None and total_extracted_bits >= total_needed_bits:
                break

        if message_length is None:
            raise ValueError("Could not extract valid message length")
        message_bits = ''.join(extracted_bits[32:32 + message_length])
        return self.bits_to_text(message_bits)