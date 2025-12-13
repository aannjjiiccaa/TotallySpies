import bitstring
import cv2
import numpy as np

from .base import StegAlgo

JPEG_STD_LUM_QUANT_TABLE = np.asarray([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 36, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
],
    dtype=np.float32)

JPEG_STD_CHROM_QUANT_TABLE = np.asarray([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99]
], dtype=np.float32)


class DCTSteg(StegAlgo):
    def __init__(self):
        self.name = "DCT"
        self.NUM_CHANNELS = 3

    @staticmethod
    def zigzag(block):
        rows, cols = block.shape
        solution = []
        for s in range(rows + cols - 1):
            if s % 2 == 0:
                for i in range(s + 1):
                    j = s - i
                    if i < rows and j < cols:
                        solution.append(block[i, j])
            else:
                for j in range(s + 1):
                    i = s - j
                    if i < rows and j < cols:
                        solution.append(block[i, j])
        return solution

    @staticmethod
    def inverse_zigzag(arr, vmax=8, hmax=8):
        block = np.zeros((vmax, hmax))
        index = 0
        for s in range(vmax + hmax - 1):
            if s % 2 == 0:
                for i in range(s + 1):
                    j = s - i
                    if i < vmax and j < hmax:
                        block[i, j] = arr[index]
                        index += 1
            else:
                for j in range(s + 1):
                    i = s - j
                    if i < vmax and j < hmax:
                        block[i, j] = arr[index]
                        index += 1
        return block

    @staticmethod
    def divide_blocks(image):
        blocks = []
        for vertical in np.vsplit(image, int(image.shape[0] / 8)):
            for horizontal in np.hsplit(vertical, int(image.shape[1] / 8)):
                blocks.append(horizontal)
        return blocks

    @staticmethod
    def revert_blocks(width, blocks):
        image_rows = []
        temp = []
        for i in range(len(blocks)):
            if i > 0 and not (i % int(width / 8)):
                image_rows.append(temp)
                temp = [blocks[i]]
            else:
                temp.append(blocks[i])
        image_rows.append(temp)

        return np.block(image_rows)
    
    def getCapacity(self, image_path):
        image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        height, width = image.shape[:2]
        height = ((height + 7) // 8) * 8
        width  = ((width  + 7) // 8) * 8
        num_blocks = (height // 8) * (width // 8)
        estimated_usable_coeffs_per_block = 4
        total_capacity_bits = num_blocks * estimated_usable_coeffs_per_block * self.NUM_CHANNELS
        return total_capacity_bits//8

    def capacity(self, image_path, secret_message):
        image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        height, width = image.shape[:2]
        while height % 8:
            height += 1
        while width % 8:
            width += 1
        num_blocks = (height // 8) * (width // 8)
        estimated_usable_coeffs_per_block = 4
        total_capacity_bits = num_blocks * estimated_usable_coeffs_per_block * self.NUM_CHANNELS
        message_bytes = len(secret_message.encode('utf-8'))
        message_bits_needed = message_bytes * 8 + 32
        return total_capacity_bits >= message_bits_needed

    @staticmethod
    def embed_in_block(block, bitstream, bit_pos):
        for i in range(1, len(block)):
            coeff = int(block[i])
            if abs(coeff) > 1:
                if bit_pos >= len(bitstream):
                    break

                bit = bitstream[bit_pos]
                bit_pos += 1
                if (coeff & 1) != bit:
                    if coeff > 0:
                        coeff = coeff + 1 if bit == 1 else coeff - 1
                    elif coeff < 0:
                        coeff = coeff - 1 if bit == 1 else coeff + 1
                    else:
                        coeff = 1 if bit == 1 else -1

                block[i] = float(coeff)

        return block, bit_pos

    @StegAlgo.runtime
    def embed(self, image_path, secret_message, output_path=None):
        raw_cover_image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
        if raw_cover_image is None:
            raise FileNotFoundError(f"Cover image not found at {image_path}")

        height, width = raw_cover_image.shape[:2]
        while height % 8:
            height += 1
        while width % 8:
            width += 1

        valid_dim = (width, height)
        padded_image = cv2.resize(raw_cover_image, valid_dim)

        cover_image_f32 = np.float32(padded_image)
        img = cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb)
        channels = [
            self.divide_blocks(img[:, :, 0]),  
            self.divide_blocks(img[:, :, 1]), 
            self.divide_blocks(img[:, :, 2]), 
        ]
        height, width = img.shape[:2]
        message_bytes = secret_message.encode('utf-8')
        secret_bits = bitstring.BitArray(bytes=message_bytes)
        
        full_bits = bitstring.BitArray(uint=len(message_bytes), length=32) + secret_bits
        total_bits = len(full_bits)
        changes = []

        bit_pos = 0
        stego_image = np.empty_like(cover_image_f32)
        
        for chan_index in range(self.NUM_CHANNELS):
            dct_blocks = [cv2.dct(block) for block in channels[chan_index]]
            if chan_index == 0:
                table = JPEG_STD_LUM_QUANT_TABLE
            else:
                table = JPEG_STD_CHROM_QUANT_TABLE

            dct_quants = [np.around(np.divide(item, table)) for item in dct_blocks]
            sorted_coefficients = [self.zigzag(block) for block in dct_quants]
            embedded_blocks = []
            
            for block in sorted_coefficients:
                if bit_pos >= total_bits:
                    embedded_blocks.append(block)
                    continue

                block, bit_pos = self.embed_in_block(block, full_bits, bit_pos)
                embedded_blocks.append(block)
                
            desorted_coefficients = [self.inverse_zigzag(block, vmax=8, hmax=8) for block in embedded_blocks]
            dct_dequants = [np.multiply(data, table) for data in desorted_coefficients]
            idct_blocks = [cv2.idct(block) for block in dct_dequants]

            stego_image[:, :, chan_index] = np.asarray(self.revert_blocks(width, idct_blocks))

        stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)
        final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))
        
        if output_path:
            cv2.imwrite(output_path, final_stego_image)
            print(f"Message embedded and stego image saved to {output_path}")
            
        return final_stego_image

    @StegAlgo.runtime
    def extract(self, stego_image_path):
        stego_image = cv2.imread(stego_image_path, flags=cv2.IMREAD_COLOR)
        if stego_image is None:
            raise FileNotFoundError(f"Stego image not found at {stego_image_path}")

        stego_image_f32 = np.float32(stego_image)
        img = cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb)
        channels = [
            self.divide_blocks(img[:, :, 0]),
            self.divide_blocks(img[:, :, 1]),
            self.divide_blocks(img[:, :, 2]),
        ]

        extracted_bits = bitstring.BitArray()
        
        for channel in range(self.NUM_CHANNELS):
            dct_blocks = [cv2.dct(block) for block in channels[channel]]
            if channel == 0:
                table = JPEG_STD_LUM_QUANT_TABLE
            else:
                table = JPEG_STD_CHROM_QUANT_TABLE
                
            dct_quants = [np.around(np.divide(item, table)) for item in dct_blocks]
            sorted_coefficients = [self.zigzag(block) for block in dct_quants]
            
            for blk in sorted_coefficients:
                for i in range(1, len(blk)):
                    coeff = int(blk[i])
                    if abs(coeff) > 1:
                        bit = coeff & 1
                        extracted_bits.append('0b1' if bit else '0b0')

        if len(extracted_bits) < 32:
            raise ValueError("Not enough bits extracted to read message length!")
        message_length_bytes = extracted_bits[0:32].uint
        required_bits = message_length_bytes * 8
        
        if len(extracted_bits) < 32 + required_bits:
            raise ValueError(f"Not enough bits extracted! Need {32 + required_bits}, got {len(extracted_bits)}")
        
        message_bits = extracted_bits[32:32 + required_bits]
        message_bytes = message_bits.tobytes()
        
        try:
            message = message_bytes.decode('utf-8')
        except UnicodeDecodeError:
            message = message_bytes.decode('latin-1')
            
        return message