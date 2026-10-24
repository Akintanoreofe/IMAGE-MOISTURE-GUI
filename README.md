# IMAGE-MOISTURE-GUI

A desktop application for recording feed sample weights, calculating moisture
content, and saving each sample's JPEG image and metadata to a Parquet dataset.

## Requirements

- Python 3
- pandas
- A Parquet engine supported by pandas, such as `pyarrow`
- Tkinter (included with many Python installations)

Install the Python packages with:

```bash
python -m pip install pandas pyarrow
```

## Run the application

```bash
python image_moisture_gui.py
```

Enter a sample number, pan weight, wet total, and dry total. Select the sample's
JPEG image, then choose **Calculate** to preview the derived measurements or
**Save Sample** to store the image and record. The application creates the
`dataset/` folder on startup. Each image is saved as
`dataset/images/jpeg/ALF_<sample number>.jpg`, and the records are appended to
`dataset/feed_data.parquet`.

## Dataset layout

After saving samples, the output folder looks like this:

```text
dataset/
├── feed_data.parquet
└── images/
    └── jpeg/
        ├── ALF_01.jpg
        └── ALF_02.jpg
```

The Parquet file contains one row per image. A CSV representation of those
columns would look like this:

```csv
sample_id,timestamp,jpeg_file,pan_weight_g,wet_weight_total_g,dry_weight_total_g,net_wet_weight_g,net_dry_weight_g,moisture_content_percent,dry_matter_percent,moisture_interval
ALF_01,2026-10-24 12:30:00,dataset/images/jpeg/ALF_01.jpg,5.0,25.0,17.0,20.0,12.0,40.0,60.0,40–60%
ALF_02,2026-10-24 12:35:00,dataset/images/jpeg/ALF_02.jpg,5.0,30.0,20.0,25.0,15.0,40.0,60.0,40–60%
```

For an input image folder, use JPEG files and name each file with its matching
sample ID:

```text
images/
└── jpeg/
    ├── ALF_01.jpg
    └── ALF_02.jpg
```

The application copies the selected source image into the generated dataset
folder when the corresponding sample is saved. It writes Parquet directly; the
CSV above illustrates the same metadata fields and is not an additional output
file.
