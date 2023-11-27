import numpy as np
import cv2 as cv
import random
import math
import sys

img_name = sys.argv[1]
wm_name = sys.argv[3]
watermarked_img = sys.argv[2]
watermarked_extracted = sys.argv[4]
key = 50
bs = 8
w1 = 64
w2= 64
fact = 8
indx = 0
indy = 0
b_cut = 50
flag = 1

def psnr(img1, img2):
	mse = np.mean( (img1 - img2) ** 2 )
	if mse == 0:
		return 100
	PIXEL_MAX = 255.0
	return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

def NCC(img1, img2):
	return abs(np.mean(np.multiply((img1-np.mean(img1)),(img2-np.mean(img2))))/(np.std(img1)*np.std(img2)))

def watermark_image(img, wm):
	c1, c2 = np.size(img,0), np.size(img,1)
	c1x = c1
	c2x = c2
	c1-= b_cut*2
	c2-= b_cut*2
	w1, w2 = np.size(wm,0), np.size(wm, 1)
	if(c1*c2//(bs*bs) < w1*w2):
		print("watermark_too_large. ")
		flag = 0
		return img
	st = set()
	blocks = (c1//bs)*(c2//bs)
	print("Blocks_availaible_{} ".format(blocks))
	blocks_needed = w1*w2
	i = 0
	j = 0
	
	imf = np.float32(img)
	
	while(i<c1x):
		while(j<c2x):		
			dst = cv.dct(imf[i:i+bs, j:j+bs])
			imf[i:i+bs, j:j+bs] = cv.idct(dst)
			j+=bs
		j = 0
		i+=bs
	random.seed(key)
	
	i = 0
	print("Blocks_needed_{} ".format(blocks_needed))
	cnt = 0
	
	while(i < blocks_needed):				
		to_embed = int(wm[i//w2][i%w2])
		ch = 0
		if(to_embed >= 127):
			to_embed = 1
			ch = 255
		else:
			to_embed = 0
		
		wm[i//w2][i%w2] = ch
		x = random.randint(1, blocks)
		if(x in st):
			continue
		st.add(x)
		n = c1//bs
		m = c2//bs
		ind_i = (x//m)*bs + b_cut
		ind_j = (x%m)*bs + b_cut
		dct_block = cv.dct(imf[ind_i:ind_i+bs, ind_j:ind_j+bs]/1)
		elem = dct_block[indx][indy]
		elem /= fact
		ch = elem
		if(to_embed%2==1):	
			if(int(math.ceil(elem))%2 == 1):
				elem = int(math.ceil(elem))
			else:
				elem = int(math.ceil(elem))-1
		else:
			if(int(math.ceil(elem))%2 == 0):
				elem = int(math.ceil(elem))
			else:
				elem = int(math.ceil(elem)-1)
		
		dct_block[indx][indy] = int(elem*fact)
		
		imf[ind_i:ind_i+bs, ind_j:ind_j+bs] = cv.idct(dct_block)
		i += 1
	print("PSNR:{} ".format(psnr(imf, img)))
	return imf

def extract_watermark(img, ext_name):
	c1x, c2x = np.size(img,0), np.size(img,1)
	c1 = c1x - b_cut*2
	c2 = c2x-b_cut*2
	blocks = (c1//bs)*(c2//bs)
	blocks_needed = w1*w2
	wm = [[0 for x in range(w1)] for y in range(w2)]
	st = set()
	random.seed(key)
	i = 0
	while(i<blocks_needed):
		curr = 0
		x = random.randint(1, blocks)
		if(x in st):
			continue
		st.add(x)
		m = c2//bs
		ind_i = (x//m)*bs + b_cut
		ind_j = (x%m)*bs + b_cut
		dct_block = cv.dct(img[ind_i:ind_i+bs, ind_j:ind_j+bs]/1)
		elem = dct_block[indx][indy]
		elem = math.floor(elem+0.5)
		elem /= fact
		if(elem%2 == 0):
			curr = 0
		else:
			curr = 255
		wm[i//w2][i%w2] = curr
		i+=1
	wm = np.array(wm)
	cv.imwrite(ext_name , wm)
	print("Watermark_extracted! ")
	return wm

if __name__ == "__main__":
	print("===================================EMBEDDING_WATERMARK=================================== ")
	image = cv.imread(img_name)
	blue, green, red = cv.split(image)
	img =  cv.imread(img_name, 0) 
	wa = cv.imread(wm_name, 0) 
	wm = cv.resize(wa, dsize=(64, 64), interpolation=cv.INTER_CUBIC)
	wlol = watermark_image(red, wm)
	wloa = np.uint8(wlol)
	rd_image = cv.merge((blue, green, wloa))
	cv.imwrite(watermarked_img, rd_image)
	print("Watermarking_Done! ")
	if flag == 1:
		print("===================================EXTRACTING_WATERMARK=================================== ")
		lmfao = cv.imread(watermarked_img)
		wblue, wgreen, wred = cv.split(lmfao)
		wx = extract_watermark(wlol, watermarked_extracted)
		print("NCC:{} ".format(NCC(wa, wx)))