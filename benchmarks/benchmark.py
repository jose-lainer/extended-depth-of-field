"""Compare the preserved baseline with functions loaded from the notebook."""
import argparse
import json
import platform
from pathlib import Path
import statistics
import time

import cv2 as cv
import numpy as np

from original import focus_stack as original_focus_stack

ROOT = Path(__file__).resolve().parents[1]


def load_notebook_functions():
    """Load definitions directly, so the benchmark exercises notebook code."""
    notebook = json.loads((ROOT / 'Extended_Depth_of_Field.ipynb').read_text())
    namespace = {'cv': cv, 'np': np}
    for cell in notebook['cells']:
        source = ''.join(cell['source'])
        if cell['cell_type'] == 'code' and source.startswith('def compute_focus_maps'):
            exec(compile(source, str(ROOT / 'Extended_Depth_of_Field.ipynb'), 'exec'), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 3:
        parser.error('Use at least three repeats.')
    cv.setNumThreads(1)
    namespace = load_notebook_functions()
    optimized = namespace['focus_stack']
    images = [cv.imread(str(ROOT / f'img_{index:02d}.jpg')) for index in range(1, 5)]
    if any(image is None for image in images):
        raise FileNotFoundError('Missing bundled input image.')
    rng = np.random.default_rng(42)
    cases = {
        'bundled_full': images,
        'bundled_half': [cv.resize(image, None, fx=0.5, fy=0.5) for image in images],
        'random': [rng.integers(0, 256, (31, 47, 3), dtype=np.uint8) for _ in range(4)],
        'ties': [np.full((17, 19, 3), value, np.uint8) for value in (20, 70, 120, 170)],
        'single': [images[0][:31, :47]],
    }
    results = {}
    for name, inputs in cases.items():
        # Untimed warmups also establish equivalence before timing.
        expected = original_focus_stack(inputs)
        actual = optimized(inputs)
        np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(cv.imencode('.jpg', actual)[1], cv.imencode('.jpg', expected)[1])
        if name == 'ties':
            np.testing.assert_array_equal(actual, inputs[0])
        samples = {'original': [], 'refactored': []}
        for repeat in range(args.repeats):
            ordered = [('original', original_focus_stack), ('refactored', optimized)]
            if repeat % 2:
                ordered.reverse()
            for label, function in ordered:
                start = time.perf_counter()
                function(inputs)
                samples[label].append(time.perf_counter() - start)
        medians = {label: statistics.median(values) for label, values in samples.items()}
        speedup = medians['original'] / medians['refactored']
        results[name] = {'shape': list(inputs[0].shape), 'samples_seconds': samples,
                         'median_seconds': medians, 'speedup': speedup,
                         'maximum_absolute_pixel_error': 0, 'jpeg_bytes_equal': True}
        print(f'{name}: {medians["original"]:.6f}s -> {medians["refactored"]:.6f}s ({speedup:.1f}x)', flush=True)
    # Mixed positive/negative equal magnitudes explicitly exercise the tie rule.
    tiny = [np.full((2, 2, 3), value, np.uint8) for value in (10, 90)]
    maps = np.array([[[1, -3], [0, 2]], [[-1, 3], [0, -4]]], dtype=np.float32)
    selected = namespace['select_focused_pixels'](tiny, maps)
    np.testing.assert_array_equal(selected, np.array([[tiny[0][0, 0], tiny[0][0, 1]],
                                                     [tiny[0][1, 0], tiny[1][1, 1]]]))
    accepted = all(results[name]['speedup'] >= 1.25 for name in ('bundled_full', 'bundled_half'))
    report = {'baseline_commit': '7cbc4c9', 'platform': platform.platform(),
              'python': platform.python_version(), 'numpy': np.__version__, 'opencv': cv.__version__,
              'opencv_threads_requested': 1,
              'opencv_threads': cv.getNumThreads(), 'repeats': args.repeats,
              'scope': 'focus computation only; image reading, writing and plotting excluded',
              'acceptance': '>=20% median runtime reduction on both bundled resolutions; exact pixels and JPEG bytes on all cases',
              'accepted': accepted, 'cases': results}
    (ROOT / 'benchmarks/results.json').write_text(json.dumps(report, indent=2) + '\n')
    if not accepted:
        raise SystemExit('Performance threshold not met.')


if __name__ == '__main__':
    main()
