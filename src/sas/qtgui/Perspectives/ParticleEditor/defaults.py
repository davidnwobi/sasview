import numpy as np


def sld(r, theta, phi):
    inside = r + 20*np.sin(6*theta)*np.cos(3*phi) < 50
    out = np.zeros_like(r)
    out[inside] = 1.0
    return out


default_text = '''""" 

Here's a new perspective. It calculates the scattering based on real-space description of a particle.

Basically, define your SLD as a function of either cartesian or polar coordinates and click scatter

  def sld(x,y,z)
  def sld(r,theta,phi)

The display on the right shows your particle, both as a total projected density (top) and as a slice (bottom).

This is a minimal working system. Currently magnetism doesn't work, neither do extra parameters for your functions,
nor structure factors, nor fitting, nor 2D plots. 

Here's a simple example: """

def sld(x,y,z):
    """ A cube with 100Ang side length"""

    return rect(0.02*x)*rect(0.02*y)*rect(0.02*z)

'''

""" Press shift-return to build and update views
    Click scatter to show the scattering profile"""