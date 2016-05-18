import numpy
import copy

''' global variables '''

def normalize(img, **kwargs):

    def img_rescale(ret):
        '''rescale entire img set to values 0.0 ~ 1.0'''
        xl = img.shape[0]
        yl = img.shape[1]
        tl = img.shape[2]
        zl = img.shape[3]

        for t in range(tl):
            for z in range(zl):
                max = numpy.amax(img[:,:,t,z])
                for i in range(xl):
                    for j in range(yl):
                        ret[i,j,t,z] /= max
        return ret

    def patch_rescale(ret):
        '''rescale entire patch set to values between 0.0 ~ 1.0'''
        idx = img.shape[0]
        xl = img.shape[1]
        yl = img.shape[2]

        for i in range(idx):
            max = numpy.amax(img[i,:,:])
            for x in range(xl):
                for y in range(yl):
                    ret[i,x,y] /= max
        return ret

    flag = kwargs.pop("flag", None)

    if flag is None:
        raise AttributeError("specify flag = [img/patch]")

    ret = copy.deepcopy(img)
    if flag == "img":
        return img_rescale(ret)
    elif flag == "patch":
        return patch_rescale(ret)

if __name__ == "__main__":
    import conf
    from resize import resize

    img_ori = numpy.load(conf.dir_data_cine + "cinedata_1.npy")
    print(img_ori.shape)

    '''resized img to 256*256'''
    img_256 = resize(img_ori, mode = 256)
    print (img_256.shape)

    img_normalized_256 = normalize(img_256, flag = "img")
    print(img_normalized_256.shape)
    print(img_normalized_256)

























''' test resize

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.imshow(img3[:,:,1,1], cmap = plt.cm.gray)

plt.show()
'''

''' test img normalization

fig = plt.figure()
for ind_seg in range(nz):

    ax = fig.add_subplot(3, 5, ind_seg+1)
    ax.imshow(img3_normalized[:,:,1,ind_seg], cmap = plt.cm.gray)

plt.show()
'''

''' test patch normalization

fig = plt.figure()
ax2 = fig.add_subplot(2, 1, 2)
ax2.imshow(patch_normalized[555,:,:], cmap = plt.cm.gray)
plt.show()
'''

