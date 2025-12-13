import time
from abc import ABC, abstractmethod
from functools import wraps
from sewar import psnr, ssim
import scipy.stats as stats
import cv2
import numpy as np

class StegAlgo(ABC):

    @abstractmethod
    def embed(self, image_path,secret_message, output_path=None):
        pass

    @abstractmethod
    def extract(self, stego_image_path):
        pass

    @staticmethod
    def runtime(method):
        @wraps(method)
        def timed(*args, **kwargs):
            start_time = time.perf_counter()
            result = method(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            print(f"[{method.__name__}] executed in {duration:.6f} seconds")
            return result

        return timed

    @abstractmethod
    def capacity(self,image_path, secret_message):
        pass

    @abstractmethod
    def getCapacity(self,image_path):
        pass

    @staticmethod
    def text_to_bits(text):
        return ''.join(f'{ord(c):08b}' for c in text)

    @staticmethod
    def bits_to_text(bits):
        chars = [bits[i:i + 8] for i in range(0, len(bits), 8)]
        return ''.join([chr(int(char, 2)) for char in chars])

    @staticmethod
    def analysis(original, stego):
        orig = cv2.imread(original)
        stego = cv2.imread(stego)
        # psnr_value = cv2.PSNR(original, stego, 255)
        print("PSNR:", psnr(orig, stego))
        ssim_val, cs_val = ssim(orig, stego)
        print("SSIM:", float(ssim_val))
        print("CS:", float(cs_val))

        hist_orig = cv2.calcHist([orig], [0], None, [256], [0, 256]).ravel()
        hist_stego = cv2.calcHist([stego], [0], None, [256], [0, 256]).ravel()
        hist_orig_norm = hist_orig / hist_orig.sum()
        hist_stego_norm = hist_stego / hist_stego.sum()

        entropy_orig = stats.entropy(hist_orig_norm + 1e-12)
        entropy_stego = stats.entropy(hist_stego_norm + 1e-12)
        print("Entropy original:", entropy_orig, "after:", entropy_stego)
        bit_plane_orig = orig & 1
        bit_plane_stego = stego & 1
        changed_bits = np.sum(bit_plane_orig != bit_plane_stego)
        total_bits = orig.size
        print("LSB bits changed ratio:", changed_bits / total_bits)

        f_orig = np.fft.fft2(orig)
        f_stego = np.fft.fft2(stego)
        diff = np.abs(f_orig - f_stego)
        print("Mean freq diff:", diff.mean())

        edges_orig = cv2.Canny(orig, 100, 200)
        edges_stego = cv2.Canny(stego, 100, 200)
        edge_diff = np.sum(edges_orig != edges_stego) / edges_orig.size
        print("Edge map difference ratio:", edge_diff)
