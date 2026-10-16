"""Original computation from repository commit 7cbc4c9 (plots and I/O excluded)."""
import cv2 as cv
import numpy as np


def focus_stack(images):
    gaussian_images = []
    for image in images:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        gaussian_images.append(cv.GaussianBlur(gray, (5, 5), 0))
    edges_images = [cv.Laplacian(image, 5) for image in gaussian_images]
    laps = np.asarray(edges_images)
    result = np.zeros(shape=images[0].shape, dtype=images[0].dtype)
    for y in range(images[0].shape[0]):
        for x in range(images[0].shape[1]):
            responses = abs(laps[:, y, x])
            index = np.where(responses == max(responses))[0][0]
            result[y, x] = images[index][y, x]
    return result
