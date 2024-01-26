import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.ndimage import convolve

n = 11
alpha = -1
beta = 1
gamma = 0.1
dt = 1e-1

n = 30
x_grid, y_grid = np.mgrid[-n // 2 + 1:n // 2 + 1, -n // 2 + 1:n // 2 + 1]

theta = np.random.rand(n, n) * 2 * np.pi
omega = np.zeros((n, n))
x = np.cos(theta)
y = np.sin(theta)

def B(x_grid, y_grid, a, b, c, d):
    B_x = a * x_grid + b * y_grid
    B_y = c * x_grid + d * y_grid

    B_x = B_x / np.sqrt(x_grid**2 + y_grid**2 + 1e-10)
    B_y = B_y / np.sqrt(x_grid**2 + y_grid**2 + 1e-10)
    return B_x, B_y

a, b, c, d = np.random.rand(4) * 2 - 1

print(f'B_x = ({a:.2f}x + {b:.2f}y) / sqrt(x^2 + y^2)')
print(f'B_y = ({c:.2f}x + {d:.2f}y) / sqrt(x^2 + y^2)')

B_x, B_y = B(x_grid, y_grid, a, b, c, d)
B_angle = np.arctan2(B_y, B_x)
B_mag = np.sqrt(B_x**2 + B_y**2)


fig, ax = plt.subplots()

def update(frame):
    global theta, omega, x, y

    for _ in range(15):
        x_up = np.roll(x, 1, axis=0)
        x_down = np.roll(x, -1, axis=0)
        x_left = np.roll(x, 1, axis=1)
        x_right = np.roll(x, -1, axis=1)

        y_up = np.roll(y, 1, axis=0)
        y_down = np.roll(y, -1, axis=0)
        y_left = np.roll(y, 1, axis=1)
        y_right = np.roll(y, -1, axis=1)

        x_neighbors = x_right + x_left + x_up + x_down
        y_neighbors = y_right + y_left + y_up + y_down

        theta_neighbors = np.arctan2(y_neighbors, x_neighbors)

        force_nieghbors = np.sin(theta_neighbors - theta)
        force_field = np.sin(B_angle - theta) * B_mag

        force = alpha * force_nieghbors + beta * force_field
        friction = gamma * omega

        # Verlet integration
        omega += dt * (force - friction)
        theta += dt * omega
        theta %= 2 * np.pi

        x = np.cos(theta)
        y = np.sin(theta)

    x_average = convolve(x, np.ones((5, 5)) / 9, mode='wrap')
    y_average = convolve(y, np.ones((5, 5)) / 9, mode='wrap')
    magnetization = x_average + y_average

    ax.clear()
    ax.quiver(x_grid, y_grid, x, y, magnetization, cmap='jet')

ani = animation.FuncAnimation(fig, update, frames=200, interval=5)

writer = animation.PillowWriter()
ani.save('images/spin_quiver.gif', writer=writer)
