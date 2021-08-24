import matplotlib.pyplot as plt

def plotGazeEvents(fix, x, y, t):

    x_1 = []
    y_1 = []

    x_2 = x
    y_2 = y

    for f in fix:
        x_1.append(f[3])
        y_1.append(f[4])

    ax = plt.gca()
    #plt.subplot(2, 1, 1)
    plt.plot(x_2, y_2, 'ko-')
    plt.ylim(1080, 0)
    plt.xlim(0, 1920)

    #plt.subplot(2, 1, 2)
    plt.plot(x_1, y_1, 'r.-')
    plt.ylim(1080, 0)
    plt.xlim(0, 1920)

    #.set_yticks([0.3, 0.55, 0.7], minor=True)

    # ax.set_yticks([360, 720], minor=True)
    ax.yaxis.grid(True, which='minor')
    # ax.set_xticks([480,960,1440], minor=True)
    ax.xaxis.grid(True, which='minor')

    plt.title('Fixations and Scanpath')
    plt.show()