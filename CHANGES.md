Changes
=======

Version 0.4.1 (2015-06-02)
--------------------------

Fixed formatting issues in README.rst


Version 0.4 (2015-06-02)
------------------------

Width arguments now specify number of text columns rather than raster width - #30
New `min_bbox()` function to easily compute the minimum bbox from geometry iterators - #27
New `--colors` flag that prints a list of available colors and exits - #37
New `style_multiple()` function to easily render and apply colors to multiple layers in the API - #20
New `render_multiple()` function to easily render multiple layers in the API - #20
New `ascii2array()` and `array2ascii()` functions
Support for colors and multiple layers on the commandline and in the API - #14, #15
Zoom in on a specific area with bbox flag and param for `render()` - #14
New `stack()` function to overlay rendered layers - #14
New `paginate()` function to easily iterate over features for the CLI - #13
New `style()` function to apply colors to a rendering - #15
`render()` now has a default width - #12
`render()` is now smarter about handling GeoJSON geometry, features, or other iterables - #11
Removed `--no-all-touched`, `-at`, `-nat`, and `-i` in favor of just `--all-touched` and `--iterate` - #29
