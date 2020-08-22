import numpy as np
from typing import List
import matplotlib.pyplot as plt


class Satellite(object):
    ''' This class contains every function and parameter that defines
        a planet and its movement around the sun.'''

    def __init__(self, SMA: float, INC: float, ECC: float, LAN: float, AOP: float, MA: float):
        self.SMA = SMA  # semi major axis
        self.INC = np.radians(INC)  # inclination
        self.ECC = ECC  # eccentricity
        self.LAN = np.radians(LAN)  # Longitude of Ascending node
        self.AOP = np.radians(AOP)  # argument of periapsis
        self.MA = np.radians(MA)    # mean anomaly
        # orbital period
        self.T = np.sqrt((4 * np.pi ** 2) /
                         (G * m_sun) * self.SMA ** 3)
        self.w = 2 * np.pi / self.T  # revolution speed

    def completeOrbitalElem2Vector(self, t: float) -> List[float]:
        ''' Computes the position and velocity of the planet on the x,y,z axis
            from the orbital parameters, at the time t.'''
        self.n = np.sqrt(G) / np.sqrt(self.SMA ** 3)
        self.M = self.MA + self.n * (t)  # We start at t0 = 0 = J2000 so no correction
        self.E = self.newton(self.keplerEquation, self.M)
        self.bigX = self.SMA * (np.cos(self.E) - self.ECC)
        self.bigY = self.SMA * np.sqrt(1 - self.ECC ** 2) * np.sin(self.E)
        self.bigXdot = - self.n * self.SMA ** 2 / \
            (self.SMA * (1 - self.ECC * np.cos(self.E))) * np.sin(self.E)
        self.bigYdot = self.n * self.SMA ** 2 / \
            (self.SMA * (1 - self.ECC * np.cos(self.E))) * np.sqrt(1 - self.ECC ** 2) * np.cos(self.E)
        self.position = np.dot(np.dot(np.dot(self.rotation3(-self.LAN),
                                             self.rotation1(-self.INC)),
                                      self.rotation3(-self.AOP)),
                               np.array([[self.bigX], [self.bigY], [0]]))
        self.velocity = np.dot(np.dot(np.dot(self.rotation3(-self.LAN),
                                             self.rotation1(-self.INC)),
                                      self.rotation3(-self.AOP)),
                               np.array([[self.bigXdot], [self.bigYdot], [0]]))
        return [self.position[0, 0], self.position[1, 0], self.position[2, 0],
                self.velocity[0, 0], self.velocity[1, 0], self.velocity[2, 0]]

    def orbitalparam2vectorList(self, timevector):
        ''' Creates a list with the xyz position of the planet at each time '''
        self.posList = [self.completeOrbitalElem2Vector(t) for t in timevector]
        return np.array(self.posList)

    def rotation1(self, theta):
        ''' rotation matrix 1'''
        return np.array([[1, 0, 0],
                         [0, np.cos(theta), np.sin(theta)],
                         [0, -np.sin(theta), np.cos(theta)]])

    def rotation3(self, theta):
        ''' rotation matrix 2'''
        return np.array([[np.cos(theta), np.sin(theta), 0],
                         [-np.sin(theta), np.cos(theta), 0],
                         [0, 0, 1]])

    def newton(self, f, E0, h=1e-4):
        ''' Nexton's method to solve Kepler's equation M = E - ECC * sin(E)'''
        E = E0
        for _ in range(5):
            diff = (f(E + h) - f(E)) / h
            E -= f(E) / diff
        return E

    def keplerEquation(self, E):
        ''' Kepler's equation'''
        return E - self.ECC * np.sin(E) - self.M


m_sun = 1  # mass of the Sun
G = 0.000295824  # gravitation constant expressed in our own system of units
k = np.sqrt(G)
mu = G * m_sun

if __name__ == "__main__":

    m_sun = 1  # mass of the Sun
    G = 0.000295824  # gravitation constant expressed in our own system of units
    k = np.sqrt(G)
    mu = G * m_sun

    o1 = Satellite(1, 0.00005, 0.01671022, 348.73936, 102.94719, -351.2222)
    time = np.linspace(0, 100000, 100000)
    pos = o1.orbitalparam2vectorList(time)
    plt.plot(pos[:, 0], pos[:, 1])
    plt.show()
