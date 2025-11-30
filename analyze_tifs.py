import os
import numpy as np
import matplotlib.pyplot as plt
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    import tifffile

def analyze_tif(filepath):
    print(f"\n--- Analyzing: {os.path.basename(filepath)} ---")
    
    try:
        if HAS_RASTERIO:
            with rasterio.open(filepath) as src:
                data = src.read(1) # Read first band
                nodata = src.nodata
                profile = src.profile
                print(f"Driver: {src.driver}")
                print(f"Size: {src.width}x{src.height}")
                print(f"CRS: {src.crs}")
                print(f"NoData Value: {nodata}")
                
                # Mask nodata
                if nodata is not None:
                    data = np.ma.masked_equal(data, nodata)
                else:
                    # Assume -9999 or similar if not defined, or just use valid data
                    pass
        else:
            print("Rasterio not found, using tifffile...")
            data = tifffile.imread(filepath)
            print(f"Shape: {data.shape}")
            print(f"Dtype: {data.dtype}")
            
        # Statistics
        valid_data = data.compressed() if np.ma.is_masked(data) else data.flatten()
        # Remove NaNs if any (for float data)
        valid_data = valid_data[~np.isnan(valid_data)]
        
        if len(valid_data) == 0:
            print("WARNING: File contains NO valid data (all masked or NaN).")
            return

        min_val = np.min(valid_data)
        max_val = np.max(valid_data)
        mean_val = np.mean(valid_data)
        std_val = np.std(valid_data)
        
        print(f"Min: {min_val:.4f}")
        print(f"Max: {max_val:.4f}")
        print(f"Mean: {mean_val:.4f}")
        print(f"Std Dev: {std_val:.4f}")
        
        # Check for anomalies
        if min_val == max_val:
            print("WARNING: Image is FLAT (all values are the same).")
        
        if max_val > 1.0:
            print("NOTE: Max value > 1.0. Is this probability (0-1) or something else?")
            
        if min_val < 0:
            print("NOTE: Negative values found.")

        # Histogram
        plt.figure(figsize=(10, 4))
        plt.hist(valid_data, bins=50, color='green', alpha=0.7)
        plt.title(f"Histogram: {os.path.basename(filepath)}")
        plt.xlabel("Pixel Value")
        plt.ylabel("Frequency")
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plot_filename = filepath.replace('.tif', '_hist.png')
        plt.savefig(plot_filename)
        print(f"Saved histogram to: {os.path.basename(plot_filename)}")
        plt.close()

    except Exception as e:
        print(f"ERROR analyzing file: {e}")

def main():
    folder = r"c:\Users\ADMIN\Desktop\Thesis\Thesis_SDM"
    files = [f for f in os.listdir(folder) if f.endswith('.tif')]
    
    if not files:
        print("No .tif files found.")
        return
        
    print(f"Found {len(files)} .tif files.")
    for f in files:
        analyze_tif(os.path.join(folder, f))

if __name__ == "__main__":
    main()
