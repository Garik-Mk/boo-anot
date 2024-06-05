import numpy as np
import cv2
import random

def choose_block(sample, block_size):
    h, w, _ = sample.shape
    y = random.randint(0, h - block_size)
    x = random.randint(0, w - block_size)
    return sample[y:y+block_size, x:x+block_size]

def overlap_error(block, block_top, block_left, overlap):
    if block_top is not None and block_left is not None:
        error = np.sum((block[:overlap, :] - block_top[-overlap:, :])**2) + np.sum((block[:, :overlap] - block_left[:, -overlap:])**2)
    elif block_top is not None:
        error = np.sum((block[:overlap, :] - block_top[-overlap:, :])**2)
    elif block_left is not None:
        error = np.sum((block[:, :overlap] - block_left[:, -overlap:])**2)
    else:
        error = 0
    return error

def find_best_block(sample, block_size, overlap, block_top, block_left):
    best_block = None
    best_error = float('inf')
    h, w, _ = sample.shape
    
    for _ in range(100):
        block = choose_block(sample, block_size)
        error = overlap_error(block, block_top, block_left, overlap)
        if error < best_error:
            best_error = error
            best_block = block
            
    return best_block

def synthesize_texture(sample, output_shape, block_size, overlap, existing_sample=None):
    h_out, w_out, _ = output_shape
    result = np.zeros(output_shape, dtype=sample.dtype)
    
    num_blocks_vert = (h_out - overlap) // (block_size - overlap)
    num_blocks_horiz = (w_out - overlap) // (block_size - overlap)
    
    for i in range(num_blocks_vert):
        for j in range(num_blocks_horiz):
            y = i * (block_size - overlap)
            x = j * (block_size - overlap)
            block_top = result[y - (block_size - overlap):y, x:x+block_size] if i > 0 else None
            block_left = result[y:y+block_size, x - (block_size - overlap):x] if j > 0 else None
            
            best_block = find_best_block(sample, block_size, overlap, block_top, block_left)
            result[y:y+block_size, x:x+block_size] = best_block
            
    return result


if __name__ == "__main__":
    sample_image = cv2.imread(r"C:\Users\garik\projects\dataset\dataset\negative\18.bmp")
    output_shape = (512, 512, 3)
    block_size = 10
    overlap = 3
    
    result = synthesize_texture(sample_image, output_shape, block_size, overlap)
    cv2.imwrite('synthesized_texture.jpg', result)
