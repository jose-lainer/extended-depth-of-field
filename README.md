# Extended Depth of Field

Combine aligned photographs focused at different distances into a single image.
The notebook measures focus with a Laplacian after a 5×5 Gaussian blur, then
copies each pixel from the input with the strongest absolute response. Equal
responses select the first input image.

## Run

Use Python 3.10 or later. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab Extended_Depth_of_Field.ipynb
```

Select the virtual environment's Python kernel and run all cells in order.
The four included JPEGs are the default inputs. To use other photos, edit
`image_paths` in the notebook. Images must be aligned, equally sized, and readable
by OpenCV. The composite is saved as `infocus_img.jpg` in the working directory.

OpenCV loads images in BGR channel order. For an RGB Matplotlib preview, use
`cv.cvtColor(focused_image, cv.COLOR_BGR2RGB)` before plotting. Image registration,
exposure correction, and boundary blending are outside the algorithm's scope.

## Files

- `Extended_Depth_of_Field.ipynb`: load, measure, compose, and preview.
- `img_01.jpg`–`img_04.jpg`: example focus stack.
- `requirements.txt`: runtime and notebook dependencies.

## License

Code and documentation are available under the [MIT license](LICENSE).
The bundled photographs are retained from the original repository; their provenance
and redistribution terms are not documented, so this license does not assert rights
over those photographs. Dependencies retain their respective licenses.
