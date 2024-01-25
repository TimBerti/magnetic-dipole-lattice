import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

n = 11
alpha = -1
beta = 1
gamma = 0.1
dt = 1e-1

n = 11
x_grid, y_grid = np.mgrid[-n // 2 + 1:n // 2 + 1, -n // 2 + 1:n // 2 + 1]

theta = np.random.rand(n, n) * 2 * np.pi
omega = np.zeros((n, n))
x = np.cos(theta)
y = np.sin(theta)

B_x = x_grid / np.sqrt(x_grid**2 + y_grid**2 + 1e-5)
B_y = y_grid / np.sqrt(x_grid**2 + y_grid**2 + 1e-5)
B_angle = np.arctan2(B_y, B_x)
B_mag = np.sqrt(B_x**2 + B_y**2)


fig, ax = plt.subplots()

def update(frame):
    global theta, omega, x, y

    for _ in range(15):
        x_right = np.concatenate((x[1:], np.zeros((1, n))), axis=0)
        x_left = np.concatenate((np.zeros((1, n)), x[:-1]), axis=0)
        x_up = np.concatenate((np.zeros((n, 1)), x[:, :-1]), axis=1)
        x_down = np.concatenate((x[:, 1:], np.zeros((n, 1))), axis=1)

        y_right = np.concatenate((y[1:], np.zeros((1, n))), axis=0)
        y_left = np.concatenate((np.zeros((1, n)), y[:-1]), axis=0)
        y_up = np.concatenate((np.zeros((n, 1)), y[:, :-1]), axis=1)
        y_down = np.concatenate((y[:, 1:], np.zeros((n, 1))), axis=1)

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

    ax.clear()
    ax.quiver(x_grid, y_grid, x, y);

ani = animation.FuncAnimation(fig, update, frames=100, interval=5)

writer = animation.PillowWriter()
ani.save('images/spin_quiver.gif', writer=writer)
