import numpy as np
import math
import matplotlib.pyplot as plt
import logging
from sas_gen import *

# main test file for fourier transform code - requires mesh to have all cells identical in type

def get_normal_vec(geometry):
    """return array of normal vectors of elements"""
    v1 = geometry[:, :, 1] - geometry[:, :, 0]
    v2 = geometry[:, :, 2] - geometry[:, :, 0]
    normals = np.cross(v1, v2)
    temp = np.linalg.norm(normals, axis=-1)
    normals = normals / np.linalg.norm(normals, axis=-1)[..., None]
    return normals


def sub_volume_transform(geometry, normals, rn_norm, qx, qy):
    """carries out fourier transform
    qx, qy are floats

    returns an array of fourier transforms for each of the subvolumes provided

    algorithm based off: An implementation of an efficient direct Fourier transform of polygonal areas and
                        volumes
                        Brian B. Maranville
                        https://arxiv.org/abs/2104.08309
    """
    # small value used in case where a fraction should limit to a finite answer with 0 on top and bottom
    # used in 2nd/3rd terms in sum over vertices
    eps = 1e-6

    # create the Q vector
    Q = np.array([qx+eps, qy+eps, 0+eps])
    # create the Q normal vector as the dot product of Q with the normal vector * the normal vector:
    # separately store the component of the Qn vector for later use
    # np.dot: (subvolumes x faces x normal_vector_coords) * (Q_coords) -> (subvolumes x faces)
    Qn_comp = np.dot(normals, Q)
    # Qn is the vector PARALLEL to the surface normal Q// in the referenced paper eq. (14)
    # np (*) (subvolumes x faces x 1) * (subvolumes x faces x normal_vector_coords) -> (subvolumes x faces x Qn_coords)
    Qn = Qn_comp[..., None] * normals
    # extract the parallel component of the Q vector
    # (1 x 1 x Q_coords) - (subvolumes x faces x Qn_coords)
    Qp = Q[None, None, :] - Qn
    # calculate the face-dependent prefactor for the sum over vertices (subvolumes x faces) 
    # TODO: divide by zero error - can nan and inf handle this?
    prefactor = (1j * Qn_comp * np.exp(1j * Qn_comp * rn_norm)) / np.sum(Q * Q)
    # calculate the sum over vertices term
    # TODO: divide by zero error - can nan and inf handle this?
    # the sub sum over the vertices in eq (14) (subvolumes x faces)
    sub_sum = np.zeros_like(prefactor, dtype="complex")
    for i in range(geometry.shape[2]-1):
        # calculate the separation vector (subvolumes x faces x vector_coords)
        v = geometry[:,:,i+1] - geometry[:,:,i]
        # the terms in the expr (subvolumes x faces)
        # WARNING: this uses the opposite sign convention as the article's code but agrees with the sign convention of the
        # main text - it takes line segment normals as pointing OUTWARDS from the surface - giving the 'standard' fourier transform
        # e.g. fourier transform of a box gives a positive sinc function
        term = (np.sum(Qp * np.cross(v, normals), axis=-1)) / np.sum(Qp * Qp, axis=-1)
        term = term * (np.exp(1j * np.sum(Qp * geometry[:,:,i+1], axis=-1)) - np.exp(1j * np.sum(Qp * geometry[:,:,i], axis=-1)))
        term = term / np.sum(Qp*v, axis=-1)
        sub_sum += term
    # sum over all the faces in each subvolume to return an array of transforms of sub_volumes
    return np.sum(prefactor*sub_sum, axis=-1)


reader = VTKReader()
data = reader.read("C:\\Users\\Robert\\Documents\\STFC\\VTK_testdata\\originals\\basic_cube_test.vtk")
if not data.are_elements_identical:
    logging.error("currently require all cells to be of the same type")
    quit()
pos_x = data.pos_x
pos_y = data.pos_y
pos_z = data.pos_z
elements = data.elements
# create the geometry as an array (subvolumes x faces x vertices x coordinates)
geometry = np.column_stack((pos_x, pos_y, pos_z))[np.concatenate((elements, elements[:,:,:1]), axis=2)]
# create normal vectors (subvolumes x faces x normal_vector_coords)
normals = get_normal_vec(geometry)
# extract the normal component of the displacement of the plane using the first point (subvolumes x faces)
rn_norm = np.sum(geometry[:,:,0] * normals, axis=-1)

qx = np.linspace(-10, 10, 40)
qy = np.linspace(-10, 10, 40)
qxs, qys = np.meshgrid(qx, qy)

output = np.zeros_like(qxs, dtype="complex")
errors = np.zeros_like(qxs, dtype=complex)
for i in range(len(qx)):
    for j in range(len(qy)):
        output[j, i] = sub_volume_transform(geometry, normals, rn_norm, qx[i], qy[j])[0]
        correct_value = 8*math.sin(qx[i])*math.sin(qy[i])/(qx[i]*qy[i])
        errors[j,i] = (math.real(output[j,i]) - correct_value)/correct_value
        #print(i, j)

mean_error = np.mean(errors)
print(mean_error*100 , "%")

import matplotlib.pyplot as plt
from matplotlib import colors, cm

extent = (qx.min(), qx.max(), qy.min(), qy.max())
fig1 = plt.figure()
plt.imshow(abs(output), extent=extent, aspect=1, cmap=cm.get_cmap("jet"))
plt.title('$Abs(FT)$')
plt.xlabel('$Q_x$', size='large')
plt.ylabel('$Q_y$', size='large')
plt.axis
plt.colorbar()
fig2 = plt.figure()
plt.imshow(np.real(output), extent=extent, aspect=1, cmap=cm.get_cmap("jet"))
plt.title('Real FT')
plt.xlabel('$Q_x$', size='large')
plt.ylabel('$Q_y$', size='large')
plt.colorbar()
plt.show()


#print(sub_volume_transform(pos_x, pos_y, pos_z, elements, 0.1, 0))
#plt.plot(qx, np.abs(output))
#plt.yscale("log")
#plt.show()