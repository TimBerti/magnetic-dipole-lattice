import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.ndimage import convolve

n = 100
n_frames = 100
steps_per_frame = 10


def generate_lattice(n=n, temperature=1.0):
    """
    Generate a 2D lattice of magnets.

    Parameters
    ----------
    n : int
        The number of lattice points in each dimension.
    temperature : float
        The temperature of the lattice.
    """

    theta = np.random.rand(n, n) * 2 * np.pi
    omega = np.random.randn(n, n) * temperature

    return theta, omega

def compute_local_magnetization(theta, kernel_size=5):
    """
    Compute the local magnetization of a 2D lattice of magnets.

    Parameters
    ----------
    theta : array_like
        The angles of the magnets.
    kernel_size : int
        The size of the kernel to use for the local average.
    """

    kernel = np.ones((kernel_size, kernel_size)) / kernel_size**2
    x = np.cos(theta)
    y = np.sin(theta)
    local_average_x = convolve(x, kernel, mode='wrap')
    local_average_y = convolve(y, kernel, mode='wrap')

    magnetization_angle = np.arctan2(local_average_y, local_average_x)
    magnetization_magnitude = np.sqrt(local_average_x**2 + local_average_y**2)

    return magnetization_angle, magnetization_magnitude

def update_lattice(theta, omega, field=None, target_temp=1.0, alpha=1, beta=0, gamma=1, dt=0.1):
    """
    Update the state of the lattice using the Nose-Hoover thermostat.

    Parameters
    ----------
    theta : array_like
        The angles of the magnets.
    omega : array_like
        The angular velocities of the magnets.
    field : tuple of array_like, optional
        The external magnetic field.
    target_temp : float
        The target temperature of the thermostat.
    alpha : float
        The strength of the interaction between magnets.
    beta :  float
        The strength of the interaction with the external field.
    gamma : float
        The strength of the thermostat.
    dt : float
        The time step.
    """

    # Force from neighbours with periodic boundary conditions

    theta_up = np.roll(theta, 1, axis=0)
    theta_down = np.roll(theta, -1, axis=0)
    theta_left = np.roll(theta, 1, axis=1)
    theta_right = np.roll(theta, -1, axis=1)

    x_neighbours = np.cos(theta_up) + np.cos(theta_down) + np.cos(theta_left) + np.cos(theta_right)
    y_neighbours = np.sin(theta_up) + np.sin(theta_down) + np.sin(theta_left) + np.sin(theta_right)

    theta_neighbours = np.arctan2(y_neighbours, x_neighbours)
    force = alpha * np.sin(theta_neighbours - theta)

    # Force from external field

    if field is not None:
        field_x, field_y = field
        field_angle = np.arctan2(field_y, field_x)
        field_mag = np.sqrt(field_x**2 + field_y**2)
        force += beta * np.sin(field_angle - theta) * field_mag

    # Nose thermostat

    avg_temp = np.mean(omega**2)
    thermostat = gamma * (target_temp - avg_temp) * omega

    # Verlet integration

    omega += (force + thermostat) * dt
    theta += omega * dt

    # Angle back to [0, 2pi]

    theta = np.mod(theta, 2 * np.pi)

    return theta, omega

def update(ax, frame):
    global theta, omega
    for _ in range(steps_per_frame):
        theta, omega = update_lattice(theta, omega, target_temp=target_temperatures[frame])
    magnetization_angle, magnetization_mag = compute_local_magnetization(theta)
    ax.clear()
    ax.quiver(np.cos(theta)*magnetization_mag, np.sin(theta)*magnetization_mag, magnetization_angle, cmap='hsv')


if __name__ == '__main__':

    theta, omega = generate_lattice(n=n)
    target_temperatures = 2 * np.concatenate((
        np.linspace(1, 0, n_frames//5), 
        np.zeros(n_frames//5), 
        np.linspace(0, .5, n_frames//10), 
        .5*np.ones(n_frames//5),
        np.linspace(.5, 0, n_frames//10),
        np.zeros(n_frames//5),
        ))

    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, lambda frame: update(ax, frame), frames=n_frames, interval=50)

    writer = animation.PillowWriter()
    ani.save(f'images/dipole_quiver{n}.gif', writer=writer)
