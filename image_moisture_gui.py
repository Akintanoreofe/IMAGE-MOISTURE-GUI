"""Collect feed sample weights and images in a Parquet dataset."""

import os
import shutil
from datetime import datetime
from tkinter import Button, Entry, Label, StringVar, Tk, filedialog, messagebox

import pandas as pd


# Dataset locations
BASE_DIR = "dataset"
JPEG_DIR = os.path.join(BASE_DIR, "images", "jpeg")
PARQUET_PATH = os.path.join(BASE_DIR, "feed_data.parquet")

os.makedirs(JPEG_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)


def compute_values(pan, wet_total, dry_total):
    """Calculate net weights, moisture, dry matter, and moisture interval.

    Parameters
    ----------
    pan : float
        Weight of the empty pan, in grams.
    wet_total : float
        Weight of the pan and wet sample, in grams.
    dry_total : float
        Weight of the pan and dry sample, in grams.

    Returns
    -------
    tuple[float, float, float, float, str]
        Net wet weight, net dry weight, moisture content percentage, dry
        matter percentage, and the corresponding moisture interval.

    Raises
    ------
    ValueError
        If the net wet weight is not greater than zero.
    """
    net_wet = wet_total - pan
    net_dry = dry_total - pan

    if net_wet <= 0:
        raise ValueError("Net wet weight must be greater than 0.")

    mc = (net_wet - net_dry) / net_wet * 100
    dm = 100 - mc

    edges = [0, 20, 40, 60, 80, 100]
    interval = "Unknown"
    for i in range(len(edges) - 1):
        if mc >= edges[i] and mc < edges[i + 1]:
            interval = f"{edges[i]}–{edges[i + 1]}%"
            break

    return net_wet, net_dry, mc, dm, interval


def append_to_parquet(row):
    """Append a sample record to the Parquet dataset.

    Parameters
    ----------
    row : dict
        Sample metadata to append as one dataset row.
    """
    if os.path.exists(PARQUET_PATH):
        df_old = pd.read_parquet(PARQUET_PATH)
        df_new = pd.concat([df_old, pd.DataFrame([row])], ignore_index=True)
    else:
        df_new = pd.DataFrame([row])

    df_new.to_parquet(PARQUET_PATH)


class FeedGUI:
    """Tkinter interface for collecting sample measurements and images."""

    def __init__(self, master):
        """Initialize the application window and its input/output fields.

        Parameters
        ----------
        master : tkinter.Tk
            Root window for the application.
        """
        self.master = master
        master.title("Feed Moisture Content Collector (Parquet Version)")
        master.geometry("700x550")

        self.sample_number = StringVar()
        self.pan = StringVar()
        self.wet_total = StringVar()
        self.dry_total = StringVar()
        self.jpeg_path = StringVar()

        self.net_wet_var = StringVar(value="—")
        self.net_dry_var = StringVar(value="—")
        self.mc_var = StringVar(value="—")
        self.dm_var = StringVar(value="—")
        self.interval_var = StringVar(value="—")
        self.last_saved_var = StringVar(value="None")

        # Sample input fields
        row = 0
        Label(master, text="Sample Number (e.g., 01):").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        Entry(master, textvariable=self.sample_number, width=15).grid(
            row=row, column=1
        )

        row += 1
        Label(master, text="Pan Weight (g):").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        Entry(master, textvariable=self.pan, width=15).grid(row=row, column=1)

        row += 1
        Label(master, text="Wet Total (g):").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        Entry(master, textvariable=self.wet_total, width=15).grid(
            row=row, column=1
        )

        row += 1
        Label(master, text="Dry Total (g):").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        Entry(master, textvariable=self.dry_total, width=15).grid(
            row=row, column=1
        )

        row += 1
        Label(master, text="JPEG Image:").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        Entry(master, textvariable=self.jpeg_path, width=40).grid(
            row=row, column=1
        )
        Button(master, text="Browse", command=self.browse_jpeg).grid(
            row=row, column=2
        )

        # Calculated sample results
        row += 1
        Label(master, text="Net Wet (g):").grid(row=row, column=0, sticky="e")
        Label(master, textvariable=self.net_wet_var).grid(
            row=row, column=1, sticky="w"
        )

        row += 1
        Label(master, text="Net Dry (g):").grid(row=row, column=0, sticky="e")
        Label(master, textvariable=self.net_dry_var).grid(
            row=row, column=1, sticky="w"
        )

        row += 1
        Label(master, text="Moisture Content (%):").grid(
            row=row, column=0, sticky="e"
        )
        Label(master, textvariable=self.mc_var).grid(
            row=row, column=1, sticky="w"
        )

        row += 1
        Label(master, text="Dry Matter (%):").grid(
            row=row, column=0, sticky="e"
        )
        Label(master, textvariable=self.dm_var).grid(
            row=row, column=1, sticky="w"
        )

        row += 1
        Label(master, text="Moisture Interval:").grid(
            row=row, column=0, sticky="e"
        )
        Label(master, textvariable=self.interval_var).grid(
            row=row, column=1, sticky="w"
        )

        # Sample actions
        row += 1
        Button(
            master, text="Calculate", command=self.calculate_values, width=15
        ).grid(row=row, column=0, pady=20)
        Button(
            master, text="Save Sample", command=self.save_sample, width=15
        ).grid(row=row, column=1)

        row += 2
        Label(master, text="Last Sample Saved:").grid(
            row=row, column=0, sticky="e"
        )
        Label(master, textvariable=self.last_saved_var).grid(
            row=row, column=1, sticky="w"
        )

    def browse_jpeg(self):
        """Open a file chooser and set the selected JPEG image path."""
        path = filedialog.askopenfilename(
            filetypes=[("JPEG Files", "*.jpg;*.jpeg")]
        )
        if path:
            self.jpeg_path.set(path)

    def calculate_values(self):
        """Calculate and display the sample's derived moisture values."""
        try:
            pan = float(self.pan.get())
            wet = float(self.wet_total.get())
            dry = float(self.dry_total.get())

            net_wet, net_dry, mc, dm, interval = compute_values(pan, wet, dry)

            self.net_wet_var.set(f"{net_wet:.3f}")
            self.net_dry_var.set(f"{net_dry:.3f}")
            self.mc_var.set(f"{mc:.2f}")
            self.dm_var.set(f"{dm:.2f}")
            self.interval_var.set(interval)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_sample(self):
        """Save the selected image and its measurements to the dataset."""
        try:
            num = self.sample_number.get().strip()
            if not num:
                raise ValueError("Sample number required.")

            sid = f"ALF_{num.zfill(2)}"

            pan = float(self.pan.get())
            wet = float(self.wet_total.get())
            dry = float(self.dry_total.get())

            jpeg_src = self.jpeg_path.get().strip()
            if not os.path.exists(jpeg_src):
                raise ValueError("Valid JPEG required.")

            net_wet, net_dry, mc, dm, interval = compute_values(pan, wet, dry)

            # Keep each saved image alongside the dataset metadata.
            jpeg_dst = os.path.join(JPEG_DIR, f"{sid}.jpg")
            shutil.copy2(jpeg_src, jpeg_dst)

            row = {
                "sample_id": sid,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "jpeg_file": jpeg_dst,
                "pan_weight_g": pan,
                "wet_weight_total_g": wet,
                "dry_weight_total_g": dry,
                "net_wet_weight_g": net_wet,
                "net_dry_weight_g": net_dry,
                "moisture_content_percent": mc,
                "dry_matter_percent": dm,
                "moisture_interval": interval,
            }

            append_to_parquet(row)
            self.last_saved_var.set(sid)

            # Clear the form after a successful save.
            self.sample_number.set("")
            self.pan.set("")
            self.wet_total.set("")
            self.dry_total.set("")
            self.jpeg_path.set("")

            self.net_wet_var.set("—")
            self.net_dry_var.set("—")
            self.mc_var.set("—")
            self.dm_var.set("—")
            self.interval_var.set("—")

            messagebox.showinfo("Success", f"Sample {sid} saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = Tk()
    app = FeedGUI(root)
    root.mainloop()
