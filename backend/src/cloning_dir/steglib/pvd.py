import cv2
import numpy as np
from .base import StegAlgo


class PVDSteg(StegAlgo):
    def __init__(self):
        self.name = "PVD"
        self.ranges = [
            (0, 7),
            (8, 15),
            (16, 31),
            (32, 63),
            (64, 127),
            (128, 255)
        ]

    def get_range(self, diff):
        for r in self.ranges:
            if r[0] <= diff <= r[1]:
                return r
        return self.ranges[-1]
    
    def getCapacity(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError("Image not found.")

        h, w, _ = img.shape
        flat = img.reshape(-1, 3)
        pixel_pairs = (len(flat) - 1) // 2
        channels = 3
        avg_bits_per_pair = 2
        estimated_capacity = pixel_pairs * channels * avg_bits_per_pair
        return estimated_capacity//8

    def capacity(self, image_path, secret_message):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError("Image not found.")

        h, w, _ = img.shape
        flat = img.reshape(-1, 3)
        pixel_pairs = (len(flat) - 1) // 2
        channels = 3
        avg_bits_per_pair = 2
        estimated_capacity = pixel_pairs * channels * avg_bits_per_pair
        message_bits = len(secret_message) * 8 + 32
        return estimated_capacity >= message_bits

    @StegAlgo.runtime
    def embed(self, image_path, secret_message, output_path=None):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError("Image not found.")
        h, w, _ = img.shape
        flat = img.reshape(-1, 3)

        message_bits = self.text_to_bits(secret_message)
        full_bits = f'{len(message_bits):032b}' + message_bits
        bit_index = 0
        i = 0
        while i < len(flat) - 1 and bit_index < len(full_bits):
            for c in range(3):
                if bit_index >= len(full_bits):
                    break

                p1 = int(flat[i][c])
                p2 = int(flat[i + 1][c])
                diff = abs(p1 - p2)
                rmin, rmax = self.get_range(diff)
                range_width = rmax - rmin + 1
                bit_start = bit_index
                n_bits = int(np.floor(np.log2(range_width)))
                remaining_bits = len(full_bits) - bit_index
                if n_bits > remaining_bits:
                    bits_to_embed = full_bits[bit_index:] + '0' * (n_bits - remaining_bits)
                else:
                    bits_to_embed = full_bits[bit_index: bit_index + n_bits]
                bit_end = bit_index + n_bits - 1

                value = int(bits_to_embed, 2)
                new_diff = rmin + value
                if p1 > p2:
                    if p1 - new_diff >= 0:
                        p2n = p1 - new_diff
                        p1n = p1
                    else:
                        p1n = new_diff + p2
                        p2n = p2
                else:
                    if p1 + new_diff <= 255:
                        p2n = p1 + new_diff
                        p1n = p1
                    else:
                        p1n = p2 - new_diff
                        p2n = p2

                p1n = np.clip(p1n, 0, 255)
                p2n = np.clip(p2n, 0, 255)
                
                actual_new_diff = abs(p1n - p2n)
                flat[i][c] = p1n
                flat[i + 1][c] = p2n
                bit_index += n_bits

            i += 2

        remaining_bits = len(full_bits) - bit_index
        if remaining_bits > 0:
            raise ValueError( f"Message too long to embed. {remaining_bits} bits left unembedded.")

        stego_image = flat.reshape((h, w, 3))
        if output_path:
            cv2.imwrite(output_path, stego_image)
            print(f"Message embedded into {output_path}")

        return stego_image

    @StegAlgo.runtime
    def extract(self, stego_image_path):
        img = cv2.imread(stego_image_path)
        if img is None:
            raise FileNotFoundError("Stego image not found.")

        h, w, _ = img.shape
        flat = img.reshape(-1, 3)

        bits = ""
        i = 0
        total_bits = None

        while i < len(flat) - 1:
            for c in range(3):
                p1 = int(flat[i][c])
                p2 = int(flat[i + 1][c])
                diff = abs(p1 - p2)
                rmin, rmax = self.get_range(diff)
                n_bits = int(np.floor(np.log2(rmax - rmin + 1)))
                if n_bits == 0:
                    continue
                if not (rmin <= diff <= rmax):
                    continue
                value = diff - rmin
                bits += f'{value:0{n_bits}b}'

                if total_bits is None and len(bits) >= 32:
                    total_bits = int(bits[:32], 2)

                if total_bits is not None and len(bits) >= 32 + total_bits:
                    msg_bits = bits[32:32 + total_bits]
                    return self.bits_to_text(msg_bits)

            i += 2
        raise ValueError("Message could not be fully extracted.")
