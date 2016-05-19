# generate filters from two patients

from __future__ import print_function

import matplotlib.pyplot as plt
import copy
import random
import sys
import scipy

import os
import timeit

import numpy

import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams

from utils import tile_raster_images

try:
    import PIL.Image as Image
except ImportError:
    import Image

''' global variables '''

lim = 11 # row / col length of patch

class dA(object):
    """Denoising Auto-Encoder class (dA)

    A denoising autoencoders tries to reconstruct the input from a corrupted
    version of it by projecting it first in a latent space and reprojecting
    it afterwards back in the input space. Please refer to Vincent et al.,2008
    for more details. If x is the input then equation (1) computes a partially
    destroyed version of x by means of a stochastic mapping q_D. Equation (2)
    computes the projection of the input into the latent space. Equation (3)
    computes the reconstruction of the input, while equation (4) computes the
    reconstruction error.

    .. math::

        \tilde{x} ~ q_D(\tilde{x}|x)                                     (1)

        y = s(W \tilde{x} + b)                                           (2)

        x = s(W' y  + b')                                                (3)

        L(x,z) = -sum_{k=1}^d [x_k \log z_k + (1-x_k) \log( 1-z_k)]      (4)

    """

    def __init__(
        self,
        numpy_rng,
        theano_rng=None,
        input=None,
        n_visible=784,
        n_hidden=500,
        W=None,
        bhid=None,
        bvis=None
    ):

        self.n_visible = n_visible
        self.n_hidden = n_hidden

        # create a Theano random generator that gives symbolic random values
        if not theano_rng:
            theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))

        # note : W' was written as `W_prime` and b' as `b_prime`
        if not W:
            initial_W = numpy.asarray(
                numpy_rng.uniform(
                    low=-4 * numpy.sqrt(6. / (n_hidden + n_visible)),
                    high=4 * numpy.sqrt(6. / (n_hidden + n_visible)),
                    size=(n_visible, n_hidden)
                ),
                dtype=theano.config.floatX
            )
            W = theano.shared(value=initial_W, name='W', borrow=True)

        if not bvis:
            bvis = theano.shared(
                value=numpy.zeros(
                    n_visible,
                    dtype=theano.config.floatX
                ),
                borrow=True
            )

        if not bhid:
            bhid = theano.shared(
                value=numpy.zeros(
                    n_hidden,
                    dtype=theano.config.floatX
                ),
                name='b',
                borrow=True
            )

        self.W = W
        # b corresponds to the bias of the hidden
        self.b = bhid
        # b_prime corresponds to the bias of the visible
        self.b_prime = bvis

        # tied weights, therefore W_prime is W transpose
        self.W_prime = self.W.T

        self.theano_rng = theano_rng
        if input is None:
            self.x = T.dmatrix(name='input')
        else:
            self.x = input

        self.params = [self.W, self.b, self.b_prime]

    def get_corrupted_input(self, input, corruption_level):

        return self.theano_rng.binomial(size=input.shape, n=1,
                                        p=1 - corruption_level,
                                        dtype=theano.config.floatX) * input

    def get_hidden_values(self, input):
        """ Computes the values of the hidden layer """
        return T.nnet.sigmoid(T.dot(input, self.W) + self.b)

    def get_reconstructed_input(self, hidden):
        """Computes the reconstructed input given the values of the
        hidden layer

        """
        return T.nnet.sigmoid(T.dot(hidden, self.W_prime) + self.b_prime)


    def get_cost_updates(self, corruption_level, learning_rate):
        """ This function computes the cost and the updates for one training
        step of the dA """

        tilde_x = self.get_corrupted_input(self.x, corruption_level)
        y = self.get_hidden_values(tilde_x)
        z = self.get_reconstructed_input(y)
        # note : we sum over the size of a datapoint; if we are using
        #        minibatches, L will be a vector, with one entry per
        #        example in minibatch
        L = - T.sum(self.x * T.log(z) + (1 - self.x) * T.log(1 - z), axis=1)
        # note : L is now a vector, where each element is the
        #        cross-entropy cost of the reconstruction of the
        #        corresponding example of the minibatch. We need to
        #        compute the average of all these to get the cost of
        #        the minibatch
        cost = T.mean(L)

        # compute the gradients of the cost of the `dA` with respect
        # to its parameters
        gparams = T.grad(cost, self.params)
        # generate the list of updates
        updates = [
            (param, param - learning_rate * gparam)
            for param, gparam in zip(self.params, gparams)
        ]

        return (cost, updates)



def resize(img, **kwargs):
    # resize each img slice into 256*256 array

    mode = kwargs.pop("mode", 64)

    tl = img.shape[2]
    zl = img.shape[3]

    if mode == 64:
        temp = numpy.zeros((256, 256, tl, zl))
        temp[:, :232, :, :] = img[16:, :232, :, :zl]

        ret = numpy.zeros((64,64,tl,zl))
        for t in range(tl):
            for z in range(zl):
                ret[:,:,t,z] = scipy.misc.imresize(temp[:,:,t,z], (64, 64), interp = 'nearest')
        '''test resize'''
        tslice = 1
        zslice = 7

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.imshow(temp[:, :, tslice, zslice], cmap=plt.cm.gray)
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.imshow(ret[:, :, tslice, zslice], cmap=plt.cm.gray)

        plt.show()

    elif mode == 256:
        ret = numpy.zeros((256,256,tl,zl))
        ret[:,:232,:,:] = img[16:,:232,:,:zl]

    return ret


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


def crop(img, **kwargs):
    #TODO: crop 10 11*11 segment from each slice(:,:,2:9)

    mode = kwargs.pop("mode", 64)
    if mode == 64:
        disp_min = lim+10
        disp_max = 64-(lim+10)
    elif mode == 256:
        disp_min = 75
        disp_max = 175

    tl = img.shape[2]

    idx = 0
    patch = numpy.zeros((2400, lim, lim))

    for z in range(2, 10):
        for t in range(tl):
            for i in range(10):
                xdisp = random.randint(disp_min, disp_max)
                ydisp = random.randint(disp_min, disp_max)

                for x in range(lim):
                    for y in range(lim):
                        patch[idx,x,y] = img[x+xdisp,y+ydisp,t,z]
                idx += 1

    return patch



img_original = numpy.load('cinedata/cinedata_1.npy')
img2_original = numpy.load('cinedata/cinedata_2.npy')
img3_original = numpy.load('cinedata/cinedata_3.npy')

print(img_original.shape)

''' resized img '''
#img3 = resize(img2)
img_64 = resize(img_original, mode = 64)
img_256 = resize(img_original, mode = 256)

img2_64 = resize(img2_original, mode = 64)
img2_256 = resize(img2_original, mode = 256)

img3_64 = resize(img3_original, mode = 64)
img3_256 = resize(img3_original, mode = 256)

tslice = 1
zslice = 7

'''
fig = plt.figure()
ax1 = fig.add_subplot(1, 3, 1)
ax1.imshow(img_64[:,:,tslice,zslice], cmap = plt.cm.gray)
ax2 = fig.add_subplot(1, 3, 2)
ax2.imshow(img_64[:,:,tslice,zslice], cmap = plt.cm.gray)
ax3 = fig.add_subplot(1, 3, 3)
ax3.imshow(img_64[:,:,tslice,zslice], cmap = plt.cm.gray)

plt.show()
'''


'''
0 : crop and normalize
1 : normalize and crop
'''
mode = 1

'''change this if img size changed'''
img = img_64
img2 = img2_64
img3 = img3_64

''' output stored in patch_normalized '''
if mode == 0:
    '''crop and normalize'''
    patch = crop(img)
    patch_normalized = normalize(patch, flag = "patch")

elif mode == 1:
    '''normalize and crop'''
    img_normalized = normalize(img, flag = "img")
    patch_normalized = crop(img_normalized, mode = 64)
    img2_normalized = normalize(img2, flag = "img")
    patch2_normalized = crop(img2_normalized, mode = 64)
    img3_normalized = normalize(img3, flag = "img")
    patch3_normalized = crop(img3_normalized, mode = 64)

''' convert each 2-dimensional array into 1-dimensional array '''
patch_data_x = numpy.zeros((7200, lim*lim))
for i in range(2400):
    patch_data_x[i] = patch_normalized[i].flatten()
for i in range(2400, 4800):
    patch_data_x[i] = patch2_normalized[i-2400].flatten()
for i in range(4800, 7200):
    patch_data_x[i] = patch3_normalized[i-4800].flatten()

print(patch_data_x.shape[0], patch_data_x.shape[1])

#numpy.save("cine_patch", patch_data_x)

'''end of resize'''
print("end of resize")

learning_rate = 0.1
training_epochs = 5 # 15

'''from 0 to 1'''
corruptionLevel_ratio = 0.3


# dataset = 'mnist.pkl.gz'
batch_size = 1
output_folder = 'dA_cine'

patch_xdim = lim  # 11 x 11 image size
n_hide = 100

train_set_x = theano.shared(numpy.asarray(patch_data_x, dtype=theano.config.floatX), borrow=True)

# datasets = load_data(dataset)
#
# train_set_x, train_set_y = datasets[0]

# train_set_x_1 = train_set_x[1,:]
# train_set_x1 = train_set_x_1.eval()
# train_set_x1_img = numpy.zeros((28, 28))
# print(train_set_x1.shape)
# train_set_x1_img = train_set_x1.reshape((28,28))

# plt.figure()
# plt.imshow(train_set_x1_img, cmap=plt.cm.gray)
# plt.show()

# print(type(train_set_x_1))
# print(train_set_x_1.eval())

# print(train_set_x.shape.eval())
# print(train_set_y.shape.eval())



# sys.exit()


# compute number of minibatches for training, validation and testing
n_train_batches = train_set_x.get_value(borrow=True).shape[0] // batch_size
print(batch_size)
print(n_train_batches)




# allocate symbolic variables for the data
index = T.lscalar()    # index to a [mini]batch


# Declare Theano symbolic variable.
x = T.matrix('x')  # the data is presented as rasterized images


# print(index)








if not os.path.isdir(output_folder):
    os.makedirs(output_folder)
os.chdir(output_folder)



rng = numpy.random.RandomState(123)
theano_rng = RandomStreams(rng.randint(2 ** 30))

da = dA(numpy_rng=rng, theano_rng=theano_rng, input=x, n_visible=patch_xdim * patch_xdim, n_hidden= n_hide)
cost, updates = da.get_cost_updates(corruption_level = corruptionLevel_ratio, learning_rate=learning_rate)

print(type(cost))

train_da = theano.function( [index], cost, updates=updates, givens={ x: train_set_x[index * batch_size: (index + 1) * batch_size] })

start_time = timeit.default_timer()


# go through training epochs
for epoch in range(training_epochs):
    # go through training set
    c = []
    for batch_index in range(n_train_batches):
        c.append(train_da(batch_index))
    print('Training epoch %d, cost ' % epoch, numpy.mean(c))


end_time = timeit.default_timer()
training_time = (end_time - start_time)

print(('The no corruption code for file ' + os.path.split(__file__)[1] + ' ran for %.2fm' % ((training_time) / 60.)), file=sys.stderr)

image = Image.fromarray(tile_raster_images(X=da.W.get_value(borrow=True).T, img_shape=(patch_xdim, patch_xdim), tile_shape=(10, 16), tile_spacing=(2, 2)))

image.save('filters_cine1.png')
#numpy.save('filters', )
print(type(da.W.get_value(borrow=True).T))
print(da.W.get_value(borrow=True).T.shape)


Fl = numpy.zeros((lim,lim,100))
for i in range(100):
    Fl[:,:,i] = numpy.reshape(da.W.get_value(borrow=True).T[i,:], (lim, lim))

numpy.save("filter11by11by100", Fl)


'''
print(Fl[:,:,0])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.imshow(Fl[:,:,0], cmap = plt.cm.gray, interpolation='none')

plt.show()
'''
''' test resize
tslice = 1
zslice = 7

fig = plt.figure()
ax1 = fig.add_subplot(1, 3, 1)
ax1.imshow(img_ori[:,:,tslice,zslice], cmap = plt.cm.gray)
ax2 = fig.add_subplot(1, 3, 2)
ax2.imshow(img_256[:,:,tslice,zslice], cmap = plt.cm.gray)
ax3 = fig.add_subplot(1, 3, 3)
ax3.imshow(img_64[:,:,tslice,zslice], cmap = plt.cm.gray)

plt.show()
'''

os.chdir('../')





























