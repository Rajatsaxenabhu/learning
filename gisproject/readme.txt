uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-reranker-base', local_dir='./models/bge-reranker-base')"


| #  | Tool name                     | Brief usage                                                                             |
| -- | ----------------------------- | --------------------------------------------------------------------------------------- |
| 1  | `search_satellite_images`     | Search satellite images by collection, AOI, date range, and cloud percentage.           |
| 2  | `get_image_metadata`          | Get metadata such as acquisition date, cloud cover, CRS, bounds, and image ID.          |
| 3  | `get_image_bands`             | Get available bands and their names/wavelength information.                             |
| 4  | `get_collection_info`         | Get information about an Earth Engine image collection and its available properties.    |
| 5  | `filter_image_collection`     | Filter an image collection by date, geometry, cloud cover, or metadata.                 |
| 6  | `create_composite`            | Create median, mean, mosaic, minimum, or maximum composites from imagery.               |
| 7  | `cloud_mask`                  | Remove cloud/cloud-shadow pixels from supported satellite imagery.                      |
| 8  | `clip_image`                  | Clip an image to a given bounding box or geometry/AOI.                                  |
| 9  | `calculate_spectral_index`    | Calculate indices such as NDVI, NDWI, NDBI, EVI, SAVI, NDMI, and NBR.                   |
| 10 | `calculate_image_statistics`  | Calculate min, max, mean, median, standard deviation, and percentiles for an image/AOI. |
| 11 | `calculate_zonal_statistics`  | Calculate raster statistics separately for each polygon/zone.                           |
| 12 | `compare_images`              | Compare two images using difference, ratio, or normalized-difference methods.           |
| 13 | `calculate_change_statistics` | Quantify the amount and magnitude of change between two images.                         |
| 14 | `classify_image`              | Perform supervised image classification using algorithms such as Random Forest or SVM.  |
| 15 | `calculate_histogram`         | Generate a pixel-value histogram for an image or selected region.                       |
| 16 | `get_pixel_value`             | Get pixel/band values at a specified coordinate.                                        |
| 17 | `reduce_region`               | Reduce raster values over a geometry using reducers such as mean, sum, min, or max.     |
| 18 | `reduce_regions`              | Perform raster reduction for multiple geometries/features.                              |
| 19 | `create_map_layer`            | Convert a GEE image into visualization/tile information for OpenLayers.                 |
| 20 | `export_image`                | Export a processed GEE image as GeoTIFF or another supported format.                    |
| 21 | `get_export_status`           | Check the status of an Earth Engine export task.                                        |
| 22 | `cancel_export`               | Cancel a running Earth Engine export task.                                              |
